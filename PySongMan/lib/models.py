import asyncio
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
    ForeignKey,
    UniqueConstraint,
    Table,
    Column,
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import async_scoped_session

from sqlalchemy.orm import (
    Session,
    DeclarativeBase,
    Mapped,
    mapped_column,
    declared_attr,
    scoped_session,
    sessionmaker,
    relationship,
)

from .app_types import Identifier, SongType, TagType


log = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def async_db(db_url="sqlite:///pysongman.sqlite3", echo=False, create=False):
    engine = create_async_engine(db_url, echo=echo)

    if create is True:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    maker = async_scoped_session(
        async_sessionmaker(bind=engine, expire_on_commit=False), asyncio.current_task
    )

    session = maker()
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


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


def connect(db_path: pathlib.Path | str, echo=False, create=True):
    """

    :param db_path:
    :param echo: Echo session data to console
    :param create: Try to create schema if it doesn't exist
    :return:
    """
    engine = create_engine(
        db_path, echo=echo, pool_size=10, max_overflow=20, connect_args={"timeout": 15}
    )
    if create:
        Base.metadata.create_all(engine, checkfirst=True)

    session_factory = sessionmaker(bind=engine)

    return engine, scoped_session(session_factory)


def get_scoped_session(db_path: pathlib.Path | str, echo=False, create=False):

    engine, scoped = connect(db_path, echo=echo, create=create)

    return scoped()


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


class Tag(Base):
    name: Mapped[str] = mapped_column(index=True)
    value: Mapped[str] = mapped_column(index=True)

    songs: Mapped[list["Song"]] = relationship(
        secondary="Song_Tag", back_populates="tags"
    )

    def to_dict(self):
        return TagType(id=self.id, name=self.name, value=self.value)

    __table_args__ = (
        UniqueConstraint(
            "name",
            "value",
            sqlite_on_conflict="REPLACE",
            name="unique_name_value",
        ),
    )


Song_Tag = Table(
    "Song_Tag",
    Base.metadata,
    Column("song_id", ForeignKey("Song.id"), primary_key=True),
    Column(
        "tag_id",
        ForeignKey("Tag.id"),
        primary_key=True,
    ),
)


class Song(Base):
    name: Mapped[str]
    artist: Mapped[str] = mapped_column(index=True)
    size: Mapped[int] = mapped_column(index=True)
    length_seconds: Mapped[int]

    file_name: Mapped[str]
    path: Mapped[str] = mapped_column(index=True, unique=True)

    codec: Mapped[str]
    format: Mapped[str]

    tags: Mapped[list[Tag]] = relationship(secondary=Song_Tag, back_populates="songs")

    library_id: Mapped[str] = mapped_column(ForeignKey("Library.id"), index=True)
    library: Mapped["Library"] = relationship("Library", back_populates="songs")

    __table_args__ = (UniqueConstraint("path", "name", name="unique_song"),)

    def to_dict(self):
        return SongType(
            id=self.id,
            name=self.name,
            artist=self.artist,
            size=self.size,
            length_seconds=self.length_seconds,
            tags=[tag.to_dict() for tag in self.tags],
        )

    @classmethod
    def GetPage(cls, session: Session, page: int, limit: int = 100):
        stmt = select(cls).limit(limit).offset(max(page, 1) * limit)
        return session.execute(stmt).scalars().all()


class Library(Base):
    path: Mapped[str] = mapped_column(index=True, unique=True)

    songs: Mapped[list[Song]] = relationship("Song", back_populates="library")
