import ast
from PySongMan.lib.transformer import process_function


def get_statememt(str_st) -> ast.FunctionDef:
    mod = ast.parse(str_st)
    return mod.body[0]


def cycle_st(str_str):
    return process_function(get_statememt(str_str))


def test_basic():

    actual = cycle_st("def foo():\n    pass")

    assert len(actual.arg_names) == 0


def test_str_arg():

    actual = cycle_st("def foo(name:str):\n    pass")

    assert len(actual.arg_names) == 1
    assert actual.arg_names[0] == "name"
    assert actual.compiled[0] == "name:string"


def test_list_arg():

    actual = cycle_st("def foo(names:list[str]):\n    pass")

    assert len(actual.arg_names) == 1
    assert actual.arg_names[0] == "names"
    assert actual.compiled[0] == "names:string[]"


def test_dict_arg():

    actual = cycle_st("def foo(names:dict[str, str]):\n    pass")

    assert len(actual.arg_names) == 1
    assert actual.arg_names[0] == "names"
    assert actual.compiled[0] == "names:{[key:string]: string}"


def test_optional_none_arg():

    actual = cycle_st("def foo(name:str|None):\n    pass")

    assert len(actual.arg_names) == 1
    assert actual.arg_names[0] == "name"
    assert actual.compiled[0] == "name:string | undefined"


def test_optional_mixed_type_arg():
    actual = cycle_st("def foo(name:int|str):\n    pass")
    assert len(actual.arg_names) == 1
    assert actual.arg_names[0] == "name"
    assert actual.compiled[0] == "name:number | string"
