import logging
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

    def get_creation_date(self):
        if self._CDATE in self._tags:
            return self._tags[self._CDATE]
        else:
            logging.debug("File %s has no exif data", self._path)
            return None
