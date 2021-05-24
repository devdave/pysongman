import logging

import pysongman
from pysongman.views.config_window import ConfigWindow
from pysongman.controllers.config.debug import ConfigDebugController
from .media import ConfigMediaController

from pysongman.lib.qtd import QtCore, QtWidgets, Qt


log = logging.getLogger(__name__)


class ConfigMasterControllerSignals(QtCore.QObject):
    closed = QtCore.Signal()


class ConfigMasterController(QtCore.QObject):

    signals: ConfigMasterControllerSignals

    def __init__(self):
        super(ConfigMasterController, self).__init__()

        self.signals = ConfigMasterControllerSignals()
        self.view = ConfigWindow()
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
        log.debug("Config menu %s(%s) was requested", label, identifier)

        controller = self.controllers[identifier]

        if identifier not in self.subviews:
            sub = self.view.mdi.addSubWindow(controller.view)
            self.subviews[identifier] = sub
        else:
            for subview in self.subviews.values():
                subview.hide()

        sub.setWindowFlag(Qt.FramelessWindowHint, True)
        sub.showMaximized()
        sub.show()


    def on_close(self):
        self.signals.closed.emit()