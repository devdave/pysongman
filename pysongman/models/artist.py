
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import Base
from . import get_db

class Artist(Base):

    name = Column(String, unique=True)
    albums = relationship("Album", back_populates="artist")


    @classmethod
    def GetCreate(cls, name):
        conn = get_db()
        record = cls.query.filter(cls.name == name).first()
        if record is None:
            record = cls(name = name)
            conn.s.add(record)

        return record