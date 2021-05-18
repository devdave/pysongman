
from sqlalchemy import Column, String, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from .base import Base

class Album(Base):
    artist_id = Column(Integer, ForeignKey("Artist.id"))
    artist = relationship("Artist", back_populates="albums")

    name = Column(String(), index=True)

    __table_args = (Index("artist_album_ux", "artist_id", "name"))



    @classmethod
    def GetCreate(cls, artist, name, session):
        record = cls.query(cls.artist == artist, cls.name == name).first()
        if record is None:
            record = cls()
            record.artist = artist
            record.name = name

            with session.begin as trx:
                trx.add(record)
                trx.commit()

        return record