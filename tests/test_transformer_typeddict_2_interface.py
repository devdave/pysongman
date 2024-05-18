import typing as t
import ast
from PySongMan.lib.transformer import process_types_source


# def test_proof_of_concept() -> None:
#     class Thing(t.TypedDict):
#         a: int
#         b: str


BASIC = """
import typing as t

class Thing(t.TypedDict):
    a: int
    b: str
    c: bool
"""

BASIC_EXPECTED = """export interface Thing {

    a: number
    b: string
    c: boolean
}
"""

LIST = """
import typing as t

class Thing(t.TypedDict):
    a: int

class Adams(t.TypedDict):
    hands: list[Thing]

"""

LIST_EXPECTED = """export interface Thing {

    a: number
}
export interface Adams {

    hands: Thing[]
}
"""


def test_basic_test():

    actual = process_types_source(BASIC, None)

    assert actual == BASIC_EXPECTED


def test_child_list():

    actual = process_types_source(LIST, None)

    assert actual == LIST_EXPECTED
