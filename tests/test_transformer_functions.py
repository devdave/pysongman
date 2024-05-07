import ast
from PySongMan.lib.transformer import process_function


def test_basic():
    fixture = "def foo():\n    pass"

    mod = ast.parse(fixture, mode="exec")
    func = mod.body[0]

    actual = process_function(func)

    assert len(actual.arg_names) == 0


def test_str_arg():
    fixture = "def foo(name:str):\n    pass"

    mod = ast.parse(fixture, mode="exec")
    func = mod.body[0]

    actual = process_function(func)

    assert len(actual.arg_names) == 1
    assert actual.arg_names[0] == "name"
    assert actual.compiled[0] == "name:string"


def test_list_arg():
    fixture = "def foo(names:list[str]):\n    pass"

    mod = ast.parse(fixture, mode="exec")
    func = mod.body[0]

    actual = process_function(func)

    assert len(actual.arg_names) == 1
    assert actual.arg_names[0] == "names"
    assert actual.compiled[0] == "names:string[]"
