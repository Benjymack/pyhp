import os

from flask import Flask, request

try:
    from pyhp import load_file, run_parsed_code, Pyhp
    from file_processing import get_directory, get_absolute_path
except ImportError:
    from .pyhp import load_file, run_parsed_code, Pyhp
    from .file_processing import get_directory, get_absolute_path


def create_app(directory: str) -> Flask:
    directory = os.path.abspath(directory)  # TODO: Move into separate function

    app = Flask(__name__)

    @app.route('/', defaults={'path': 'index'})
    @app.route('/<path:path>')
    def catch_all(path):
        pyhp_class = Pyhp(directory, app.config['DEBUG'],
                          dict(request.cookies),
                          dict(request.args),
                          dict(request.form))

        absolute_path = get_absolute_path(path, directory)

        return get_page_or_404(absolute_path, pyhp_class, app.config['DEBUG'])

    return app


def get_page_or_404(absolute_path: str, pyhp_class: Pyhp,
                    debug: bool) -> (str, int):
    try:
        dom = load_file(absolute_path)
        return run_parsed_code(dom, pyhp_class)
    except FileNotFoundError:
        print(os.getcwd())
        if debug:
            return f'File not found: {absolute_path}', 404
        else:
            return '', 404
