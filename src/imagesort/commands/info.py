import click
from ..exif import ExifTagsExtractor, UnsupportedImageFormat


@click.command(name="info")
@click.option("--debug", is_flag=True)
@click.argument("path", type=click.Path(
    exists=True, dir_okay=False, file_okay=True, allow_dash=False,
    path_type=str
))
def main(path, debug):
    try:
        _main(path, debug)
    except UnsupportedImageFormat as e:
        print(f"File {e.path} can't be load as image")


def _main(path, debug):
    exif = ExifTagsExtractor(path, verbose=debug)
    print(f"File {path}")
    print(f"  - Creation Date: {exif.get_creation_date()}")
