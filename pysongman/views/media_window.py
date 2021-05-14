
import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets


class MediaWindow(QtWidgets.QMainWindow):

    artist_table: QtWidgets.QTableView
    album_table: QtWidgets.QTableView
    songs_table: QtWidgets.QTableView

    toolbar: QtWidgets.QToolBar
    add_button: QtWidgets.QPushButton
    nuke_button: QtWidgets.QPushButton
    add_menu: QtWidgets.QMenu
    act_add_file: QtWidgets.QAction
    act_add_dir: QtWidgets.QAction


    def __init__(self):
        super(MediaWindow, self).__init__()

        self.top = None
        self.body = None
        self.frame = None
        self.setup_ui()
        self.setup_toolbar()

    def setup_toolbar(self):
        self.toolbar = QtWidgets.QToolBar()

        self.add_button = QtWidgets.QPushButton("Add...")
        self.nuke_button = QtWidgets.QPushButton("Nuke")

        self.addToolBar(Qt.BottomToolBarArea, self.toolbar)

        self.toolbar.addWidget(self.add_button)
        self.toolbar.addWidget(self.nuke_button)

        self.add_menu = QtWidgets.QMenu()
        self.act_add_file = QtWidgets.QAction("Add file(s)")
        self.act_add_dir = QtWidgets.QAction("Add folder")

        self.add_menu.addAction(self.act_add_file)
        self.add_menu.addAction(self.act_add_dir)

        self.add_button.setMenu(self.add_menu)

    def setup_ui(self):
        # our widgets
        self.frame = QtWidgets.QFrame()
        self.artist_table = QtWidgets.QTableView()
        self.album_table = QtWidgets.QTableView()
        divide = QtWidgets.QSplitter()
        self.songs_table = QtWidgets.QTableView()

        # get rid of the vertical headers
        for table in [self.artist_table, self.album_table, self.songs_table]:
            table.verticalHeader().hide()
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            table.setSortingEnabled(True)
            table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # layouts
        # top body
        self.top = QtWidgets.QHBoxLayout()
        self.top.setAlignment(Qt.AlignLeft)
        self.top.addWidget(self.artist_table, 1, Qt.AlignLeft)
        self.top.addWidget(self.album_table, 1, Qt.AlignLeft)

        # main body
        self.body = QtWidgets.QVBoxLayout()
        self.body.addLayout(self.top)
        self.body.setAlignment(Qt.AlignLeft)  # Ever get a feeling I really want this to be alligned left?
        self.body.addWidget(divide)
        self.body.addWidget(self.songs_table)

        self.frame.setLayout(self.body)

        self.setCentralWidget(self.frame)

        self.setWindowTitle("Media Library")
        self.setWindowFlags(self.windowFlags() & Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinMaxButtonsHint)


