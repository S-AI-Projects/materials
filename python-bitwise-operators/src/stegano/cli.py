"""
Command line arguments parsing.
"""

import argparse
import pathlib
from dataclasses import dataclass
from typing import Callable, Optional, Sequence


@dataclass
class CommandLineArguments:
    """Parsed command line arguments.

    Preconditions and Interface:
    - Line 12: CommandLineArguments dataclass definition.
    - Fields:
        bitmap: pathlib.Path
        encode: Optional[pathlib.Path]
        decode: bool
        erase: bool
    External dependencies:
    - Filesystem check via pathlib.Path.exists() and is_file() during argument parsing.
    - CLI argv reading via sys.argv when args is None.
    - Smallest valid input fixture: Decode flag with a single valid bitmap path.
        Literal inputs: ['image.bmp', '--decode']
        Expected: CommandLineArguments(bitmap=Path('image.bmp'), encode=None, decode=True, erase=False)
    - Ordinary input fixture: Encode flag with bitmap and secret payload file.
        Literal inputs: ['carrier.bmp', '--encode', 'secret.txt']
        Expected: CommandLineArguments(bitmap=Path('carrier.bmp'), encode=Path('secret.txt'), decode=False, erase=False)
    """

    bitmap: pathlib.Path
    encode: Optional[pathlib.Path]
    decode: bool
    erase: bool


def parse_args(
    args: Optional[Sequence[str]] = None,
    path_validator: Optional[Callable[[str], pathlib.Path]] = None,
) -> CommandLineArguments:
    """Parse command line arguments.

    Parameters:
      args: Command line arguments list to parse (defaults to None, reading sys.argv).
      path_validator: Factory function converting path strings and checking existence (defaults to path_factory).
    """
    factory = path_validator if path_validator is not None else path_factory

    parser = argparse.ArgumentParser()
    parser.add_argument("bitmap", type=factory)

    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--encode", "-e", metavar="file", type=factory)
    modes.add_argument("--decode", "-d", action="store_true")
    modes.add_argument("--erase", "-x", action="store_true")

    parsed = parser.parse_args(args)

    if not any([parsed.encode, parsed.decode, parsed.erase]):
        parser.error("Mode required: --encode file | --decode | --erase")

    return CommandLineArguments(**vars(parsed))


def path_factory(argument: str) -> pathlib.Path:
    """Convert the argument to a path instance."""

    path = pathlib.Path(argument)

    if not path.exists():
        raise argparse.ArgumentTypeError("file doesn't exist")

    if not path.is_file():
        raise argparse.ArgumentTypeError("must be a file")

    return path
