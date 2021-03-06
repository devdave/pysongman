import logging

from pysongman.lib.qtd import QtCore, Qt

from ..tables.playlist import PlaylistTableModel

log = logging.getLogger(__name__)


class SearchFilterProxy(QtCore.QSortFilterProxyModel):

    filter_string: QtCore.QRegExp
    sourceModel: PlaylistTableModel

    def __init__(self, parent_model):
        super(SearchFilterProxy, self).__init__(parent_model)
        self.filter_string = None
        self._filters = []

    def setFilterString(self, text):
        logging.debug("setFilterString %s", text)
        if text is None:
            self.filter_string = None
            self._filters = []

        elif isinstance(text, str):

            if text.strip() == "":
                self.filter_string = None
            else:
                self.filter_string = text
                self._filters = [QtCore.QRegExp(span, cs=Qt.CaseInsensitive, syntax=QtCore.QRegExp.Wildcard)
                                 for span in text.split(" ")]
                log.debug("Created %d filters against %s", len(self._filters), text)

        self.invalidateFilter()

    def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:
        song = self.sourceModel().getSong(source_row)

        # should_free = True if song.handle is None else False

        try:
            if self.filter_string is None:
                return False

            elif self.filter_string:
                results = []
                for test in self._filters:

                    if test.indexIn(song.title) != -1:
                        results.append(True)
                        break
                    elif test.indexIn(song.file_path.as_posix()) != -1:
                        results.append(True)
                        break
                    else:
                        results.append(False)

                return all(results)
        finally:
            pass
            # if should_free:
            #     song.free_stream()

        return False


