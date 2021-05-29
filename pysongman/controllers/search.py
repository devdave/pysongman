from .. import USE_PYSIDE

import logging

from ..lib.qtd import QtCore, QtGui, Qt

from pybass3.pys2_playlist import Pys2Playlist

from ..views.search_window import SearchWindow
from ..lib.search_proxy import SearchFilterProxy

log = logging.getLogger(__name__)

class SearchController(QtCore.QObject):

    pl_obj: Pys2Playlist

    def __init__(self, playlist_table, playlist_obj):
        super(SearchController, self).__init__()
        self.pl_table = playlist_table
        self.pl_obj = playlist_obj

        self.view = SearchWindow()

        self.proxy_model = SearchFilterProxy(self.view)
        self.proxy_model.setSourceModel(self.pl_table)

        self.view.results.setModel(self.proxy_model)
        self.setup()

    def setup(self):

        self.view.results.setModel(self.proxy_model)
        self.view.results.setModelColumn(3)

        self.view.results.installEventFilter(self)

        self.setup_connections()

    def setup_connections(self):
        self.view.search.textChanged.connect(self.on_search_edited)

        self.view.search.returnPressed.connect(self.on_search_returned)

        self.view.results.clicked.connect(lambda : log.debug("Clicked"))
        self.view.results.doubleClicked.connect(self.on_search_double_clicked)

    def setup_shortcuts(self):
        pass

    def on_search_double_clicked(self):
        selected = self.view.results.selectionModel().selection().value(0).indexes()[0]
        row = selected.row()
        pid = self.proxy_model.index(row, 0)
        data = self.proxy_model.itemData(pid)
        song_id = data[Qt.DisplayRole]
        self.pl_obj.play_song_by_id(song_id)
        self.view.search.setText("")
        self.view.hide()
        self.proxy_model.setFilterString(None)
        debug = 1

    def on_search_edited(self, text):
        if len(text) >= 3:
            self.proxy_model.setFilterString(text)

    def on_search_returned(self):
        log.debug("Play first entry if it exists")
        if self.proxy_model.rowCount() > 0:
            pid = self.proxy_model.index(0,0)
            data = self.proxy_model.itemData(pid)
            song_id = data[0]
            log.debug("Play SID %s", song_id)
            self.pl_obj.play_song_by_id(song_id)

            self.view.search.setText("")
            self.view.hide()
            self.proxy_model.setFilterString(None)

        else:
            log.debug("Nothing to play")

    def show(self):
        self.view.show()
        self.view.search.setFocus()

    def hide(self):
        self.view.hide()

    def activate(self):
        self.view.activateWindow()

    def do_play_selected_result(self):
        selected = self.view.results.selectionModel().selection()

        try:
            pid = selected.indexes()[0]
            row_num = pid.row()
            pid = self.proxy_model.index(row_num, 0)
            data = self.proxy_model.itemData(pid)
            song_id = data[Qt.DisplayRole]
            self.pl_obj.play_song_by_id(song_id)
            self.view.search.setText("")
            self.view.hide()
            self.proxy_model.setFilterString(None)
        except IndexError:
            log.debug("Index error when trying to find index")
            pass


    def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent) -> bool:
        if watched is self.view.results and event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.do_play_selected_result()
                
        return super(SearchController, self).eventFilter(watched, event)