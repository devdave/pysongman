from pysongman import USE_PYSIDE
from pysongman.views.config.master import ConfigMasterWindow

if USE_PYSIDE:
    from PySide2 import QtCore, QtWidgets

class ConfigMasterController(QtCore.QObject):


    def __init__(self):
        super(ConfigMasterController, self).__init__()

        self.view = ConfigMasterWindow()

    def setup_connections(self):
        self.view.menu_tree.itemClicked.connect(self.on_menu_tree_item_clicked)

    def hide(self):
        self.view.hide()

    def show(self):
        self.view.show()

    def activate(self):
        self.view.activateWindow()

    def on_menu_tree_item_clicked(self, treeItem: QtWidgets.QTreeWidgetItem):
        pass