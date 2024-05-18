"""
    Application Types
"""

import typing

# import enum
# import typing as T
# from enum import Enum as pyEnum
# import datetime as DT

Identifier = str | int


class TagType(typing.TypedDict):
    id: Identifier
    name: str
    value: str


class SongType(typing.TypedDict):
    id: Identifier
    name: str
    artist: str
    size: int
    length_seconds: int
    tags: list[TagType]
