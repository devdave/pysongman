from .. import USE_PYSIDE

if USE_PYSIDE:
    from PySide2 import QtCore, QtWidgets, QtGui

    Qt = QtCore.Qt


class SearchWindow(QtWidgets.QWidget):

    key_search_down = QtCore.Signal()
    key_search_up = QtCore.Signal()
    selected = QtCore.Signal()

    search_box: QtWidgets.QTextEdit
    choices: QtWidgets.QTableWidget


    def __init__(self):
        super(SearchWindow, self).__init__()
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):

        body = QtWidgets.QVBoxLayout(self)

        self.search = QtWidgets.QLineEdit("")
        body.addWidget(self.search)

        self.results = QtWidgets.QListView()
        body.addWidget(self.results)

        self.search.installEventFilter(self)
        self.search.setFocus()

    def setup_shortcuts(self):

        down_pressed = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.Key_Enter), self.results)
        down_pressed.activated.connect(lambda : self.selected.emit())


    def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent) -> bool:
        if watched == self.search:
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() == Qt.Key_Down:
                    self.key_search_down.emit()
                    self.results.setFocus()
                    return False

                
        return super(SearchWindow, self).eventFilter(watched, event)
        
        
