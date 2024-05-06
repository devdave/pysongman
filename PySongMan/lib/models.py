import contextlib
import datetime as DT
import enum
import logging
import pathlib
import typing as T

import sqlalchemy
from sqlalchemy import (
    select,
    update,
    create_engine,
    func,
    delete,
    true,
)

from sqlalchemy.orm import (
    Session,
    DeclarativeBase,
    Mapped,
    mapped_column,
    declared_attr,
    scoped_session,
    sessionmaker,
)

from .app_types import Identifier


log = logging.getLogger(__name__)


@contextlib.contextmanager
def db_with(db_url="sqlite:///pysongman.sqlite3", echo=False, create=False):
    """
    Context wrapper around connect

    :param db_url:
    :param echo:
    :param create:
    :return:
    """

    engine, session = connect(db_url, echo=echo, create=create)
    yield session

    session.close_all()
    engine.dispose()


def connect(db_path: pathlib.Path, echo=False, create=True):
    """

    :param db_path:
    :param echo: Echo session data to console
    :param create: Try to create schema if it doesn't exist
    :return:
    """
    engine = create_engine(
        f"sqlite:///{db_path}", echo=echo, pool_size=10, max_overflow=20
    )
    if create:
        Base.metadata.create_all(engine, checkfirst=True)

    session_factory = sessionmaker(bind=engine)

    return engine, scoped_session(session_factory)


class Base(DeclarativeBase):
    """
    Base/scaffold model class for all other models

    """

    id: Mapped[int] = mapped_column(primary_key=True)

    created_on: Mapped[DT.datetime] = mapped_column(
        default=None, server_default=func.now()
    )
    updated_on: Mapped[DT.datetime] = mapped_column(
        default=None, server_default=func.now(), onupdate=func.now()
    )

    type_annotation_map = {
        enum.Enum: sqlalchemy.Enum(enum.Enum),
    }

    @declared_attr.directive
    def __tablename__(self) -> str:
        return self.__name__

    @classmethod
    def Touch(cls, session: Session, record_id: Identifier):
        """
        Update a record given its record id
        :param session:
        :param record_id:
        :return:
        """
        stmt = update(cls).where(cls.id == record_id).values()
        session.execute(stmt)

    def touch(self):
        """
        Update a record instance

        :return:
        """
        self.updated_on = DT.datetime.now()

    @classmethod
    def GetById(cls, session: Session, record_id: Identifier) -> T.Self:
        """
        Get a record by its ID.

        :param session:
        :param record_id:
        :return:
        """
        stmt = select(cls).where(cls.id == record_id)
        return session.execute(stmt).scalars().one()

    @classmethod
    def DeleteByID(cls, session, record_id) -> bool:
        stmt = delete(cls).where(cls.id == record_id)
        result = session.execute(stmt)
        return result.rowcount == 1

    @classmethod
    def GetAll(cls, session: Session) -> T.Sequence[T.Self]:
        stmt = select(cls)
        return session.execute(stmt).scalars().all()

    @classmethod
    def GetOrCreate(cls, session: Session, defaults=None, **kwargs) -> T.Self | None:
        instance = session.execute(select(cls).filter_by(**kwargs)).one_or_none()
        if instance:
            return instance[0]

        kwargs |= defaults or {}
        new_instance = cls(**kwargs)
        try:
            session.add(new_instance)
            session.commit()
        except sqlalchemy.exc.IntegrityError:  # type: ignore
            session.rollback()
            return session.execute(select(cls).filter_by(**kwargs)).one()[0]

        return new_instance

    def update(self, changeset):
        """
        Update a record with safe values from the provided changeset.

        Safe values are a class defined SAFE_KEYS list attribute of valid model attribute names

        :param changeset:
        :return:
        """
        if not hasattr(self, "SAFE_KEYS"):
            raise AttributeError(
                f"Attempting to update {self} with `{changeset=}` but no safe keys"
            )

        for safe_key in getattr(self, "SAFE_KEYS", []):
            if safe_key in changeset:
                setattr(self, safe_key, changeset[safe_key])
