
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class Artist(Base):

    name = Column(String)
    albums = relationship("ArtistAlbum", back_populates="artists")