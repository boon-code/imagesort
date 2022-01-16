import logging
import os
import shutil
from .exif import ExifTagsExtractor, UnsupportedImageFormat


class Action:
    SKIP = 'skip'
    OK = 'ok'
    ERROR = 'error'

    def __init__(self, action, path, moved=False, exception=None, desc=None):
        self.action = action
        self.path = path
        self.moved = moved
        self.exception = exception
        self.desc = desc
        self._optimize_desc()

    def _optimize_desc(self):
        if (self.exception is not None) and (self.desc is None):
            self.desc = f"{self.exception}"

    def is_error(self):
        return self.action == self.ERROR

    def is_skipped(self):
        return self.action == self.SKIP

    def is_ok(self):
        return self.action == self.OK


class ImageSorter:
    DST_PRESERVE = 'PRESERVE'
    DST_REVERSE = 'REVERSE'
    DST_REMOVE = 'REMOVE'
    DST_OPTIONS = (DST_PRESERVE, DST_REVERSE, DST_REMOVE)

    def __init__(self, src, dst, move=False, dryrun=True, follow_links=False, dir_method=None,
                 ignore_exceptions=False, create_dst=False):
        self._log = logging.getLogger("ImageSorter")
        self._dryrun = dryrun
        self._src = src
        self._dst = dst
        self._follow_links = follow_links
        self._dir_method = dir_method if dir_method in self.DST_OPTIONS else self.DST_REVERSE
        self._move = move
        self._re_raise_exceptions = not ignore_exceptions
        self._create_dst = create_dst
        self._set_filter()
        self._log.info("Source folder: %s, destination folder: %s", self._src, self._dst)
        self._log.info("Options: dry run: %s, move files: %s follow links: %s, directory creation method: %s",
                       self._dryrun, self._move, self._follow_links, self._dir_method)

    def sort(self):
        self._check_target_directory()
        for root, file in self._walk_files(skip_cb=self._warn_skipped_files):
            src = os.path.join(self._src, root, file)
            try:
                root_dst = self._get_dst_root(src, root)
                if root_dst is None:
                    self._log.warning("Skipping file %s: Couldn't determine destination directory", src)
                    yield Action(Action.SKIP, src)
                else:
                    self._create_dst_dir(root_dst)
                    self._log.debug("Destination for %s: %s", src, root_dst)
                    yield self._run_file_action(root, file, root_dst)
            except Exception as e:
                yield Action(Action.ERROR, src, exception=e)
                if self._re_raise_exceptions:
                    raise

    def _get_dst_root(self, src, root):
        dt = self._get_exif_creation_date(src)
        if dt is None:
            return None
        year = dt.strftime("%Y")
        month = dt.strftime("%m_%B")
        if self._dir_method == self.DST_PRESERVE:
            return os.path.join(root, year, month)
        elif self._dir_method == self.DST_REVERSE:
            return os.path.join(year, month, root)
        elif self._dir_method == self.DST_REMOVE:
            return os.path.join(year, month)
        else:
            raise AssertionError(
                f"Invalid directory name generation method {self._dir_method}, must be one of {self.DST_OPTIONS}"
            )

    def _get_exif_creation_date(self, path):
        ret = None
        try:
            dt = ExifTagsExtractor(path).get_creation_date()
            ret = dt
        except UnsupportedImageFormat as e:
            self._log.warning("Unsupported image format of file: %s: %s", path, e)
        return ret

    def _run_file_action(self, root, file, dst_root):
        src = os.path.join(self._src, root, file)
        dst = os.path.join(self._dst, dst_root, file)
        if src == dst:
            self._log.warning("Would override same file '%s' -> abort", dst)
            return Action(Action.SKIP, src, desc="Source and destination are the same")
        if os.path.exists(dst):
            self._log.warning("Destination file %s already exists -> skipping", dst)
            return Action(Action.SKIP, src, desc="Would override source file")
        if self._dryrun:
            method = "move" if self._move else "copy"
            self._log.info("dryrun: Would %s %s -> %s", method, src, dst)
        else:
            if self._move:
                raise NotImplementedError()
            else:
                shutil.copyfile(src, dst, follow_symlinks=True)
        return Action(Action.OK, src, moved=self._move)

    def _create_dst_dir(self, rel_path):
        path = os.path.join(self._dst, rel_path)
        try:
            self._create_directory(path)
            return True
        except OSError as e:
            self._log.exception("Failed to create directory '%s': %s", path, e)
            return False

    def _check_target_directory(self):
        if self._create_dst:
            self._create_directory(self._dst)
        else:
            if not os.path.exists(self._dst):
                raise RuntimeError("Target folder '%s' doesn't exist", self._dst)
            elif not os.path.isdir(self._dst):
                raise RuntimeError("Target path '%s' is not a folder", self._dst)

    def _create_directory(self, path):
        if self._dryrun:
            self._log.info("dryrun: Would create directory: %s", path)
        else:
            os.makedirs(path, exist_ok=True)

    def count(self):
        count = 0
        for root, files in self._walk_files_list(skip_cb=self._warn_skipped_files):
            count += len(list(filter(self._filter, files)))
        return count

    def _walk_files(self, skip_cb=None, check_dir_cb=None):
        _, skip_cb = self._test_callback(skip_cb, '_walk_files skip_cb')
        use_dir_check, check_dir_cb = self._test_callback(check_dir_cb, '_walk_files check_dir_cb')
        for root, files in self._walk_files_list(skip_cb=skip_cb):
            dir_ok = True
            if use_dir_check:
                dir_ok = check_dir_cb(root)
            if dir_ok:
                for i in files:
                    yield root, i
            else:
                self._log.warning("Skipping directory %s", root)

    def _walk_files_list(self, skip_cb=None):
        call_skip_cb, _ = self._test_callback(skip_cb, "_walk_files_list")
        for root, dirs, files in os.walk(self._src, followlinks=self._follow_links):
            if root.startswith(self._src):
                root = os.path.relpath(root, self._src)
                yield root, files
            else:
                if call_skip_cb:
                    skip_cb(root)

    def _test_callback(self, cb, site):
        use_callback = False
        if cb is not None:
            if callable(cb):
                use_callback = True
            else:
                self._log.error("%s: Callback parameter isn't callable -> skip: %s", site, cb)
        if not use_callback:
            cb = None
        return use_callback, cb

    def _warn_skipped_files(self, path):
        self._log.warning("Path '%s' didn't start with '%s' -> Skipping", path, self._src)

    def _set_filter(self):
        self._filter = lambda x: x
