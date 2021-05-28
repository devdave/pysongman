from pysongman.lib.qtd import QtWidgets, Qt
from pysongman.lib.qtd import QHBoxLayout
from pysongman.lib.qtd import QVBoxLayout
from pysongman.lib.qtd import QLabel
from pysongman.lib.qtd import QLineEdit
from pysongman.lib.qtd import QPushButton
from pysongman.lib.qtd import QFrame


class AudioWindow(QtWidgets.QWidget):

    search_label: QLabel
    search_input: QLineEdit
    clear_button: QPushButton

    artist_table: QtWidgets.QTableView
    album_table: QtWidgets.QTableView
    songs_table: QtWidgets.QTableView

    def __init__(self):
        super(AudioWindow, self).__init__()

        self.top = None
        self.body = None
        self.frame = None
        self.setup_ui()

    def setup_ui(self):
        """

        frame
            VBOX
                HBOX # Search label # Line edit # clear button
                ##############################################
                    HBOX # Artist Table | SPLITTER | Album Table
                |SPLITTER |
                    # Song table #


        """

        self.frame = QFrame()
        self.body = QVBoxLayout()

        search_line = QHBoxLayout()
        search_label = QLabel("Search: ")
        self.search_input = QLineEdit()
        self.clear_button = QPushButton("Clear Search")

        search_line.addWidget(search_label)
        search_line.addWidget(self.search_input)
        search_line.addWidget(self.clear_button)

        self.body.addLayout(search_line)

        self.artist_table = QtWidgets.QTableView()
        self.album_table = QtWidgets.QTableView()
        self.songs_table = QtWidgets.QTableView()

        # get rid of the vertical headers
        for table in [self.artist_table, self.album_table, self.songs_table]:
            table.verticalHeader().hide()
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            table.setSortingEnabled(True)
            table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        artist_album_split = QtWidgets.QSplitter(Qt.Horizontal)
        artist_album_split.addWidget(self.artist_table)
        artist_album_split.addWidget(self.album_table)

        a_a_songs_split = QtWidgets.QSplitter(Qt.Vertical)
        a_a_songs_split.addWidget(artist_album_split)
        a_a_songs_split.addWidget(self.songs_table)

        self.body.addWidget(a_a_songs_split)

        self.setLayout(self.body)


    def show(self) -> None:
        super(AudioWindow, self).show()
        self.album_table.model().beginResetModel()
        self.artist_table.model().beginResetModel()


