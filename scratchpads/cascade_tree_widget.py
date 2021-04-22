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



class MasterConfigController(QtCore.QObject):

    def __init__(self):
        super(MasterConfigController, self).__init__()
        self.view = MasterConfig()

        self.subviews = {}

        self.connect()

    def connect(self):
        self.view.menu_tree.itemClicked.connect(self.on_treeitem_clicked)


    def on_treeitem_clicked(self, treeItem: QtWidgets.QTreeWidgetItem):
        label = treeItem.text(0)
        identifier = treeItem.text(2)
        print(treeItem, label, identifier)
        mconfig = MediaConfigWidget()
        mconfig.setWindowTitle("Media Config")
        if identifier not in self.subviews:
            sub = self.view.mdi.addSubWindow(mconfig)
            sub.setWindowFlag(Qt.FramelessWindowHint, True)
            sub.showMaximized()
            sub.show()
            self.subviews[identifier] = sub
        else:
            sub = self.subviews[identifier]
            sub.show()
            sub.showMaximized()


class MediaConfigWidget(QtWidgets.QWidget):

    def __init__(self):
        super(MediaConfigWidget, self).__init__()
        self.setupUI()

    def setupUI(self):

        self.setWindowTitle("Media configuration")

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        groupbox = QtWidgets.QGroupBox("Watch folder settings")
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





class MasterConfig(QtWidgets.QMainWindow):

    def __init__(self):
        super(MasterConfig, self).__init__()
        self.setupUI()

    def setupUI(self):

        self.setWindowTitle("Master configuration")

        self.left_side = QtWidgets.QVBoxLayout(self)
        self.body_layout = QtWidgets.QHBoxLayout(self)


        # left side
        self.menu_tree = QtWidgets.QTreeWidget(self)
        self.menu_tree.setMinimumHeight(450)
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




    def buildTree(self):
        self.root_header = QtWidgets.QTreeWidgetItem(["Main config"])
        # root.setText(1, "Configuration")
        self.menu_tree.setHeaderItem(self.root_header)

        self.media_fldr = QtWidgets.QTreeWidgetItem(self.menu_tree, ["Media library"])
        self.media_fldr.setData(2, QtCore.Qt.EditRole, "media_lib")







def main():

    db = initialize_db("./pysongman.sqlite3")

    app = QtWidgets.QApplication(sys.argv)

    controller = MasterConfigController()
    controller.view.show()

    return app.exec_()


if __name__ == '__main__':
    main()