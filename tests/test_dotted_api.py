"""
Tests for handling api.{child class}.{method} subclassed API
"""

import pathlib
import ast

from PySongMan.lib import transformer


def test_dotted_api_basic():
    """
    Basic test for processing a child class

    :return:
    """

    fixture = "class Logger:\n" "    def info(self):\n" "        pass\n" "\n"

    code = ast.parse(fixture, filename="__fixture__", mode="exec")
    mod = code.body
    element = mod[0]
    if isinstance(element, ast.ClassDef):
        logger_cls: ast.ClassDef = element
    else:
        raise ValueError(f"Bad fixture, got {element}")

    actual_name, actual_methods = transformer.process_child_class(logger_cls)

    assert actual_name == "Logger"
    assert len(actual_methods) == 1
    assert list(actual_methods.keys())[0] == "info"


def test_generates_api():
    """
    Comprehensive test that transformer can build out a dotted/child class design to
    make things a little easier to read and manage.

    :return:
    """

    fixture_path = (
        pathlib.Path(__file__).parent / "fixtures/plain_api_logger_child_base_func.py"
    )
    expected = (
        pathlib.Path(__file__).parent / "fixtures/plain_api_logger_child_base_func.ts"
    ).read_text()

    actual = transformer.process_source(fixture_path)

    assert actual == expected
