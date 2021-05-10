from pathlib import Path
import logging

from .. import USE_PYSIDE

if USE_PYSIDE:
    from pybass3.pys2_playlist import Pys2Playlist
    from PySide2.QtCore import Qt
    from PySide2 import QtGui


from ..controllers.player import PlayerControl
from ..controllers.playlist import Playlist as PlaylistController

log = logging.getLogger(__name__)

class Application(QApplication):

    def __init__(self, song_path: list = None, nuke_everything: bool = False):
        super(Application, self).__init__()
        self.song_path = song_path
        self.nuke_everything = nuke_everything

        self.playlist = Pys2Playlist()
        self.player_control = PlayerControl(self.playlist)
        self.playlist_control = PlaylistController(self.playlist)

        self.setup_connections()


    def setup_connections(self):

        self.player_control.viewClosed.connect(self.do_close)
        self.player_control.showMedialib.connect(self.toggle_medialib)
        self.player_control.showPlayList.connect(self.toggle_playlist)
        self.player_control.key_pressed.connect(self.on_key_pressed)

    def toggle_medialib(self, toggle):
        pass

    def toggle_playlist(self, toggle):
        log.debug("Should toggle playlist, %s", toggle)
        if self.playlist_control.view.isVisible() is False or self.playlist_control.view.isHidden() is True:
            self.playlist_control.show()
        else:
            self.playlist_control.hide()


    def do_close(self, return_code=0):
        log.debug("Closing application")
        self.exit(return_code)

    def startup(self):
        self.playlist_control.show()
        self.player_control.show()

        if self.song_path is not None:
            if isinstance(self.song_path, list) is False:
                raise ValueError(f"Expected song_path to be a list but got {type(self.song_path)} instead")

            for element in self.song_path:
                file_dir = Path(element)
                if file_dir.is_dir():
                    self.playlist.add_directory(file_dir)
                elif file_dir.is_file():
                    self.playlist.add_song(file_dir)

            if len(self.playlist) > 0:
                self.playlist.play()
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