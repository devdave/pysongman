

from .. import USE_PYSIDE
from ..views.player_window import PlayerWindow


if USE_PYSIDE:
    from pybass3.pys2_playlist import Pys2Playlist
    from PySide2.QtCore import QObject

class PlayerControl(QObject):

    playlist: Pys2Playlist
    view: PlayerWindow

    def __init__(self, playlist: Pys2Playlist):
        super(PlayerControl, self).__init__()
        self.playlist = playlist
        self.view = PlayerWindow()

        self.setupConnections()

    def setupConnections(self):
        pass

    def show(self):
        self.view.show()
