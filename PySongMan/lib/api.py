"""
The bridge API between the python application and the TS/react frontend
"""

import contextlib
import logging

from .app_types import SongType, GetPlaylistPage, PlaylistPage
from .application import App
from . import models

LOG = logging.getLogger(__name__)


class Logger:
    """
    A simple utility logger
    """

    __app: App

    def __init__(self, app: App):
        self.__app = app
        LOG.debug("Logger initialized")
        print(__name__)

    def info(self, message: str):
        """
        Info logger
        :param message:
        :return:
        """
        LOG.info(message)

    def debug(self, message: str):
        """
        Debug logger

        :param message:
        :return:
        """
        LOG.debug(message)

    def error(self, message: str):
        """
        Error logger

        :param message:
        :return:
        """
        LOG.error(message)


class Songs:

    __app: App

    def __init__(self, app: App):
        self.__app = app

    def list(
        self, page: int, limit: int = 100, filters: dict[str, str] | None = None
    ) -> PlaylistPage:
        with self.__app.get_db() as session:
            response = models.Song.GetPage(session, page, limit, filters)
            return dict(
                data=[song.to_dict() for song in response["data"]],
                offset=max(1, page) * limit,
                limit=limit,
                page=page,
                count=response["count"],
            )

    def get(self, song_id: int) -> SongType:
        with self.__app.get_db() as session:
            return models.Song.GetById(session, song_id).to_dict()

    def play(self, song_id: int) -> SongType:
        pass

    def stop(self):
        pass


class API:
    """
    The actual API bridge
    """

    __app: App
    logger: Logger
    songs: Songs

    def __init__(self, app):
        self.__app = app

        self.logger = Logger(app)
        self.songs = Songs(app)

    def info(self, message: str):
        print(">", message)
