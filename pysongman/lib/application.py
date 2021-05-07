from .. import USE_PYSIDE

from PySide2.QtWidgets import QApplication

if USE_PYSIDE:
    from pybass3.pys2_playlist import Pys2Playlist


from ..controllers.player import PlayerControl


class Application(QApplication):

    def __init__(self, song_path=None, nuke_everything=False):

        super(Application, self).__init__()
        self.playlist = Pys2Playlist()
        self.plc = PlayerControl(self.playlist)

    def startup(self):
        self.plc.show()