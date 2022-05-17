# Imports
from flask import Flask, request
from pyhp import load_file, run_parsed_code
from argparse import ArgumentParser
import os


def setup_file_action(subparser):
    file = subparser.add_parser('file', help='Run a file')

    file.add_argument('file', help='File to run')


def setup_server_action(subparser):
    server = subparser.add_parser('server', help='Start a server')

    server.add_argument('directory', help='Directory to serve')
    server.add_argument('-p', '--port', help='Port to serve on', type=int,
                        default=5000)


def setup_argument_parsing() -> ArgumentParser:
    parser = ArgumentParser(description='Python Hypertext Preprocessor (PyHP)')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode',
                        default=False)

    subparser = parser.add_subparsers(dest='action', help='Action to perform',
                                      required=True)
    setup_file_action(subparser)
    setup_server_action(subparser)

    return parser


def run_file():
    parsed_code = load_file(args.file)
    output = run_parsed_code(parsed_code, debug=args.debug)
    print(output)


def get_page_or_404(path: str, predefined: dict, debug: bool) -> (str, int):
    try:
        dom = load_file(path)
        return run_parsed_code(dom, predefined, debug)
    except FileNotFoundError:
        return "File not found", 404


def run_server():
    app = Flask(__name__)

    @app.route('/', defaults={'path': 'index'})
    @app.route('/<path:path>')
    def catch_all(path):
        predefined = {
            '_COOKIE': request.cookies,
            '_GET': request.args,
            '_POST': request.form,
        }

        path = os.path.join(args.directory, path)

        return get_page_or_404(path, predefined, args.debug)

    app.run(port=args.port, debug=args.debug)


if __name__ == '__main__':
    parser = setup_argument_parsing()

    args = parser.parse_args()

    if args.action == 'file':
        run_file()
    elif args.action == 'server':
        run_server()
