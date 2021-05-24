from ..lib.qtd import QtCore
from ..models.album import Album as AlbumModel
from .base import BaseTable

class AlbumTable(BaseTable):

    def __init__(self, data_map):
        super(AlbumTable, self).__init__(data_map, model=AlbumModel)
