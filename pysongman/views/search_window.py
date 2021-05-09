from .. import USE_PYSIDE

if USE_PYSIDE:
    from PySide2 import QtCore, QtWidgets

    from pybass3.pys2_playlist import Pys2Playlist

    Qt = QtCore.Qt

class SearchWindow(QtWidgets.QWidget):

    playlist: Pys2Playlist
    search_box: QtWidgets.QTextEdit
    choices: QtWidgets.QListView

    def __init__(self, playlist: Pys2Playlist):
        super(SearchWindow, self).__init__()
        self.playlist = playlist
