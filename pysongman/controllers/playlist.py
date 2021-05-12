import logging
import pathlib

from .. import USE_PYSIDE

if USE_PYSIDE:
    from PySide2 import QtCore
    from PySide2 import QtWidgets

    from pybass3.pys2_playlist import Pys2Playlist

from ..tables.playlist import PlaylistTableModel
from ..views.playlist_window import PlaylistWindow

log = logging.getLogger(__name__)

class Playlist(QtCore.QObject):

    playlist: Pys2Playlist
    table_model: PlaylistTableModel
    view: PlaylistWindow

    def __init__(self, playlist_obj):
        """

        Args:
            playlist_obj: A PyBass Playlist object
            playlist_tm: The Table Model for Playlist
        """
        self.playlist = playlist_obj
        self.table_model = PlaylistTableModel(playlist_obj)
        self.view = PlaylistWindow(self.playlist, self.table_model)

        self.setup_connections()
        self.setup_menu_connections()

    def setup_connections(self):
        self.view.table.doubleClicked.connect(self.on_row_doubleclicked)
        self.playlist.song_changed.connect(self.on_song_changed)

    def setup_menu_connections(self):
        self.view.fm_add_folder.triggered.connect(self.on_menu_add_folder)
        self.view.fm_add_files.triggered.connect(self.on_menu_add_file)
        pass


    def on_menu_add_file(self):
        music_dir = pathlib.Path.home() / "music"
        return_val = QtWidgets.QFileDialog.getOpenFileNames(self.view, "Select song(s) to add", music_dir.as_posix(), "Any (*)")
        log.debug("on_menu_add_file %s", return_val)
        if return_val:
            files, _ = return_val
            for file in files:
                self.playlist.add_song(file)

    def on_menu_add_folder(self):
        music_dir = pathlib.Path.home() / "music"
        new_dir = QtWidgets.QFileDialog.getExistingDirectory(self.view, "Select directory to add", music_dir.as_posix())
        log.debug("on_menu_add_filder %s", new_dir)
        if new_dir:
            self.playlist.add_directory(new_dir, top=True, recurse=False, surpress_emit=False)




    def show(self):
        self.view.show()

    def hide(self):
        self.view.hide()

    def on_row_doubleclicked(self, index: QtCore.QModelIndex):
        log.debug("on_row_doubleclicked %s clicked", index)
        self.playlist.play_song_by_index(index.row())

    def on_song_changed(self, song_id):
        log.debug("Playlist control song changed to %s", song_id)

        song_index = self.playlist.get_indexof_song_by_id(song_id)
        self.view.table.selectRow(song_index)
        self.view.table.resizeColumnsToContents()