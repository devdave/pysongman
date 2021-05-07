from .. import USE_PYSIDE

if USE_PYSIDE:
    from PySide2 import QtCore
    from PySide2 import QtWidgets


class Playlist(QtCore.QObject):

    def __init__(self, playlist_obj, playlist_table_model):
        """

        Args:
            playlist_obj: A PyBass Playlist object
            playlist_tm: The Table Model for Playlist
        """
        self.playlist = playlist_obj
        self.table_model = playlist_table_model


