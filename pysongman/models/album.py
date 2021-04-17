
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base

class Album(Base):
    artist_id = Column(Integer, ForeignKey("Artist.id"))
    artists = relationship("Artist", back_populates="albums")

    name = Column(String())
