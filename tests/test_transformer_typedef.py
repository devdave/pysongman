import ast


def test_basic_idea():

    fixture = """Identifier = str | int"""
    expected = """export typedef Identifier = string | number"""

    mod = ast.parse(fixture, filename="__module__.py", mode="exec")
    type_st = mod.body[0]

    assert isinstance(type_st, ast.Assign)
    assert len(type_st.targets) == 1

    target = type_st.targets[0]
    assert isinstance(target, ast.Name)
    assert target.id == "Identifier"
    assert isinstance(type_st.value, ast.BinOp)
    binop = type_st.value
    assert isinstance(binop.left, ast.Name)
    assert isinstance(binop.right, ast.Name)
    assert binop.right.id == "int"
    assert binop.left.id == "str"

    debug = 1
