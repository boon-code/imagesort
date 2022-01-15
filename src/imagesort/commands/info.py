import click
from ..exif import ExifTagsExtractor
from ..util import UnsupportedImageFormat


@click.command(name="info")
@click.argument("path", type=click.Path(
    exists=True, dir_okay=False, file_okay=True, allow_dash=False,
    path_type=str
))
def main(path):
    try:
        _main(path)
    except UnsupportedImageFormat as e:
        print(f"File {e.path} can't be load as image")


def _main(path):
    exif = ExifTagsExtractor(path)
    print(f"File {path}")
    print(f"  - Creation Date: {exif.get_creation_date()}")
