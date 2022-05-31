"""
Tests PyHP when connected to a flask server.

TestFileSecurity:
    Tests that the file security is correctly enforced.
"""

# pylint: disable=missing-function-docstring

from unittest import TestCase


class TestFileSecurity(TestCase):
    """Tests that the file security is correctly enforced."""
    def test_disallow_parent_directory_access(self):
        pass  # TODO: Finish

    def test_disallow_absolute_path_access(self):
        pass  # TODO: Finish
