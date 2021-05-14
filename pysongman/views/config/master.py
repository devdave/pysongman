from pysongman import USE_PYSIDE

import logging

if USE_PYSIDE:
    from PySide2 import QtWidgets, QtCore
    from PySide2.QtCore import Qt

log = logging.getLogger(__name__)

class ConfigMasterWindow(QtWidgets.QMainWindow):

    left_side: QtWidgets.QVBoxLayout
    body_layout: QtWidgets.QHBoxLayout

    menu_tree: QtWidgets.QTreeWidget
    close_button: QtWidgets.QPushButton
    mdi: QtWidgets.QMdiArea

    frame: QtWidgets.QFrame
    
    def __init__(self):
        super(ConfigMasterWindow, self).__init__()

        self.controllers = {}
        self.folders = {}
        self.subviews = {}

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

    def add_controller(self, controller_cls, identifier, label, group_id = None, show = False):
        log.debug("Adding controller %s(%s) to %s", label, identifier, group_id)

        if group_id is None:
            root = self.menu_tree
        elif group_id in self.folders:
            root = self.folders[group_id]
        else:
            raise ValueError(f"{group_id!r} is not a valid folder. options are {self.folders.keys()!r}")

        self.controllers[identifier] = controller_cls()

        self.folders[identifier] = QtWidgets.QTreeWidgetItem(root, [label])
        self.folders[identifier].setData(2, QtCore.Qt.EditRole, identifier)

        if show is True:
            self.subviews[identifier] = self.mdi.addSubWindow(self.controllers[identifier].view)
            self.show_subview(self.subviews[identifier])

    def show_subview(self, sub: QtWidgets.QWidget):

        sub.setWindowFlag(Qt.FramelessWindowHint, True)
        sub.showMaximized()
        sub.show()