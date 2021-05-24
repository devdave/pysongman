from .. import USE_PYSIDE


from ..lib.qtd import QtCore, Signal

from pybass3.pys2_playlist import Pys2Playlist

from ..views.media_window import MediaWindow

from ..tables.artist import ArtistTable
from ..tables.album import AlbumTable


class MediaControllerSignals(QtCore.QObject):
    show_config = Signal()


class MediaController(QtCore.QObject):

    signals: MediaControllerSignals

    def __init__(self, playlist: Pys2Playlist):
        super(MediaController, self).__init__()
        self.signals = MediaControllerSignals()

        self.playlist = playlist
        self.view = MediaWindow()

        self.setup_connections()
        self.setup_models()

    def setup_connections(self):
        self.view.act_lib_config.triggered.connect(lambda : self.signals.show_config.emit())
        pass

    def setup_models(self):
        self.artist_table = ArtistTable(
            {
                "name": dict(fetcher=lambda r: r.name),
                "Albums": dict(fetcher=lambda r: r.albums.count()),
                "Songs": dict(fetcher=lambda r: len(r.artists))

            }
        )
        self.album_table = AlbumTable(
            {
                "name": dict(fetcher=lambda r: r.name),
                "songs": dict(fetcher=lambda r: len(r.songs))
            }
        )

        self.view.artist_table.setModel(self.artist_table)
        self.view.album_table.setModel(self.album_table)

    def show(self):
        self.view.show()

    def hide(self):
        self.view.hide()

    def activate(self):
        self.view.activateWindow()

