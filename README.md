# PyHP (Python Hypertext Preprocessor)

PyHP is a Python script that can be used to write Python code in HTML, then execute it and render it to a page.

## Getting Started
### Installation
To use this project, install it using pip:

```commandline
pip install python-hypertext-preprocessor
```

Alternatively, clone the repository and install the dependencies:

```commandline
git clone https://github.com/Benjymack/pyhp.git
cd pyhp
pip install -r requirements.txt
```

### Running the example Flask server
To run a simple Flask server with the pip installed version, use the following command:

```commandline
python -m pyhp server path/to/directory
```

If you cloned from GitHub:

```commandline
python -m src.pyhp server examples
```

In both cases, the server will be available at http://localhost:5000/

### Running individual files
To run an individual example file, use the following command:

```commandline
python -m pyhp file path/to/file.pyhp
```
