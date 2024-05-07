import typing as T

class Person(T.TypedDict):
    name: str
    age: int
    active: bool


class Location(T.TypedDict):
    name: str
    state: str
    latitude: float
    longitude: float

