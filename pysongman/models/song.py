
from . import initialize_db
from .base import Base


class Song(Base):

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
        cursor = raw()
        cursor.execute(SQL, path)
        result = cursor.fetchone()
        sid = result[0]
        return Song.query.filter(Song.id == sid).first()






