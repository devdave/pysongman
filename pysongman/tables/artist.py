import typing

from sqlalchemy.orm import Query

from ..models.artist import Artist as ArtistModel
from .base import BaseTable


class ArtistTable(BaseTable):

    _query: Query

    def __init__(self, data_map: dict, model: ArtistModel = None):
        super(ArtistTable, self).__init__(data_map, model=ArtistModel)
        self._query = ArtistModel.query


    def _get_query(self):
        return self._query
