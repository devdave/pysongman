from pathlib import Path

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from ..lib.path_type import PathType

from .base import Base

class ParentDir(Base):
    path = Column(PathType(), unique=True)

    @classmethod
    def GetCreate(cls, dir_path: Path):

        record = cls.query.filter(cls.path == dir_path).first()

        if record is None:
            record = cls(path=dir_path)

        return record