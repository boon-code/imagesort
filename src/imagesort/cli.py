import sys
import logging
import click
from .commands import sort, info

_LOG_FORMAT = "{name:<15} : {threadName:>15} : {levelname:>8} : {message}"
_DEFAULT_LOG_LEVEL = logging.INFO

def _init_logging(verbose):
    handler = logging.StreamHandler(sys.stderr)
    logging.basicConfig(format=_LOG_FORMAT,
                        style='{',
                        handlers=[handler],
                        level=logging.DEBUG)
    level = _DEFAULT_LOG_LEVEL
    if verbose:
        level = logging.DEBUG
    handler.setLevel(level)


@click.group()
@click.option('-v', '--verbose', is_flag=True)
def main(verbose):
    _init_logging(verbose)


main.add_command(sort.main)
main.add_command(info.main)
