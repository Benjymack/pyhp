# Imports
from flask import Flask, request
from pyhp import load_file, run_parsed_code


# Constants
DEBUG = True


if __name__ == '__main__':
    # Setup the flask application
    app = Flask(__name__)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        if path == '':
            path = 'index'

        # Get information for initial_globals variables
        predefined = {
            '_COOKIE': request.cookies,
            '_GET': request.args,
            '_POST': request.form,
        }

        try:
            parsed_code = load_file(path)
        except FileNotFoundError:
            return 'File not found', 404
        return run_parsed_code(parsed_code, predefined, DEBUG)

    app.run()
