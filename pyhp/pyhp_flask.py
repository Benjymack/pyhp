import os

from flask import Flask, request

try:
    from pyhp import load_file, run_parsed_code, Pyhp
    from file_processing import get_directory, get_absolute_path
except ImportError:
    from .pyhp import load_file, run_parsed_code, Pyhp
    from .file_processing import get_directory, get_absolute_path


def create_app(base_dir: str) -> Flask:
    base_dir = os.path.abspath(base_dir)  # TODO: Move into separate function

    app = Flask(__name__)

    @app.route('/', defaults={'path': 'index'}, methods=['GET', 'POST'])
    @app.route('/<path:path>', methods=['GET', 'POST'])
    def catch_all(path) -> Response:
        pyhp_class = Pyhp(base_dir, app.config['DEBUG'],
                          dict(request.cookies),
                          dict(request.args),
                          dict(request.form))

        absolute_path = get_absolute_path(path, base_dir)

        return get_page_or_404(absolute_path, pyhp_class, app.config['DEBUG'])

    return app


def get_page_or_404(absolute_path: str, pyhp_class: Pyhp,
                    debug: bool) -> (str, int):
    try:
        dom = load_file(absolute_path)
        return run_parsed_code(dom, pyhp_class), 200
    except FileNotFoundError:
        print(os.getcwd())
        if debug:
            return f'File not found: {absolute_path}', 404
        else:
            return '', 404
