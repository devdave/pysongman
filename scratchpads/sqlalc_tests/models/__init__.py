
SA_ENGINE = None
SA_FACTORY = None



from pathlib import Path
from dataclasses import dataclass

import sqlalchemy
from sqlalchemy import create_engine, engine
from sqlalchemy.ext import declarative
from sqlalchemy import orm
from sqlalchemy.orm import scoped_session, sessionmaker, session, query, Session

from .base import Base

@dataclass
class SAConnection:
    e: sqlalchemy.engine
    s: Session

def get_db_url(db_location=False):
    return f"sqlite:///{db_location.as_posix()}"


def get_db() -> SAConnection:
    global SA_ENGINE, SA_FACTORY

    return SAConnection(SA_ENGINE, SA_FACTORY())

def initialize_db(create=False, db_location=False) -> SAConnection:
    global SA_ENGINE, SA_FACTORY

    if SA_ENGINE is None:
        SA_ENGINE = create_engine(get_db_url(db_location))
        Base.metadata.bind = SA_ENGINE

    if SA_FACTORY is None:
        sm = sessionmaker(bind=SA_ENGINE)
        SA_FACTORY = scoped_session(sm)
        Base.query = SA_FACTORY.query_property()\

    session = SA_FACTORY()

    if create is True:
        from .song import Song
        from .artist import Artist
        from .album import Album
        from .parent_dir import ParentDir

        Base.metadata.create_all(SA_ENGINE)

    return SAConnection(SA_ENGINE, session)



