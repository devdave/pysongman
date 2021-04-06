import typing as T
import pathlib

import PySide2
from PySide2.QtGui import QPixmap
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets
from PySide2 import QtMultimedia

from .. import ICON_DIR
from .. import CSS_DIR


class PlaylistWindow(QtWidgets.QWidget):

    def __init__(self):
        super(PlaylistWindow, self).__init__()

    def setupUI(self):
        self.label = QtWidgets.QLabel("Hello world")
        self.addWidget(self.label)