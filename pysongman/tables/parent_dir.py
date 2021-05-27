import typing


from pysongman.models.parent_dir import ParentDir


from ..lib.qtd import QtCore, QtWidgets, Qt


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
                return str(record.path)