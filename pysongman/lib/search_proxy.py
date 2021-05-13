import logging

from .. import USE_PYSIDE


if USE_PYSIDE is True:
    from PySide2 import QtCore
    from PySide2.QtCore import Qt

from ..tables.playlist import PlaylistTableModel

log = logging.getLogger(__name__)

class SearchFilterProxy(QtCore.QSortFilterProxyModel):

    filter_string: QtCore.QRegExp
    sourceModel: PlaylistTableModel

    def __init__(self, parent_model):
        super(SearchFilterProxy, self).__init__(parent_model)
        self.filter_string = None

    def setFilterString(self, text):
        logging.debug("setFilterString %s", text)
        if text is None:
            self.filter_string = None

        elif isinstance(text, str) and text.strip() == "":
            self.filter_string = None

        else:
            self.filter_string = QtCore.QRegExp(text, cs=Qt.CaseInsensitive, syntax=QtCore.QRegExp.Wildcard)

        self.invalidateFilter()

    def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:
        model = self.sourceModel()
        song = model.getSong(source_row)
        should_free = True if song.handle is None else False

        if self.filter_string is None:
            return True

        elif self.filter_string:

            if self.filter_string.indexIn(song.title) != -1:
                return True
            elif self.filter_string.indexIn(song.file_path.as_posix()) != -1:
                return True

        if should_free:
            song.free_stream()

        return False


