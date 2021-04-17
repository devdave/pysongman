import sqlite3

from sqlalchemy import Column, String, Integer, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship

from . import initialize_db
from .base import Base


class Song(Base):
    title = Column(String())
    track = Column(String())

    artist_id = Column(Integer(), ForeignKey("Artist.id"))
    artist = relationship("Artist", backref="songs")

    album_id = Column(Integer(), ForeignKey("Album.id"))
    album = relationship("Album", backref="songs")

    filesize = Column(Float)  # Bytes


    #library metadata
    play_count = Column(Integer, default=0)
    last_played = Column(DateTime, default=None)


    @classmethod
    def GetByPath(cls, path):
        """
            TODO - Should I figure out how to do this with pure SqlAlchemy?

        Args:
            path: str or pathlib.Path

        Returns:

        """

        SQL = """
        SELECT 
            Song.id, ParentDir.path || Song.rel_path as path 
        FROM Song 
        LEFT JOIN ParentDir PD on PD.id = Song.parent_dir
        WHERE
            path == ?
        """
        conn = initialize_db()
        raw = conn.e.raw_connection()
        cursor = raw.cursor()
        try:
            cursor.execute(SQL, path)
        except sqlite3.OperationalError:
            return None

        result = cursor.fetchone()
        sid = result[0]

        return Song.query.filter(Song.id == sid).first()







