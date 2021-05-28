import typing

from ..models.base import Base as BaseModel
from ..lib.qtd import QtCore, QtWidgets, Qt


class BaseTable(QtCore.QAbstractTableModel):

    def __init__(self, data_map: dict, model: BaseModel = None ):
        super(BaseTable, self).__init__()

        self.data_map = data_map
        self.model = model

        self.column_names = []
        self.fetchers = []
        for column_name, config in self.data_map.items():
            self.column_names.append(column_name)
            self.fetchers.append(config['fetcher'])

    def headerData(self, section:int, orientation: QtCore.Qt.Orientation, role:int=...) -> typing.Any:
        if role == Qt.DisplayRole:
            return "RID" if section == 0 else self.column_names[section-1]

    def columnCount(self, parent:QtCore.QModelIndex=...) -> int:
        return len(self.column_names) + 1

    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        return self._get_query().count()

    def data(self, index:QtCore.QModelIndex, role:int=...) -> typing.Any:
        adj_col = index.column()-1
        if role == Qt.DisplayRole:
            record = self._get_query().offset(index.row()).first()
            if record:
                return record.id if index.column() == 0 else self.fetchers[adj_col](record)

    def _get_query(self):
        raise NotImplementedError("Missing _get_query method for subclass %s" % self.__class__.__name__)