import ast
from PySongMan.lib.transformer import process_function


def get_statememt(str_st) -> ast.FunctionDef:
    mod = ast.parse(str_st)
    return mod.body[0]


def cycle_st(str_str):
    return process_function(get_statememt(str_str))
