
from sqlalchemy.orm import Query

from ..lib.qtd import QtCore

class QueryTable(QtCore.QAbstractTableModel):

    _base_query: Query
    _active_query: Query

    def __init__(self, base_query, data_map):
        self._base_query = base_query
        self._active_query = base_query

        self.dmap = data_map

    @property
    def query(self):
        return self._active_query

    @query.setter
    def query(self, new_query):
        self._active_query = new_query

    @query.deleter
    def query(self):
        self._active_query = self._base_query

    def reset_query(self):
        self._active_query = self._base_query


