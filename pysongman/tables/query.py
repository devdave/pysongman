import typing

from sqlalchemy.orm import Query

from ..lib.qtd import QtCore, Qt

class QueryTable(QtCore.QAbstractTableModel):

    _base_query: Query
    _active_query: Query

    def __init__(self, base_query, data_map, show_all_row=True):
        super(QueryTable, self).__init__()

        self._base_query = base_query
        self._active_query = base_query

        self._show_all = show_all_row
        self.data_map = data_map
        self.column_names = []
        self.fetchers = []
        self.filters = {}
        for column_name, config in self.data_map.items():
            self.column_names.append(column_name)
            self.fetchers.append(config['fetcher'])


    def clear_filters(self):
        self.filters = {}
        self.sa_query = self.base_query()
        return self

    def set_filter_by(self, **kwargs):
        self.filters.update(kwargs)
        self.sa_query = self.base_query().filter_by(**self.filters)
        return self

    def clear_filter_by(self, key_name):
        if key_name in self.filters:
            del self.filters[key_name]
            self.sa_query = self.base_query().filter_by(**self.filters)

    def set_filter(self, *expression):
        self.sa_query = self.base_query().filter(*expression)

    @property
    def sa_query(self):
        return self._active_query

    @sa_query.setter
    def sa_query(self, new_query):
        self._active_query = new_query

    @sa_query.deleter
    def sa_query(self):
        self._active_query = self._base_query

    def base_query(self):
        return self._base_query

    def headerData(self, section:int, orientation: QtCore.Qt.Orientation, role:int=...) -> typing.Any:
        if role == Qt.DisplayRole:
            return "RID" if section == 0 else self.column_names[section-1]

    def columnCount(self, parent:QtCore.QModelIndex=...) -> int:
        return len(self.column_names) + 1

    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        return self.sa_query.count()+1 if self._show_all is True else self.sa_query.count()

    def data(self, index:QtCore.QModelIndex, role:int=...) -> typing.Any:

        if self._show_all is True and (index.row() == 0 and role == Qt.DisplayRole):
            if index.column() == 0:
                return -1
            else:
                return "All"
        else:
            adj_col = index.column()-1
            adj_row = index.row()-1 if self._show_all else index.row()
            if role == Qt.DisplayRole:
                record = self.sa_query.offset(adj_row).first()
                if record:
                    return record.id if index.column() == 0 else self.fetchers[adj_col](record)