import pathlib
from pathlib import Path
import sqlite3

from sqlalchemy import Column, String, Integer, ForeignKey, Float, DateTime, func, Boolean
from sqlalchemy.orm import relationship, Query
from sqlalchemy.ext.hybrid import hybrid_property

from pybass3 import BassException
from pybass3.pys2_song import Pys2Song as SongObj

from . import initialize_db
from .artist import Artist
from .album import Album
from ..lib.path_type import PathType
from .base import Base


class Song(Base):

    path: Path = Column(PathType(), unique=True) # type: Path

    title = Column(String())
    is_valid = Column(Boolean(), default=False)
    invalid_reason = Column(String(), default=None)

    # metadata
    filesize = Column(Float())  # Bytes according to Bass library
    stat_created = Column(Integer())  # uses Path.stat.st_create
    stat_modified = Column(Integer())  # uses Path.stat.st_modified
    length_seconds = Column(Float())
    length_bytes = Column(Integer())

    @hybrid_property
    def time(self):
        seconds = int(self.length_seconds % 60)
        minutes = int(self.length_seconds // 60)
        return f"{minutes}:{seconds:02}"


    added_to_library = Column(DateTime(), server_default=func.now())
    last_played = Column(DateTime(), default=None)

    # library metadata
    play_count = Column(Integer, default=0)

    parent_id = Column(Integer(), ForeignKey("ParentDir.id"))
    parent = relationship("ParentDir", backref="songs")

    artist_id = Column(Integer(), ForeignKey("Artist.id"))
    artist = relationship("Artist", backref="songs")

    album_id = Column(Integer(), ForeignKey("Album.id"))
    album = relationship("Album", backref="songs")

    # type hint helper
    query: Query

    @classmethod
    def GetByPath(cls, song_path: pathlib.Path):

        if song_path.exists() is False:
            raise ValueError("Providing path doesn't exist: %s" % song_path)

        return cls.query.filter(cls.path == song_path).first()


    @classmethod
    def GetCreateByPath(cls, song_path: pathlib.Path, parent) -> "Song":

        if song_path.exists() is False:
            raise ValueError("Providing path doesn't exist: %s" % song_path)

        old_record = True
        record = cls.query.filter(cls.path == song_path, cls.parent == parent).first()

        if record is None:
            old_record = False
            record = cls()
            record.path = song_path
            record.filesize = song_path.stat().st_size
            record.stat_created = song_path.stat().st_ctime
            record.stat_modified = song_path.stat().st_mtime

            record.parent = parent

            song = SongObj(file_path=song_path)
            try:
                song.touch()
                record.is_valid = True
            except BassException:
                # log.debug("Failed to load %r", song_path)
                record.is_valid = False
                return record
            else:

                record.length_seconds = song.duration
                record.length_bytes = song.duration_bytes

                artist_name = song_path.name if song.tags['artist'] is None else song.tags['artist']
                album_name = song_path.parent.name if song.tags['album'] is None else song.tags['album']

                record.title = song.tags['title']
                record.artist = Artist.GetCreate(artist_name)
                record.album = Album.GetCreate(record.artist, album_name)





        return record

    def __repr__(self):
        return f"<Song path={self.path.name}>"



