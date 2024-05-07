import pathlib
import ast
from PySongMan.lib.transformer import process_typeddict, process_types_source


def test_basic_idea():
    fixture = pathlib.Path(__file__).parent / "fixtures/simple_dict_type.py"

    code = ast.parse(fixture.read_text(), filename="fixture.py", mode="exec")
    for element in code.body:
        if isinstance(element, ast.ClassDef):
            break
    else:
        raise ValueError("Could not find class definition")

    actual = process_typeddict(element)

    assert len(actual.elements) == 3
    assert "name" in actual.elements
    assert actual.elements["name"] == "string"
    assert "age" in actual.elements
    assert actual.elements["age"] == "number"
    assert "active" in actual.elements
    assert actual.elements["active"] == "boolean"


def test_simple_file_comparison():
    fixture = pathlib.Path(__file__).parent / "fixtures/simple_dict_type.py"
    expected = pathlib.Path(__file__).parent / "fixtures/simple_dict_type.ts"
    actual = process_types_source(fixture)

    assert actual == expected.read_text()


def test_double_file_comparison():
    fixture = pathlib.Path(__file__).parent / "fixtures/double_dict_type.py"
    expected = pathlib.Path(__file__).parent / "fixtures/double_dict_type.ts"
    actual = process_types_source(fixture)

    assert actual == expected.read_text()


def test_interface_extended_by():
    fixture = pathlib.Path(__file__).parent / "fixtures/base_dict_type.py"
    expected = pathlib.Path(__file__).parent / "fixtures/base_dict_type.ts"
    actual = process_types_source(fixture)

    assert actual == expected.read_text()
