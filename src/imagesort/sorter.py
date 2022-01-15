import os


class ImageSorter:

    def __init__(self, src, dst, move=False, dryrun=True, follow_links=False):
        self._dryrun = dryrun
        self._move = move
        self._src = src
        self._dst = dst
        self._follow_links = follow_links
        self._filter = lambda x: x

    def sort(self):
        pass  # Sort all files

    def count(self):
        count = 0
        for root, dirs, files in os.walk(self._src, followlinks=self._follow_links):
            count += len(list(filter(self._filter, files)))
        return count

    def _walk(self):
        start_len = len(self._src)
        for root, dirs, files in os.walk(self._src, followlinks=self._follow_links):
            if root.startswith(self._src):
                root = root[start_len:]
            print(f"{root} | {dirs} | {files}")

