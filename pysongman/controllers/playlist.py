import logging
import pathlib

import pysongman

from pybass3.pys2_playlist import Pys2Playlist
from pybass3.pys2_song import Pys2Song as Song

from ..lib.qtd import QtCore, Qt, QtWidgets, QtGui
from ..tables.playlist import PlaylistTableModel
from ..views.playlist_window import PlaylistWindow
from .search import SearchController

log = logging.getLogger(__name__)


class Playlist(QtCore.QObject):

    playlist: Pys2Playlist
    table_model: PlaylistTableModel
    view: PlaylistWindow

    def __init__(self, playlist_obj: Pys2Playlist):
        """

        Args:
            playlist_obj: A PyBass Playlist object
            playlist_tm: The Table Model for Playlist
        """
        super(Playlist, self).__init__()
        log.debug("Initialized PlaylistController")

        self.playlist = playlist_obj
        self.table_model = PlaylistTableModel(playlist_obj)
        self.view = PlaylistWindow(self.playlist, self.table_model)
        self.search = SearchController(self.table_model, self.playlist)

        self.setup_connections()
        self.setup_menu_connections()
        self.setup_toolbar_connections()
        
        

    def setup_connections(self):
        log.debug("Setting up connections")

        self.view.signals.key_presssed.connect(self.on_keypress)

        self.view.table.doubleClicked.connect(self.on_row_doubleclicked)

        self.playlist.signals.song_changed.connect(self.on_song_changed)
        self.playlist.signals.playlist_cleared.connect(self.on_playlist_cleared)

        self.view.signals.search_requested.connect(lambda : self.search.show())

    def setup_toolbar_connections(self):

        self.view.tb_add_dir.triggered.connect(self.on_menu_add_folder)
        self.view.tb_add_files.triggered.connect(self.on_menu_add_file)


    def setup_menu_connections(self):
        log.debug("Setting up menu connections")

        self.view.fm_add_folder.triggered.connect(self.on_menu_add_folder)
        self.view.fm_add_files.triggered.connect(self.on_menu_add_file)
        pass

    def on_keypress(self, event: QtGui.QKeyEvent):
        log.debug("Key pressed %r", event.key())
        if event.key() == Qt.Key_J:
            log.debug("Show Search")
        elif event.key() in [Qt.Key_Enter, Qt.Key_Return]:
            self.play_selected_record()

    def play_selected_record(self):
        sel_idx = self.view.table.selectionModel().selectedIndexes()[0]
        self.playlist.play_song_by_index(sel_idx.row())

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
            worker = pysongman.App.generate_song_directory_worker(new_dir) # type: SongDirectoryCollector
            worker.signals.song_found.connect(self.on_directory_worker_add_song)
            self.playlist.add_directory(new_dir, top=True, recurse=False, suppress_emit=False)

    def on_directory_worker_add_song(self, song_path: str, tags: dict, length_seconds: float, length_bytes: int):
        song = Song(pathlib.Path(song_path), tags=tags, length_seconds=length_seconds, length_bytes=length_bytes)

        self.playlist.add_song(song, add2queue=True)

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


    def on_playlist_cleared(self):
        self.table_model.beginResetModel()
        self.table_model.endResetModel()