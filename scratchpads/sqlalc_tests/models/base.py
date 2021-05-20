
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import query, Query
from sqlalchemy import Column, Integer


@as_declarative()
class Base:

    id = Column(Integer, primary_key=True)
    query: Query

    @declared_attr
    def __tablename__(self):
        return self.__name__