
import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt

from .base import Base




class Table(QtCore.QAbstractTableModel):

    def __init__(self, playlist_obj):
        super(Table, self).__init__()
        self.obj = playlist_obj

    pass


class Domain(Base):
    pass