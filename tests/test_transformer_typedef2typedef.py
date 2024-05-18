from PySongMan.lib import transformer


BASIC = "Identifier = str | int"
BASIC_EXPECTED = "export typedef Identifier = string | number\n"


def test_basic_transform():

    actual = transformer.process_types_source(BASIC)

    assert actual == BASIC_EXPECTED
