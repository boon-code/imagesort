import locale
import logging
import os

import click
from prompt_toolkit.shortcuts import ProgressBar

from ..interactive import ask_ok_cancel
from ..util import UserAborted
from ..sorter import ImageSorter


@click.command(name="sort")
@click.option('--dryrun/--no-dryrun', default=True)
@click.option('--move/--copy', default=False)
@click.option("-t", "--target", type=click.Path(
    file_okay=False, resolve_path=True, allow_dash=False,
    path_type=str
))
@click.option('-l', '--follow-links', is_flag=True)
@click.option('-d', '--dir-creation-method',
    type=click.Choice(ImageSorter.DST_OPTIONS, case_sensitive=False),
    help="""
Defines the method that is used to create the folder structure.
""".strip()
)
@click.option('-a', '--create-destination', is_flag=True)
@click.option('-L', '--use-locale', help="Set locale you want to use (f.e. en_US.utf8, de_AT.utf8, ...)")
@click.argument("directory", type=click.Path(
    exists=True, dir_okay=True, file_okay=False, resolve_path=True, allow_dash=False,
    path_type=str
))
def main(directory, target, dryrun, move, follow_links, dir_creation_method, use_locale, create_destination):
    _handle_locale(use_locale)
    try:
        _main(directory, target, dryrun, move, follow_links, dir_creation_method, create_destination)
    except UserAborted:
        logging.warning("Aborted by user")


def _handle_locale(arg_locale=None):
    env_locale = os.environ.get('LC_TIME')
    if arg_locale:
        locale.setlocale(locale.LC_TIME, arg_locale)
    elif env_locale is not None:
        locale.setlocale(locale.LC_TIME, env_locale)


def _main(directory, target, dryrun, move, follow_links, dir_creation_method, create_destination):
    logging.info("Image sort: dir=%s, target=%s, dry-run=%s, move-mode=%s",
                 directory, target, dryrun, move)
    if target is None:
        target = directory  # in-place sort
    mode = "move" if move else "copy"
    if not dryrun:
        ask_ok_cancel(
            f"Sorting {directory}",
            f"Please confirm: Sorting images in {directory} to {target} using {mode} mode")
    sorter = ImageSorter(directory,
                         target,
                         move=move,
                         dryrun=dryrun,
                         follow_links=follow_links,
                         dir_method=dir_creation_method,
                         create_dst=create_destination
    )
    number_of_files = sorter.count()
    print(f"Number of files: {number_of_files}")
    skipped = []
    failed = []
    with ProgressBar() as pb:
        for action in pb(sorter.sort(), total=number_of_files):
            if action.is_error():
                failed.append(action.path)
            elif action.is_skipped():
                skipped.append(action.path)
    print("")
    _print_list_if_not_empty(skipped, "Skipped files: ")
    _print_list_if_not_empty(failed, "Failed files: ")


def _print_list_if_not_empty(l, title):
    if l:
        print(title)
        for i in l:
            print(f"  {i}")
