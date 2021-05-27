from pysongman.lib.qtd import QtWidgets, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton


class BaseList(QtWidgets.QWidget):

    search_line: QLineEdit
    search_clear: QPushButton
    table: QtWidgets.QTableView

    def __init__(self):
        super(BaseList, self).__init__()
        self.setup_ui()

    def setup_ui(self):

        body = QVBoxLayout(self)
        search_body = QHBoxLayout(self)

        search_label = QLabel("Search:", self)
        self.search_line = QLineEdit(self)
        self.search_clear = QPushButton("Clear Search")

        search_body.addWidget(search_label)
        search_body.addWidget(self.search_line)
        search_body.addWidget(self.search_clear)

        body.addLayout(search_body)

        self.table = QtWidgets.QTableView(self)

        body.addWidget(self.table)

        self.setLayout(body)







