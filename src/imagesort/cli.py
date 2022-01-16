import sys
import logging
import click
from .commands import sort, info

_LOG_FORMAT = "{name:<15} : {threadName:>15} : {levelname:>8} : {message}"
_DEFAULT_LOG_LEVEL = logging.INFO

def _init_logging(verbose, quiet):
    handler = logging.StreamHandler(sys.stderr)
    logging.basicConfig(format=_LOG_FORMAT,
                        style='{',
                        handlers=[handler],
                        level=logging.DEBUG)
    level = _DEFAULT_LOG_LEVEL
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.WARNING
    handler.setLevel(level)


@click.group()
@click.option('-v', '--verbose', is_flag=True)
@click.option('-q', '--quiet', is_flag=True)
def main(verbose, quiet):
    _init_logging(verbose, quiet)


main.add_command(sort.main)
main.add_command(info.main)
