"""
PyHP: Python Hypertext Preprocessor
"""

from argparse import ArgumentParser
from pathlib import PurePath, Path

try:
    from pyhp.pyhp_interface import Pyhp
    from pyhp.file_processing import SystemFileProcessor
except ImportError:
    from .pyhp_interface import Pyhp
    from pyhp.file_processing import SystemFileProcessor


if __name__ == '__main__':
    parser = ArgumentParser(description='Python Hypertext Preprocessor (PyHP)')
    parser.add_argument('file', help='File to run')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode',
                        default=False)

    args = parser.parse_args()

    base_dir = PurePath(args.file).parent
    pyhp_class = Pyhp(base_dir, SystemFileProcessor(Path(base_dir)), args.debug)

    print(pyhp_class.include(args.file))
