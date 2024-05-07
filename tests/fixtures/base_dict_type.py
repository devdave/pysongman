import typing as T
import datetime

class Base(T.TypedDict):
    created_on: datetime.datetime
    updated_on: datetime.datetime


class Person(Base):
    name: str
    age: int
