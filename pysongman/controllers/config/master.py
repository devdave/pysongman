import logging

import pysongman
from pysongman.views.config.master import ConfigMasterWindow
from pysongman.controllers.config.debug import ConfigDebugController
from .media import ConfigMediaController

if pysongman.USE_PYSIDE:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtCore import Qt

log = logging.getLogger(__name__)

class ConfigMasterController(QtCore.QObject):

    closed = QtCore.Signal()

    def __init__(self):
        super(ConfigMasterController, self).__init__()

        self.view = ConfigMasterWindow()
        self.controllers = {}
        self.folders = {}
        self.subviews = {}

        log.debug("Master Config controller initialized")

        self.setup_connections()
        self.setup_subwindows()

    def setup_connections(self):
        self.view.menu_tree.itemClicked.connect(self.on_menu_tree_item_clicked)
        self.view.close_button.clicked.connect(self.on_close)
        log.debug("Connections setup")

    def setup_subwindows(self):
        self.add_controller(ConfigMediaController, "local_media", "Local Media config", show=True)
        if pysongman.App and pysongman.App.debug_enabled is True:
            self.add_controller(ConfigDebugController, "debug", "Debug data", show=False)

        log.debug("Subwindows added")

    def add_controller(self, controller_cls, identifier, label, group_id = None, show = False):
        log.debug("Adding controller %s(%s) to %s", label, identifier, group_id)

        if group_id is None:
            root = self.view.menu_tree
        elif group_id in self.folders:
            root = self.folders[group_id]
        else:
            raise ValueError(f"{group_id!r} is not a valid folder. options are {self.folders.keys()!r}")

        self.controllers[identifier] = controller_cls()

        self.folders[identifier] = QtWidgets.QTreeWidgetItem(root, [label])
        self.folders[identifier].setData(2, QtCore.Qt.EditRole, identifier)

        if show is True:
            self.subviews[identifier] = self.view.mdi.addSubWindow(self.controllers[identifier].view)
            self.show_subview(self.subviews[identifier])

    def show_subview(self, sub_window: QtWidgets.QWidget):
        sub_window.setWindowFlag(Qt.FramelessWindowHint, True)
        sub_window.showMaximized()
        sub_window.show()


    def hide(self):
        self.view.hide()

    def show(self):
        self.view.show()

    def activate(self):
        self.view.activateWindow()

    def on_menu_tree_item_clicked(self, treeItem: QtWidgets.QTreeWidgetItem):
        label = treeItem.text(0)
        identifier = treeItem.text(2)
