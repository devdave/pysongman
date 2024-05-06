"""
Tests for dictionary argument annotations

"""

import ast

from PySongMan.lib import transformer


def test_transformer_dict_type() -> None:
    """
    Correctly handle dictionary python to typescript types

    :return:
    """

    src2 = """
def action(self, val: int) -> dict[str, str]:
    return {"val": val}
"""

    parsed = ast.parse(src2, "test_data.py", mode="exec")
    element = parsed.body[0]
    if isinstance(element, ast.FunctionDef):
        function: ast.FunctionDef = element
        actual: transformer.FuncDef = transformer.process_function(function)

        assert len(actual.arg_names) == 1
        assert actual.arg_names[0] == "val"
        assert actual.compiled[0] == "val:number"
        assert actual.return_type == "{[key:string]: string}"
    else:
        raise AssertionError(f"parsed body 0 is not a function {parsed.body[0]:s}")
