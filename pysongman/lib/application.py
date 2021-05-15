import pathlib
from pathlib import Path
import logging
import typing

from .. import DB_FILE, USE_PYSIDE

if USE_PYSIDE is True:
    from pybass3.pys2_playlist import Pys2Playlist
    from PySide2.QtWidgets import QApplication
    from PySide2.QtCore import Qt
    from PySide2 import QtGui

from ..models import initialize_db
from ..controllers.media import MediaController
from ..controllers.player import PlayerControl
from ..controllers.playlist import Playlist as PlaylistController
from ..controllers.config.master import ConfigMasterController

log = logging.getLogger(__name__)


class Application(QApplication):

    # Known controllers
    master_config: ConfigMasterController

    # environment
    _here: pathlib.Path
    _home: pathlib.Path
    _configured_file: pathlib.Path
    _configured: bool

    # startup arguments
    song_path: list
    nuke_everything: bool  # Wipe out the database and other configuration files
    debug_enabled: bool  # if True enables debugging features across the app

    # Application components
    playlist: Pys2Playlist
    player_control: PlayerControl
    player_control: PlaylistController
    media_control: MediaController
    master_config: typing.Union[ConfigMasterController, None]

    def __init__(self, here=None, home=None, configured=None):
        super(Application, self).__init__()
        log.debug(f"Initialized Application with {here=}, {home=}, {configured=}")

        self._here = here
        self._home = home
        self._configured_file = configured
        self._configured = configured.exists()

        log.debug("Application is configured/setup %s", self._configured)

        self.song_path = list()
        self.nuke_everything = False
        self.debug_enabled = False

        log.debug("Application is configured %r", self._configured)

        self.playlist = Pys2Playlist()
        self.player_control = PlayerControl(self.playlist)
        self.playlist_control = PlaylistController(self.playlist)
        self.media_control = MediaController(self.playlist)
        self.master_config = None

        self.setup_connections()

    def setup_connections(self):

        self.player_control.viewClosed.connect(self.do_close)
        self.player_control.showMedialib.connect(self.toggle_medialib)
        self.player_control.showPlayList.connect(self.toggle_playlist)
        self.player_control.key_pressed.connect(self.on_key_pressed)
        self.player_control.showMasterConfig.connect(self.toggle_masterconfig)

        log.debug("Application connections setup")

    def toggle_medialib(self, toggle):
        log.debug("Toggling medialib %s", toggle)
        if self.media_control.view.isVisible() is False or self.media_control.view.isHidden() is True:
            self.media_control.show()
            self.media_control.view.activateWindow()
        else:
            self.media_control.hide()

    def toggle_playlist(self, toggle):
        log.debug("Should toggle playlist, %s", toggle)
        if self.playlist_control.view.isHidden():
            self.playlist_control.show()
        elif self.playlist_control.view.isVisible() is False:
            self.playlist_control.view.activateWindow()
        elif self.playlist_control.view.isVisible() is True:
            self.playlist_control.hide()

    def toggle_masterconfig(self):
        if self.master_config is None:
            self.master_config = ConfigMasterController()
            self.master_config.show()
            self.master_config.view.onClose.connect(self.clean_up_master_config)
        else:
            self.master_config.activate()

    def clean_up_master_config(self):
        self.master_config = None

    def do_close(self, return_code=0):
        log.debug("Closing application")
        self.exit(return_code)

    def configure(self, song_path: list = None, nuke_everything: bool = False, debug_flag: bool = False):
        log.debug("Running startup")

        self.song_path = song_path
        self.nuke_everything = nuke_everything
        self.debug_enabled = debug_flag

        if debug_flag is True:
            from pybass3.bass_stream import BassStream
            BassStream.DEBUG_BASS_STREAM = True

        if self.nuke_everything is True:
            DB_FILE.unlink(True)
            self._configured_file.unlink(True)
            self._configured = False

        if self._configured is False:
            initialize_db(create=True)
            self._configured_file.touch()
        else:
            initialize_db(create=False)

        self.playlist_control.show()
        self.player_control.show()

        if self.song_path:
            if isinstance(self.song_path, list) is False:
                raise ValueError(f"Expected song_path to be a list but got {type(self.song_path)}{song_path=} instead")

            for element in self.song_path:
                file_dir = Path(element)
                if file_dir.exists():
                    if file_dir.is_dir():
                        # TODO put a Threaded worker to preload up song data
                        self.playlist.add_directory(file_dir, top=True)
                    elif file_dir.is_file():
                        self.playlist.add_song(file_dir)

            if len(self.playlist) > 0:
                self.playlist.play()

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
