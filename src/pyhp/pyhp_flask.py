"""
PyHP: Python Hypertext Preprocessor

This is a Flask app that can be used to run PyHP files.

Run the examples with `set FLASK_APP=pyhp_flask:create_app('./examples')` and
`flask run`.
"""

from typing import Optional
from pathlib import Path, PurePath

from flask import Flask, request, make_response, Response, redirect, \
    send_from_directory

try:
    from pyhp_interface import Pyhp
    from file_processing import SystemFileProcessor
    from cookies import NewCookie, DeleteCookie
except ImportError:
    from .pyhp_interface import Pyhp
    from .file_processing import SystemFileProcessor
    from .cookies import NewCookie, DeleteCookie


def create_app(base_dir: str) -> Flask:
    """Create a PyHP Flask app and return it."""
    base_dir = Path(base_dir).absolute()

    app = Flask(__name__)

    @app.route('/', defaults={'path': 'index'}, methods=['GET', 'POST'])
    @app.route('/<path:path>', methods=['GET', 'POST'])
    def catch_all(path: str) -> Response:
        if path.endswith('/'):
            return redirect('index')

        file_processor = SystemFileProcessor(base_dir)

        try:
            relative_path = file_processor.get_true_path(PurePath(path))
        except FileNotFoundError:
            if app.config['DEBUG']:
                return make_response(f'File not found: {path}', 404)
            return make_response('', 404)
        except IsADirectoryError:
            return redirect(f'{path}/')

        current_dir = relative_path.parent

        pyhp_class = Pyhp(current_dir, file_processor, app.config['DEBUG'],
                          dict(request.cookies), dict(request.args),
                          dict(request.form))

        return process_request(file_processor,
                               PurePath(relative_path.name),
                               pyhp_class)

    return app


def process_request(file_processor: SystemFileProcessor,
                    relative_path: PurePath, pyhp_class: Pyhp) -> Response:
    """Process a request."""

    if file_processor.is_pyhp_file(relative_path):
        page_text = pyhp_class.run(str(relative_path))
        status_code = 200  # TODO: Change, allow for custom status codes

        return redirect_or_create_response(
            page_text, status_code,
            pyhp_class.get_new_cookies(),
            pyhp_class.get_delete_cookies(),
            pyhp_class.get_redirect_information())
    return send_from_directory(
        file_processor.get_absolute_path(pyhp_class.current_dir),
        relative_path
    )


def redirect_or_create_response(page_text: str, status_code: int,
                                new_cookies: dict[str, NewCookie],
                                delete_cookies: dict[str, DeleteCookie],
                                redirect_information: Optional[
                                    tuple[str, int]]) -> Response:
    """Return a redirect response or create a new response."""
    if redirect_information is not None:
        url, status_code = redirect_information
        return redirect(url, status_code)

    return create_response(page_text, status_code, new_cookies, delete_cookies)


def create_response(page_text: str, status_code: int,
                    new_cookies: dict[str, NewCookie],
                    delete_cookies: dict[str, DeleteCookie]) -> Response:
    """Create a new response."""
    response = make_response(page_text, status_code)

    for cookie in new_cookies.values():
        response.set_cookie(**cookie.__dict__)

    for cookie in delete_cookies.values():
        response.delete_cookie(**cookie.__dict__)

    return response
