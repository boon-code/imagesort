import re
import logging
import datetime
import exif
import plum
from PIL import Image, ExifTags, UnidentifiedImageError


_RE_EXIF_DATE = r'(\d+):(\d+):(\d+) (\d+):(\d+):(\d+)'
_RX_EXIF_DATE = re.compile(_RE_EXIF_DATE)


def _parse_date(date_str):
    m = _RX_EXIF_DATE.match(date_str)
    if m is None:
        return None
    return datetime.datetime(
            int(m.group(1)),
            int(m.group(2)),
            int(m.group(3)),
            int(m.group(4)),
            int(m.group(5)),
            int(m.group(6))
    )


class ExifTagsExtractor:
    _TAGS = ('datetime_original', 'datetime_digitized')

    def __init__(self, path, verbose=False):
        self._path = path
        self._verbose = verbose
        self._tags = dict()
        self._load()

    def _load(self):
        with open(self._path, 'rb') as f:
            image = self._open_image(f)
        if image.has_exif:
            self._tags = self._extract_tags(image)

    def _open_image(self, fobj):
        try:
            return exif.Image(fobj)
        except plum.UnpackError as e:
            logging.debug("Unsupprted image format %s: %s", self._path, e)
            raise UnsupportedImageFormat(self._path)

    def _extract_tags(self, image: exif.Image):
        assert image is not None, "Image must be set"
        assert image.has_exif, "Image must contain exif info"
        tags = dict()
        for name in filter(lambda x: x in self._TAGS, image.list_all()):
            val = getattr(image, name)
            if self._verbose:
                logging.debug("EXIF info: key=%s, value=%s", name, val)
            tags[name] = val
        logging.debug("Extracted exif tags for %s: %s", self._path, tags)
        return tags

    def _parse_date(self, date_str):
        dt = _parse_date(date_str)
        if dt is None:
            logging.debug("File %s: Creation date can't be parsed: %s'", self._path, date_str)
        return dt

    def get_creation_date(self):
        date_str = self._tags.get(
            'datetime_original',
            self._tags.get(
                'datetime_digitized',
                None
            )
        )
        if date_str is not None:
            obj = self._parse_date(date_str)
            assert obj.strftime("%Y:%m:%d %H:%M:%S") == date_str
            return obj
        else:
            logging.info("File %s has no useable date information", self._path)
            return None


class PilExifTagsExtractor:
    _CDATE = "DateTime"

    def __init__(self, path, verbose=False):
        self._path = path
        self._verbose = verbose
        self._tags = dict()
        self._load()

    def _open_image(self):
        try:
            return Image.open(self._path)
        except UnidentifiedImageError as e:
            logging.debug("Unsupprted image format %s: %s", self._path, e)
            raise UnsupportedImageFormat(self._path)

    def _load(self):
        img = self._open_image()
        exif = img.getexif()
        if exif is None:
            logging.debug("File %s has no exif data attached", self._path)
        else:
            logging.debug("File %s has exif data", self._path)
            self._extract_tags(exif)

    def _extract_tags(self, exif: Image.Exif):
        for k, v in exif.items():
            if k in ExifTags.TAGS:
                str_tag = ExifTags.TAGS[k]
                self._tags[str_tag] = v
            if self._verbose:
                logging.debug("EXIF info: keys=%s, values=%s", k, v)
        logging.debug("Found tags: %s", self._tags)

    def _parse_date(self, date_str):
        RX = r'(\d+):(\d+):(\d+) (\d+):(\d+):(\d+)'
        rx = re.compile(RX)
        m = rx.match(date_str)
        if m is None:
            logging.debug("File %s: Creation date can't be parsed: %s'", sel._path, date_str)
            return None
        return datetime.datetime(
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
                int(m.group(4)),
                int(m.group(5)),
                int(m.group(6))
        )

    def get_creation_date(self):
        if self._CDATE in self._tags:
            date_str = self._tags[self._CDATE]
            obj = self._parse_date(date_str)
            assert obj.strftime("%Y:%m:%d %H:%M:%S") == date_str
            return obj
        else:
            logging.debug("File %s has no exif data", self._path)
            return None


class UnsupportedImageFormat(Exception):

    def __init__(self, path):
        self.path = path
        Exception.__init__(self, f"File {path} has an unsupported image format")
