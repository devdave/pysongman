import logging

from .. import USE_PYSIDE
import typing as T
import pathlib

if USE_PYSIDE:
    import PySide2
    from PySide2.QtGui import QPixmap
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtCore import Qt

    from pybass3.pys2_playlist import Pys2Playlist

from .. import ICON_DIR
from .. import CSS_DIR
from ..tables.playlist import PlaylistTableModel

log = logging.getLogger(__name__)


class AlignLeftDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option:PySide2.QtWidgets.QStyleOptionViewItem, index:PySide2.QtCore.QModelIndex) -> None:
        super(AlignLeftDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignLeft


class PlaylistWindow(QtWidgets.QMainWindow):

    #Signals
    keyPressed = QtCore.Signal(QtGui.QKeyEvent)
    search_requested = QtCore.Signal()

    # UI Elements
    frame: QtWidgets.QFrame
    model: PlaylistTableModel
    body: QtWidgets.QVBoxLayout
    table: QtWidgets.QTableView

    # menu hints
    fm_clear: QtWidgets.QAction
    fm_open: QtWidgets.QAction
    fm_open_from_lib: QtWidgets.QAction
    fm_open_library_view_results: QtWidgets.QAction
    fm_add_files: QtWidgets.QAction
    fm_add_folder: QtWidgets.QAction
    fm_save: QtWidgets.QAction
    fm_fileinfo: QtWidgets.QAction
    fm_close: QtWidgets.QAction

    plm_select_all: QtWidgets.QAction
    plm_select_none: QtWidgets.QAction
    plm_select_invert: QtWidgets.QAction
    plm_remove_selected: QtWidgets.QAction
    plm_crop_selected: QtWidgets.QAction
    plm_clear_playlist: QtWidgets.QAction
    plm_remove_missing: QtWidgets.QAction
    plm_delete_files: QtWidgets.QAction
    plm_preferences: QtWidgets.QAction

    sort_by_title: QtWidgets.QAction
    sort_by_filename: QtWidgets.QAction
    sort_by_path_filename: QtWidgets.QAction
    sort_reverse: QtWidgets.QAction
    sort_randomize: QtWidgets.QAction

    help_about: QtWidgets.QAction

    tb_add_menu: QtWidgets.QMenu
    tb_add_files: QtWidgets.QAction
    tb_add_dir: QtWidgets.QAction

    tb_rem_menu: QtWidgets.QMenu
    tb_rem_selected: QtWidgets.QAction
    tb_rem_clear: QtWidgets.QAction



    def __init__(self, playlist: Pys2Playlist, playlist_table_model: PlaylistTableModel ):
        super(PlaylistWindow, self).__init__()

        self.model = playlist_table_model

        self.body = None
        self.table = None


        self.setup_UI()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_shortcuts()


        self.setWindowFlags(self.windowFlags() & Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
        log.debug("Playlist window initialized")

    def setup_shortcuts(self):
        search_sc = QtWidgets.QShortcut(QtGui.QKeySequence("alt+j"), self)
        search_sc.activated.connect( lambda : self.search_requested.emit())

    def setup_toolbar(self):

        add_button = QtWidgets.QPushButton("Add")
        rem_button = QtWidgets.QPushButton("Rem")

        toolbar = QtWidgets.QToolBar(self)

        self.addToolBar(Qt.BottomToolBarArea, toolbar)

        toolbar.addWidget(add_button)
        toolbar.addWidget(rem_button)

        self.tb_add_menu = QtWidgets.QMenu()  # Need to keep a reference ot the menu or else it ceases to exist
        self.tb_add_files = self.tb_add_menu.addAction("Add Files")
        self.tb_add_dir = self.tb_add_menu.addAction("Add Folder")

        self.tb_rem_menu = QtWidgets.QMenu()
        self.tb_rem_selected = self.tb_rem_menu.addMenu("Remove selected")
        self.tb_rem_clear = self.tb_rem_menu.addMenu("Clear playlist")

        add_button.setMenu(self.tb_add_menu)






        self.search_sc.activated.connect( lambda : self.search_requested.emit())


    def setup_UI(self):
        self.frame = QtWidgets.QFrame()

        self.setWindowTitle("Playlist editor")
        self.body = QtWidgets.QVBoxLayout(self.frame)

        self.table = QtWidgets.QTableView()
        self.table.setModel(self.model)

        self.table.verticalHeader().hide()

        # self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.table.resizeColumnsToContents()
        self.table.hideColumn(0)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        alignleft = AlignLeftDelegate(self.table)
        self.table.setItemDelegateForColumn(2, alignleft)


        self.body.addWidget(self.table)
        self.body.setStretch(0, 1)
        self.setMinimumWidth(725)
        self.setMaximumWidth(750)



        self.setCentralWidget(self.frame)



    def setup_menu(self):
        bar = self.menuBar()
        self.file_menu = bar.addMenu("&File")
        self.fm_clear = self.file_menu.addAction("New playlist(clear)")
        self.fm_open = self.file_menu.addAction("Open playlist")
        self.fm_open_from_lib = self.file_menu.addAction("Open playlist from Library")
        self.fm_open_library_view_results = self.file_menu.addMenu("Open Library view results")
        self.file_menu.addSeparator()

        self.fm_add_files = self.file_menu.addAction("Add files(s)")
        self.fm_add_folder = self.file_menu.addAction("Add folder")
        self.file_menu.addSeparator()

        self.fm_save = self.file_menu.addAction("Save playlist")
        self.file_menu.addSeparator()

        self.fm_fileinfo = self.file_menu.addAction("File info")
        # self.fm_pl_entry = self.file_menu.addAction("Playlist entry")
        self.file_menu.addSeparator()

        self.fm_close = self.file_menu.addAction("Close Playlist Editor")


        self.playlist_menu = bar.addMenu("&Playlist")
        self.plm_select_all = self.playlist_menu.addAction("Select all")
        self.plm_select_none = self.playlist_menu.addAction("Select none")
        self.plm_select_invert = self.playlist_menu.addAction("Invert Selection")
        self.playlist_menu.addSeparator()

        self.plm_remove_selected = self.playlist_menu.addAction("Remove selected")
        self.plm_crop_selected = self.playlist_menu.addAction("Crop selected")
        self.plm_clear_playlist = self.playlist_menu.addAction("Clear playlist")
        self.playlist_menu.addSeparator()

        self.plm_remove_missing = self.playlist_menu.addAction("Remove missing files from playlist")
        self.plm_delete_files = self.playlist_menu.addAction("Physically remove selected file(s)")
        self.playlist_menu.addSeparator()

        self.plm_preferences = self.playlist_menu.addAction("Playlist preferences")
        self.playlist_menu.addSeparator()


        self.sort_menu = bar.addMenu("&Sort")
        self.sort_by_title = self.sort_menu.addAction("Sory list by title")
        self.sort_by_filename = self.sort_menu.addAction("Sort list by filename")
        self.sort_by_path_filename = self.sort_menu.addAction("Sort list by path and filename")
        self.sort_menu.addSeparator()

        self.sort_reverse = self.sort_menu.addAction("Reverse list")
        self.sort_randomize = self.sort_menu.addAction("Randomize list")

        self.help = bar.addMenu("&Help")
        self.help_about = self.help.addAction("About")


    def keyPressEvent(self, event:QtGui.QKeyEvent) -> None:
        super(PlaylistWindow, self).keyPressEvent(event)
        self.keyPressed.emit(event)

        event.accept()