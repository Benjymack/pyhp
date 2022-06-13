# PyHP (Python Hypertext Preprocessor)

PyHP is a Python script that can be used to write Python code in HTML, then execute it and render it to a page.

## Getting Started
### Installation
To use this project, clone the repository and install the dependencies.

```commandline
git clone https://github.com/Benjymack/pyhp.git
cd pyhp
pip install -r requirements.txt
```

### Running the example Flask server
To run the examples, use the following commands:

```commandline
set FLASK_APP=phyp:pyhp_flask:create_app('./examples')
set FLASK_ENV=development
set FLASK_DEBUG=1
flask run
```

### Running individual files
To run an individual example file, use the following command:

```commandline
python pyhp/pyhp.py ./examples/index.pyhp
```
