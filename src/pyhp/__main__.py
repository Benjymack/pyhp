"""
PyHP: Python Hypertext Preprocessor
"""

from argparse import ArgumentParser
from pathlib import PurePath, Path

try:
    from pyhp_interface import Pyhp
    from file_processing import SystemFileProcessor
    from pyhp_flask import create_app
except ImportError:
    from .pyhp_interface import Pyhp
    from .file_processing import SystemFileProcessor
    from .pyhp_flask import create_app


if __name__ == '__main__':
    parser = ArgumentParser(description='Python Hypertext Preprocessor (PyHP)')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode',
                        default=False)

    action_parser = parser.add_subparsers(dest='action',
                                          help='Action to perform',
                                          required=True)
    file_parser = action_parser.add_parser('file', help='Run a file')
    file_parser.add_argument('file', help='File to run')

    server_parser = action_parser.add_parser('server', help='Run a server')
    server_parser.add_argument('directory', help='Directory to serve')
    server_parser.add_argument('--port', help='Port to serve on', type=int,
                               default=5000)

    args = parser.parse_args()

    if args.action == 'file':
        base_dir = Path(args.file).parent.absolute()
        root_pyhp = Pyhp(PurePath(), SystemFileProcessor(base_dir),
                         args.debug)
        print(root_pyhp.run(PurePath(args.file).name))
    elif args.action == 'server':
        app = create_app(args.directory)
        app.run(port=args.port, debug=args.debug)
    else:
        parser.print_help()
