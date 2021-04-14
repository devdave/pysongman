
SA_ENGINE = None
SA_FACTORY = None

from .. import HOME, APP_NAME
from .base import Base

from pathlib import Path
from dataclasses import dataclass

import sqlalchemy
from sqlalchemy import create_engine, engine
from sqlalchemy.ext import declarative
from sqlalchemy import orm
from sqlalchemy.orm import scoped_session, sessionmaker, session, query


@dataclass
class SAConnection:
    e: sqlalchemy.engine
    q: orm.query


def initialize_db() -> SAConnection:
    global SA_ENGINE, SA_FACTORY

    if SA_ENGINE is None:
        home_path = Path(HOME)
        engine_url = f"sqlite:///{home_path.as_posix()}/{APP_NAME}.sqlite3"
        SA_ENGINE = create_engine(engine_url)
        Base.metadata.bind = SA_ENGINE

    if SA_FACTORY is None:
        sm = sessionmaker(bind=SA_ENGINE)
        SA_FACTORY = scoped_session(sm)
        Base.query = SA_FACTORY.query_property()\

    session = SA_FACTORY()

    return SAConnection(SA_ENGINE, session)



