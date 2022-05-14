# Imports
from flask import Flask, request
from pyhp import load_file, run_parsed_code


if __name__ == '__main__':
    # Setup the flask application
    app = Flask(__name__)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        if path == '':
            path = 'index'

        try:
            parsed_code = load_file(path)
        except FileNotFoundError:
            return 'File not found', 404
        return run_parsed_code(parsed_code)

    app.run()
