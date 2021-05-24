from .. import USE_PYSIDE


from ..lib.qtd import QtCore, QtWidgets, QtGui, Qt


class SearchWindowSignals(QtCore.QObject):
    """
        Signals used by Search window
    """
    key_search_down = QtCore.Signal()
    key_search_up = QtCore.Signal()
    selected = QtCore.Signal()


class SearchWindow(QtWidgets.QWidget):

    signals: SearchWindowSignals()

    search_box: QtWidgets.QTextEdit
    choices: QtWidgets.QTableWidget


    def __init__(self):
        super(SearchWindow, self).__init__()
        self.signals = SearchWindowSignals()
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):

        body = QtWidgets.QVBoxLayout(self)

        self.search = QtWidgets.QLineEdit("")
        body.addWidget(self.search)

        self.results = QtWidgets.QListView()
        self.results.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        body.addWidget(self.results)

        self.search.installEventFilter(self)
        self.search.setFocus()

    def setup_shortcuts(self):
        down_pressed = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.Key_Enter), self.results)
        down_pressed.activated.connect(self.shift_focus_to_results)

    def shift_focus_to_results(self):
        self.results.setFocus()

    def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent) -> bool:
        if watched == self.search:
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() in (Qt.Key_Down, Qt.Key_Return, Qt.Key_Enter,):
                    self.signals.key_search_down.emit()
                    self.results.setFocus()
                    return False

                
        return super(SearchWindow, self).eventFilter(watched, event)
        
        
