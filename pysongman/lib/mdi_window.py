
from .qtd import QtCore, QtWidgets, Qt

class MDIWindowSignals(QtCore.QObject):
    pass

class MDIWindow(QtWidgets.QMainWindow):

    menu_tree: QtWidgets.QTreeWidget
    menu_button: QtWidgets.QPushButton
    mdi: QtWidgets.QMdiArea
    signals: MDIWindowSignals

    def __init__(self):
        super(MDIWindow, self).__init__()
        self.signals = MDIWindowSignals()

        self.setup_ui()

    def setup_ui(self):
        divider = QtWidgets.QSplitter(Qt.Horizontal, self)
        menu_side = QtWidgets.QVBoxLayout(self)
        menu_frame = QtWidgets.QFrame()

        self.menu_tree = QtWidgets.QTreeWidget(self)
        self.menu_button = QtWidgets.QPushButton("Close")

        menu_side.addWidget(self.menu_tree)
        menu_side.addWidget(self.menu_button)
        menu_frame.setLayout(menu_side)

        self.mdi = QtWidgets.QMdiArea(self)

        divider.addWidget(menu_frame)
        divider.addWidget(self.mdi)

        self.setCentralWidget(divider)
