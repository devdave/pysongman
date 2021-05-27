from pysongman.lib.qtd import QtCore, Qt, QObject
from pysongman.views.library.audio import AudioWindow
from pysongman.tables.album import AlbumTable
from pysongman.tables.artist import ArtistTable


class AudioLibraryController(QObject):

    artist_table: ArtistTable
    album_table: AlbumTable

    def __init__(self):
        super(AudioLibraryController, self).__init__()
        self.view = AudioWindow()

        self.setup_models()


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