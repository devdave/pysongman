from pysongman import USE_PYSIDE

import logging

if USE_PYSIDE:
    from PySide2 import QtWidgets, QtCore
    from PySide2.QtCore import Qt

log = logging.getLogger(__name__)

class ConfigMasterWindowSignals(QtCore.QObject):
    on_close = QtCore.Signal()



class ConfigMasterWindow(QtWidgets.QMainWindow):

    signals: ConfigMasterWindowSignals

    left_side: QtWidgets.QVBoxLayout
    body_layout: QtWidgets.QHBoxLayout

    menu_tree: QtWidgets.QTreeWidget
    close_button: QtWidgets.QPushButton
    mdi: QtWidgets.QMdiArea

    frame: QtWidgets.QFrame
    
    def __init__(self):
        super(ConfigMasterWindow, self).__init__()
        self.signals = ConfigMasterWindowSignals()
        self.setup_ui()

        log.debug("Config Master Window initialized")


    def setup_ui(self):

        self.setWindowTitle("Master Configuration")

        self.left_side = QtWidgets.QVBoxLayout(self)
        self.body_layout = QtWidgets.QHBoxLayout(self)

        #left side
        self.menu_tree = QtWidgets.QTreeWidget(self)
        self.menu_tree.setMinimumSize(180, 325)
        self.close_button = QtWidgets.QPushButton("Close")

        self.left_side.addWidget(self.menu_tree)
        self.left_side.addWidget(self.close_button)

        #right side
        self.mdi = QtWidgets.QMdiArea()

        #put together
        self.body_layout.addLayout(self.left_side)
        self.body_layout.addWidget(self.mdi)

        #show it in a frame
        self.frame = QtWidgets.QFrame()
        self.frame.setLayout(self.body_layout)

        self.setCentralWidget(self.frame)

        self.build_tree()

        self.setMinimumSize(600, 400)
        self.setMaximumSize(600, 400)


    def build_tree(self):

        self.root_header = QtWidgets.QTreeWidgetItem(["Main Config"])
        self.menu_tree.setHeaderItem(self.root_header)


    def closeEvent(self, event):
        self.signals.on_close.emit()
        event.accept()