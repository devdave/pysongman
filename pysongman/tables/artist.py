import typing

from ..models.artist import Artist as ArtistModel
from .base import BaseTable


class ArtistTable(BaseTable):

    def __init__(self, data_map: dict, model: ArtistModel = None):
        super(ArtistTable, self).__init__(data_map, model=ArtistModel)

