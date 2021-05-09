from .. import USE_PYSIDE
import typing as T
import pathlib

if USE_PYSIDE:
    import PySide2
    from PySide2.QtGui import QPixmap
    from PySide2 import QtCore
    from PySide2.QtCore import Qt
    from PySide2 import QtWidgets
    from PySide2 import QtMultimedia

    from pybass3.pys2_playlist import Pys2Playlist

from .. import ICON_DIR
from .. import CSS_DIR
from ..tables.playlist import PlaylistTableModel


class AlignLeftDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option:PySide2.QtWidgets.QStyleOptionViewItem, index:PySide2.QtCore.QModelIndex) -> None:
        super(AlignLeftDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignLeft


class PlaylistWindow(QtWidgets.QWidget):

    def __init__(self):
        super(PlaylistWindow, self).__init__()

        self.table = None
        self.body = None

        self.setup_UI()


    def setup_UI(self):
        self.setWindowTitle("Playlist editor")
        self.body = QtWidgets.QVBoxLayout(self)

        self.table = QtWidgets.QTableView()

        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table.verticalHeader().hide()

        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        # Ever get the feeling I REALLY want this to expand?
        alignleft = AlignLeftDelegate(self.table)
        self.table.setItemDelegateForColumn(1, alignleft)


        self.body.addWidget(self.table)
        self.body.setStretch(0, 1)
        self.setMinimumWidth(725)
        self.setMaximumWidth(750)





