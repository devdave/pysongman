from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Float, Time, TIMESTAMP
from sqlalchemy import func, UniqueConstraint, Table, extract
from sqlalchemy.orm import relationship, scoped_session, sessionmaker, session
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.types import Enum
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.query import Query
from sqlalchemy import create_engine

from collections import namedtuple

SAConn = namedtuple("SAConn", "engine,maker")

SA_ENGINE = None
SA_MAKER = None


def initialize_db(sqlite_path: str = None):
    global SA_ENGINE, SA_MAKER

    if sqlite_path is None:
        if SA_ENGINE is not None and SA_MAKER is not None:
            return SAConn(SA_ENGINE, SA_MAKER)

    if sqlite_path.startswith("sqlite:") is False:
        # default to relative
        sqlite_path = f"sqlite:///{sqlite_path}"

    engine = create_engine(sqlite_path)
    maker = sessionmaker(bind=engine)
    scoped = scoped_session(maker)

    Base.metadata.bind = engine
    Base.query = scoped.query_property()

    SA_ENGINE = engine
    SA_MAKER = scoped
    return SAConn(engine, scoped)

def kill_db(bound:SAConn):
    SAConn.engine.dispose()
    SAConn.maker.close()
    Base.query = None
    Base.metadata.bind = None


@as_declarative()
class Base(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__

    id = Column(Integer, primary_key=True)

    query:Query = None

class Artist(Base):

    name = Column(String)
    albums = relationship("ArtistAlbum", back_populates="artists")



class ArtistAlbum(Base):

    artist_id = Column(Integer, ForeignKey("Artist.id"))
    artists = relationship("Artist", back_populates="albums")

    name = Column(String())

class ParentDir(Base):

    path = Column(String)

    children = relationship("Song")


class Song(Base):

    title = Column(String())
    track = Column(String())

    artist_id = Column(Integer(), ForeignKey("Artist.id"))
    artist = relationship("Artist", backref="songs")

    album_id = Column(Integer(), ForeignKey("ArtistAlbum.id"))
    album = relationship("ArtistAlbum", backref="songs")

    filesize = Column(Float)

    @hybrid_property
    def filesize_kb(self):
        return self.filesize / 1024 if self.filesize is not None else 0

    @hybrid_property
    def filesize_mb(self):
        return self.filesize_kb / 1024

    duration = Column(Float)

    @hybrid_property
    def duration_minutes(self):
        return self.duration / 60 if self.duration is not None else 0

    @hybrid_property
    def duration_str(self):
        if self.duration is None:
            return "UNKNOWN"

        minutes = int(self.duration / 60)
        seconds = int(((self.duration / 60) - minutes) * 60)

        return f"{minutes}:{seconds:02}"


    filename = Column(String)
    rel_path = Column(String)
    parent_dir = Column(Integer, ForeignKey("ParentDir.id"))
    parent = relationship("ParentDir", back_populates="children")

    # TODO, pretending the constraints don't exist for now

