import pathlib
from pathlib import Path
import sqlite3

from sqlalchemy import Column, String, Integer, ForeignKey, Float, DateTime, func, Boolean
from sqlalchemy.orm import relationship

from pybass3 import Song as SongObj, BassException

from . import initialize_db
from .artist import Artist
from .album import Album
from ..lib.path_type import PathType
from .base import Base


class Song(Base):

    path: Path = Column(PathType(), unique=True)

    title = Column(String())
    is_valid = Column(Boolean(), default=False)

    # metadata
    filesize = Column(Float())  # Bytes according to Bass library
    stat_created = Column(Integer())  # uses Path.stat.st_create
    stat_modified = Column(Integer())  # uses Path.stat.st_modified
    length_seconds = Column(Float())
    length_bytes = Column(Integer())

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



    @classmethod
    def GetCreateByPath(cls, song_path: pathlib.Path, parent) -> (object, bool):

        if song_path.exists() is False:
            raise ValueError("Providign path doesn't exist: %s" % song_path)

        old_record = True
        record = cls.query.filter(cls.rel_path == song_path, cls.parent == parent).first()

        if record is None:
            old_record = False
            record = cls()
            record.rel_path = song_path
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
                return record, False
            else:

                record.length_bytes = song.duration
                record.length_seconds = song.duration_bytes

                if song.tags['artist'] is None:
                    artist_name = song_path.name
                else:
                    artist_name = song.tags['artist']

                record.artist = Artist.GetCreate(artist_name)

        return record, old_record

    def __repr__(self):
        return f"<Song rel_path={self.rel_path.name}>"



