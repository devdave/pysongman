"""

Tree - selected config panel


"""
import sys

import PySide2
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Qt

class Controller(QtCore.QObject):

    def __init__(self):
        super(Controller, self).__init__()
        self.view = Master()

    def on_folder_click(self, treeitem):
        print(treeitem)


class Master(QtWidgets.QMainWindow):

    def __init__(self):
        super(Master, self).__init__()
        self.setupUI()

    def setupUI(self):

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


    def buildTree(self):
        self.root_header = QtWidgets.QTreeWidgetItem(["Main config"])
        # root.setText(1, "Configuration")
        self.menu_tree.setHeaderItem(self.root_header)

        self.media_fldr = QtWidgets.QTreeWidgetItem(self.menu_tree, ["Media library"])
        self.media_fldr.setData(2, QtCore.Qt.EditRole, "media_lib")







def main():
    app = QtWidgets.QApplication(sys.argv)

    controller = Controller()
    controller.view.show()

    return app.exec_()


if __name__ == '__main__':
    main()