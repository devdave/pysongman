"""

Tree - selected config panel


"""
import sys
from dataclasses import dataclass
import typing

import PySide2
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Qt
DisplayRole = Qt.DisplayRole


from sa_models1 import initialize_db, ParentDir


class ParentTableBridge(QtCore.QAbstractTableModel):

    def rowCount(self, parent:PySide2.QtCore.QModelIndex=...) -> int:
        return ParentDir.query.count()

    def columnCount(self, parent:PySide2.QtCore.QModelIndex=...) -> int:
        return 2

    def headerData(self, section:int, orientation:PySide2.QtCore.Qt.Orientation, role:int=...) -> typing.Any:
        if role == Qt.DisplayRole:
            if section == 0:
                return None
            elif section == 1:
                return "Path"

    def data(self, index:PySide2.QtCore.QModelIndex, role:int=...) -> typing.Any:
        if role == Qt.DisplayRole:
            record = ParentDir.query.limit(1).offset(index.row()).first()  # type: ParentDir
            if index.column() == 0:
                return record.id
            else:
                return record.path

class MasterConfig(QtWidgets.QMainWindow):

    def __init__(self):
        super(MasterConfig, self).__init__()
        self.controllers = {}
        self.folders = {}
        self.subviews = {}


        self.setupUI()

        self.menu_tree.itemClicked.connect(self.on_treeitem_clicked)

    def setupUI(self):

        self.setWindowTitle("Master configuration")

        self.left_side = QtWidgets.QVBoxLayout(self)
        self.body_layout = QtWidgets.QHBoxLayout(self)


        # left side
        self.menu_tree = QtWidgets.QTreeWidget(self)
        self.menu_tree.setMinimumHeight(325)
        self.menu_tree.setMinimumWidth(180)

        self.close_btn = QtWidgets.QPushButton("Close")
        self.left_side.addWidget(self.menu_tree)
        self.left_side.addWidget(self.close_btn)

        # right side
        self.mdi = QtWidgets.QMdiArea()

        #put together
        self.body_layout.addLayout(self.left_side)
        self.body_layout.addWidget(self.mdi)

        # shove it in a frame
        self.frame = QtWidgets.QFrame()
        self.frame.setLayout(self.body_layout)

        self.setCentralWidget(self.frame)

        self.buildTree()

        self.setMinimumSize(600, 400)
        self.setMaximumSize(600, 400)


    def add_controller(self, controller_cls, identifier, label, group_id=None, show = False):
        if group_id is None:
            root = self.menu_tree
        elif group_id in self.folders:
            root = self.folders[group_id]
        else:
            raise Exception(f"{group_id} is not a valid folder id. - options are {self.folders.keys()}")

        self.controllers[identifier] = controller_cls()

        self.folders[identifier] = QtWidgets.QTreeWidgetItem(root, [label])
        self.folders[identifier].setData(2, QtCore.Qt.EditRole, identifier)

        if show is True:
            self.subviews[identifier] = self.mdi.addSubWindow(self.controllers[identifier].view)
            self.show_subview(self.subviews[identifier])


    def buildTree(self):
        self.root_header = QtWidgets.QTreeWidgetItem(["Main config"])

        self.menu_tree.setHeaderItem(self.root_header)

    def on_treeitem_clicked(self, treeItem: QtWidgets.QTreeWidgetItem):
        label = treeItem.text(0)
        identifier = treeItem.text(2)
        print(treeItem, label, identifier)
        controller = self.controllers[identifier]

        if identifier not in self.subviews:
            sub = self.mdi.addSubWindow(controller.view)
            self.subviews[identifier] = sub
        else:
            for subview in self.subviews.values():
                subview.hide()

        self.show_subview(self.subviews[identifier])

    def show_subview(self, sub):


        sub.setWindowFlag(Qt.FramelessWindowHint, True)
        sub.showMaximized()
        sub.show()



class MasterConfigController(QtCore.QObject):

    def __init__(self):
        super(MasterConfigController, self).__init__()
        self.view = MasterConfig()

        self.view.add_controller(MediaConfigController, "media_config", "Media Library", show=True)
        # self.view.add_controller(lambda : MediaConfigController("Second Config"), "media_config2", "Second config")

        self.subviews = {}

        self.connect()

    def connect(self):
        # self.view.menu_tree.itemClicked.connect(self.on_treeitem_clicked)
        self.view.close_btn.clicked.connect(self.on_close_clicked)

    def show(self):
        self.view.show()



    def on_close_clicked(self):
        self.view.close()


class MediaConfigController(QtCore.QObject):
    def __init__(self, optional_title=None):
        self.optional_title = optional_title
        self.view = MediaConfigWidget(optional_title=optional_title)
        self.make_connections()

    def make_connections(self):
        self.view.add_folder.clicked.connect(self.on_click_add_folder)
        self.view.edit_folder.clicked.connect(self.on_click_edit_folder)
        self.view.remove_folder.clicked.connect(self.on_click_remove_folder)
        pass

    def on_click_add_folder(self):
        print("Add Folder", self.optional_title)

    def on_click_edit_folder(self):
        print("Edit folder", self.optional_title)

    def on_click_remove_folder(self):
        print("Remove Folder", self.optional_title)



class MediaConfigWidget(QtWidgets.QWidget):

    def __init__(self, optional_title=None):
        super(MediaConfigWidget, self).__init__()
        self.optional_title = optional_title
        self.setupUI()

    def setupUI(self):

        if self.optional_title is None:
            self.setWindowTitle("Media configuration")
        else:
            self.setWindowTitle(self.optional_title)

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        if self.optional_title is None:
            groupbox = QtWidgets.QGroupBox("Watch folder settings")
        else:
            groupbox = QtWidgets.QGroupBox(self.optional_title)

        layout.addWidget(groupbox)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop)

        groupbox.setLayout(vbox)

        label = QtWidgets.QLabel("New media found in the following folders will automatically be added to the library:")
        label.setWordWrap(True)
        vbox.addWidget(label)

        self.table = QtWidgets.QTableView()
        self.model = ParentTableBridge()

        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table.setColumnHidden(0, True)
        self.table.setMaximumHeight(150)
        self.table.setMaximumWidth(300)

        vbox.addWidget(self.table)

        action_layout = QtWidgets.QHBoxLayout()

        self.add_folder = QtWidgets.QPushButton("Add folder...")
        self.edit_folder = QtWidgets.QPushButton("Edit selected")
        self.remove_folder = QtWidgets.QPushButton("Remove selected")

        action_layout.addWidget(self.add_folder)
        action_layout.addWidget(self.edit_folder)
        action_layout.addWidget(self.remove_folder)

        vbox.addLayout(action_layout)
        vbox.addStretch()













def main():

    db = initialize_db("./pysongman.sqlite3")

    app = QtWidgets.QApplication(sys.argv)

    controller = MasterConfigController()
    controller.show()

    return app.exec_()


if __name__ == '__main__':
    main()