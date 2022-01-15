import logging

import click
from ..interactive import ask_ok_cancel
from ..util import UserAborted
from ..sorter import ImageSorter


@click.command(name="sort")
@click.option('--dryrun/--no-dryrun', default=True)
@click.option('--move/--copy', default=False)
@click.option("-t", "--target", type=click.Path(
    exists=True, dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False,
    path_type=str
))
@click.option('-l', '--follow-links', is_flag=True)
@click.argument("directory", type=click.Path(
    exists=True, dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False,
    path_type=str
))
def main(directory, target, dryrun, move, follow_links):
    try:
        _main(directory, target, dryrun, move, follow_links)
    except UserAborted:
        logging.warning("Aborted by user")


def _main(directory, target, dryrun, move, follow_links):
    logging.info("Image sort: dir=%s, target=%s, dry-run=%s, move-mode=%s",
                 directory, target, dryrun, move)
    if target is None:
        target = directory  # in-place sort
    mode = "move" if move else "copy"
    if not dryrun:
        ask_ok_cancel(
            f"Sorting {directory}",
            f"Please confirm: Sorting images in {directory} to {target} using {mode} mode")
    sorter = ImageSorter(directory, target, move=move, dryrun=dryrun, follow_links=follow_links)
    num = sorter.count()
    print(f"Number of files: {num}")
