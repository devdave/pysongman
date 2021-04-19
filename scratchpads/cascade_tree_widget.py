"""

Tree - selected config panel


"""
import sys

import PySide2
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Qt

class Master(QtWidgets.QMainWindow):

    def __init__(self):
        super(Master, self).__init__()
        self.setupUI()

    def setupUI(self):

        self.left_side = QtWidgets.QVBoxLayout()
        self.body_layout = QtWidgets.QHBoxLayout()


        # left side
        self.menu_tree = QtWidgets.QTreeWidget()
        self.menu_tree.setMinimumHeight(450)

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






def main():
    app = QtWidgets.QApplication(sys.argv)

    window = Master()
    window.show()

    return app.exec_()


if __name__ == '__main__':
    main()