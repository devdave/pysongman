
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import Base

class Artist(Base):

    name = Column(String)
    albums = relationship("Album", back_populates="artists")