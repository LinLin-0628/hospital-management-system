import os

import pytest


def pytest_collection_modifyitems(config, items):
    """
    Automatically mark all tests inside this app's tests folder as 'unit'.
    """

    # get absolute path to the app tests folder
    tests_dir = os.path.dirname(__file__)

    for item in items:
        # item.fspath is the path to the test file
        if str(item.fspath).startswith(tests_dir):
            item.add_marker(pytest.mark.unit)
