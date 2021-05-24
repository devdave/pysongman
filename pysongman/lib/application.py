import pathlib
from pathlib import Path
import logging
import typing

import pysongman
from .. import DB_FILE
from ..lib.song_directory_collector import SongDirectoryCollector


from .qtd import QApplication, QtCore, Qt, QtGui, Signal, Slot

from pybass3.pys2_playlist import Pys2Playlist as Playlist
from pybass3.pys2_song import Pys2Song as Song

from ..models import initialize_db
from ..models.album import Album as AlbumModel
from ..models.artist import Artist as ArtistModel
from ..models.song import Song as SongModel

from ..controllers.media import MediaController
from ..controllers.player import PlayerControl
from ..controllers.playlist import Playlist as PlaylistController
from ..controllers.config.master import ConfigMasterController

log = logging.getLogger(__name__)


class Application(QApplication):

    ACCEPTED_SUFFIX = ['.mp3', '.mp4', '.ogg', '.opus', '.wav']

    # environment
    _here: pathlib.Path
    _home: pathlib.Path
    _configured_file: pathlib.Path
    _configured: bool
    _pool: QtCore.QThreadPool

    # startup arguments
    song_path: list
    nuke_everything: bool  # Wipe out the database and other configuration files
    debug_enabled: bool  # if True enables debugging features across the app

    # Application components
    playlist: Playlist
    playlist_control: PlaylistController
    player_control: PlayerControl
    player_control: PlaylistController
    media_control: MediaController
    master_config: typing.Union[ConfigMasterController, None]

    def __init__(self, here=None, home=None, configured_file=None):
        super(Application, self).__init__()
        log.debug(f"Initialized Application with {here=}, {home=}, {configured_file=}")

        self._here = here
        self._home = home
        self._configured_file = home / configured_file
        self._configured = self._configured_file.exists()
        self._database_file = self._home / pysongman.DB_FILE
        self._pool = QtCore.QThreadPool()
        self._work_pending = 0

        # I don't want to saturate/thrash the GIL so keep this down to 4 workers
        self._pool.setMaxThreadCount(4)

        log.debug("Application is configured/setup %s @ %s", self._configured, self._configured_file)
        log.debug("Database will be at %s", self._database_file)

        self.song_path = list()
        self.nuke_everything = False
        self.debug_enabled = False

        log.debug("Application is configured %r", self._configured)

        self.playlist = Playlist()

    def configure(self, song_path: list = None, nuke_everything: bool = False, debug_flag: bool = False):
        log.debug("Running startup")

        self.song_path = song_path
        self.nuke_everything = nuke_everything
        self.debug_enabled = debug_flag

        if debug_flag is True:
            from pybass3.bass_stream import BassStream
            BassStream.DEBUG_BASS_STREAM = True

        if self.nuke_everything is True:
            self._database_file.unlink(True)
            self._configured_file.unlink(True)
            self._configured = False

        if self._configured is False:
            initialize_db(create=True, db_location=self._database_file)
            self._configured_file.touch()
        else:
            initialize_db(create=False, db_location=self._database_file)

        self.create_controllers()
        self.setup_connections()

        self.playlist_control.show()
        self.player_control.show()

        if self.song_path:
            if isinstance(self.song_path, list) is False:
                raise ValueError(f"Expected song_path to be a list but got {type(self.song_path)}{song_path=} instead")

            for element in self.song_path:
                file_dir = Path(element)
                if file_dir.exists():
                    if file_dir.is_dir():
                        # self.playlist.add_directory(file_dir, top=True)
                        self._work_pending += 1
                        worker = self.generate_recursing_song_directory_worker(file_dir)
                        # worker.signals.song_found.connect(self.on_directory_worker_add_song)
                        worker.signals.songs_found.connect(self.on_directory_worker_add_songs)
                        worker.signals.work_complete.connect(self.on_directory_worker_finished)
                        self.execute_song_directory_collector(worker)


                    elif file_dir.is_file():
                        self.playlist.add_song_by_path(file_dir)

            if len(self.playlist) > 0 and self._work_pending <= 0:
                self.playlist.play()

    def create_controllers(self):
        self.player_control = PlayerControl(self.playlist)
        self.playlist_control = PlaylistController(self.playlist)
        self.media_control = MediaController(self.playlist)
        self.master_config = None

    def setup_connections(self):

        self.player_control.signals.view_closed.connect(self.do_close)
        self.player_control.signals.show_medialib.connect(self.toggle_medialib)
        self.player_control.signals.show_playlist.connect(self.toggle_playlist)
        self.player_control.signals.key_pressed.connect(self.on_key_pressed)
        self.player_control.signals.show_config.connect(self.toggle_masterconfig)

        log.debug("Application connections setup")

    @Slot(bool)
    def toggle_medialib(self, toggle):
        log.debug("Toggling medialib %s", toggle)
        if self.media_control.view.isVisible() is False or self.media_control.view.isHidden() is True:
            self.media_control.show()
            self.media_control.signals.show_config.connect(self.toggle_masterconfig)
            self.media_control.view.activateWindow()
        else:
            self.media_control.hide()

    @Slot(bool)
    def toggle_playlist(self, toggle):
        log.debug("Should toggle playlist, %s", toggle)
        if self.playlist_control.view.isHidden():
            self.playlist_control.show()
        elif self.playlist_control.view.isVisible() is False:
            self.playlist_control.view.activateWindow()
        elif self.playlist_control.view.isVisible() is True:
            self.playlist_control.hide()

    @Slot()
    def toggle_masterconfig(self):
        if self.master_config is None:
            self.master_config = ConfigMasterController()
            self.master_config.show()
            self.master_config.signals.closed.connect(self.clean_up_master_config)
            self.master_config.view.signals.on_close.connect(self.clean_up_master_config)
        else:
            self.master_config.activate()

    def clean_up_master_config(self):
        self.master_config.view.hide()
        self.master_config = None

    @Slot(int)
    def do_close(self, return_code=0):
        log.debug("Closing application")
        self.exit(return_code)


    def generate_recursing_song_directory_worker(self, file_dir) -> SongDirectoryCollector:
        return SongDirectoryCollector(file_dir, recurse=True, valid_suffix=self.ACCEPTED_SUFFIX)

    def execute_song_directory_collector(self, collector_worker):
        return self._pool.start(collector_worker)

    @Slot()
    def on_directory_worker_finished(self):
        if len(self.playlist) > 0:
            self.playlist.play()

    @Slot(str, dict, float, int)
    def on_directory_worker_add_song(self, song_path:str, tags:dict, length_seconds:float, length_bytes:int):
        song = Song(pathlib.Path(song_path), tags=tags, length_seconds=length_seconds, length_bytes=length_bytes)

        self.playlist.add_song(song, add2queue=True)

    @Slot(list)
    def on_directory_worker_add_songs(self, songs_list:typing.List[typing.Tuple[str, dict, float, int]]):
        for song_prim in songs_list:
            self.on_directory_worker_add_song(*song_prim)


    @Slot(QtGui.QKeyEvent)
    def on_key_pressed(self, event: QtGui.QKeyEvent):
        log.debug("Application is handling keypress %s", event.key())
        if event.key() == Qt.Key_Z:
            self.playlist.previous()
        elif event.key() == Qt.Key_X:
            self.playlist.play()
        elif event.key() == Qt.Key_C:
            self.playlist.pause()
        elif event.key() == Qt.Key_V:
            self.playlist.stop()
        elif event.key() == Qt.Key_B:
            self.playlist.next()


    def on_medialibrary_rescan_request(self):
        pass

