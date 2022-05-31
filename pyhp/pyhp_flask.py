"""
PyHP: Python Hypertext Preprocessor

This is a Flask app that can be used to run PyHP files.

Run the examples with `set FLASK_APP=pyhp_flask:create_app('./examples')` and
`flask run`.
"""

import os

from typing import Optional
from flask import Flask, request, make_response, Response, redirect

try:
    from pyhp import load_file, run_parsed_code, PyhpProtocol, Pyhp
    from file_processing import get_absolute_path
    from cookies import NewCookie, DeleteCookie
except ImportError:
    from .pyhp import load_file, run_parsed_code, PyhpProtocol, Pyhp
    from .file_processing import get_absolute_path
    from .cookies import NewCookie, DeleteCookie


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

        page_text, status_code = get_page_or_404(absolute_path, pyhp_class,
                                                 app.config['DEBUG'])

        return redirect_or_create_response(
            page_text, status_code,
            pyhp_class.get_new_cookies(),
            pyhp_class.get_delete_cookies(),
            pyhp_class.get_redirect_information())

    return app


def get_page_or_404(absolute_path: str, pyhp_class: PyhpProtocol,
                    debug: bool) -> (str, int):
    try:
        dom = load_file(absolute_path)
        return run_parsed_code(dom, pyhp_class), 200
    except FileNotFoundError:
        print(os.getcwd())
        if debug:
            return f'File not found: {absolute_path}', 404
        return '', 404


def redirect_or_create_response(page_text: str, status_code: int,
                                new_cookies: dict[str, NewCookie],
                                delete_cookies: dict[str, DeleteCookie],
                                redirect_information: Optional[
                                    tuple[str, int]]) -> Response:
    if redirect_information is not None:
        url, status_code = redirect_information
        return redirect(url, status_code)

    return create_response(page_text, status_code, new_cookies, delete_cookies)


def create_response(page_text: str, status_code: int,
                    new_cookies: dict[str, NewCookie],
                    delete_cookies: dict[str, DeleteCookie]) -> Response:
    response = make_response(page_text, status_code)

    for cookie in new_cookies.values():
        response.set_cookie(**cookie.__dict__)

    for cookie in delete_cookies.values():
        response.delete_cookie(**cookie.__dict__)

    return response
