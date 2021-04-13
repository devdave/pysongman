
import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets


class Media(QtWidgets.QWidget):

    def __init__(self):
        super(Media, self).__init__()

        self.artist_table = None
        self.album_table = None
        self.songs_table = None

        self.top = None
        self.body = None
        self.frame = None
        self.setupUI()

    def setupUI(self):
        # our widgets
        self.artist_table = QtWidgets.QTableView()
        self.album_table = QtWidgets.QTableView()
        divide = QtWidgets.QSplitter()
        self.songs_table = QtWidgets.QTableView()

        # get rid of the vertical headers
        for table in [self.artist_table, self.album_table, self.songs_table]:
            table.verticalHeader().hide()
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
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

        #Why did I do this?
        self.frame = QtWidgets.QFrame(self)
        self.frame.setLayout(self.body)


        self.setWindowTitle("Media Library")


