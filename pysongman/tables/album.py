from sqlalchemy.orm import Query

from ..lib.qtd import QtCore
from ..models.album import Album as AlbumModel
from .base import BaseTable

class AlbumTable(BaseTable):

    _query: Query

    def __init__(self, data_map):
        super(AlbumTable, self).__init__(data_map, model=AlbumModel)
        self._query = AlbumModel.query

    def _get_query(self):
        return self._query