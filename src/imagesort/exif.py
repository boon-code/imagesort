import re
import logging
import datetime
from PIL import Image, ExifTags, UnidentifiedImageError
from .util import UnsupportedImageFormat


class ExifTagsExtractor:
    _CDATE = "DateTime"

    def __init__(self, path):
        self._path = path
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
