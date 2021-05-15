import typing

from pysongman import USE_PYSIDE
from pysongman.models.parent_dir import ParentDir


if USE_PYSIDE is True:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtCore import Qt


class ParentTableBridge(QtCore.QAbstractTableModel):

    def rowCount(self, parent: QtCore.QModelIndex=...) -> int:
        return ParentDir.query.count()

    def columnCount(self, parent: QtCore.QModelIndex=...) -> int:
        return 2

    def headerData(self, section:int, orientation: QtCore.Qt.Orientation, role:int=...) -> typing.Any:
        if role == Qt.DisplayRole:
            if section == 0:
                return "ID"
            elif section == 1:
                return "Path"

    def data(self, index: QtCore.QModelIndex, role:int=...) -> typing.Any:
        if role == Qt.DisplayRole:
            record = ParentDir.query.limit(1).offset(index.row()).first()  # type: ParentDir
            if index.column() == 0:
                return record.id
            else:
                return record.path