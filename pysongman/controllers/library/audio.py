import logging

from sqlalchemy import func

from pysongman.lib.qtd import QtCore, Qt, QObject, Signal, QSortFilterProxyModel
from pysongman.views.library.audio import AudioWindow

from pysongman.tables.query import QueryTable
from pysongman.models.artist import Artist as ArtistModel
from pysongman.models.album import Album as AlbumModel
from pysongman.models.song import Song as SongModel


log = logging.getLogger(__name__)

class AudioLibrarySignals(QObject):
    # provides a list of song record id's
    new_playlist = Signal(list)

class AudioLibraryController(QObject):

    artist_model: QueryTable
    album_model: QueryTable
    songs_model: QueryTable

    def __init__(self):
        super(AudioLibraryController, self).__init__()
        log.debug("%s initialized", self.__class__.__name__)
        self.signals = AudioLibrarySignals()
        self.view = AudioWindow()

        self.setup_models()
        self.setup_connections()


    def setup_models(self):
        self.artist_model = QueryTable(
            ArtistModel.query,
            {
                "name": dict(
                    fetcher=lambda r: r.name
                ),
                "Albums": dict(
                    fetcher=lambda r: len(r.albums)
                ),
                "Songs": dict(fetcher=lambda r: len(r.songs))
            }
        )
        self.album_model = QueryTable(
            AlbumModel.query,
            {
                "name": dict(fetcher=lambda r: r.name),
                "songs": dict(fetcher=lambda r: len(r.songs))
            }
        )

        self.songs_model = QueryTable(
            SongModel.query,
            {
                "artist": dict(fetcher=lambda r: r.artist.name),
                "name": dict(fetcher=lambda r: r.title),
                "album": dict(fetcher=lambda r: r.album.name),
                "length": dict(fetcher=lambda r: r.time)
            },
            show_all_row=False
        )

        self.view.artist_table.setModel(self.artist_model)
        self.view.album_table.setModel(self.album_model)
        self.view.songs_table.setModel(self.songs_model)

        log.debug("Models & Tables setup")

        # These reappear once the model is changed/set
        self.view.artist_table.horizontalHeader().hideSection(0)
        self.view.album_table.horizontalHeader().hideSection(0)
        self.view.songs_table.horizontalHeader().hideSection(0)


    def reload(self):
        self.artist_model.beginResetModel()
        self.album_model.beginResetModel()
        self.songs_model.beginResetModel()

        self.album_model.clear_filters()
        self.artist_model.clear_filters()
        self.songs_model.clear_filters()

        self.album_model.endResetModel()
        self.artist_model.endResetModel()
        self.songs_model.endResetModel()

    def setup_connections(self):
        self.view.artist_table.clicked.connect(self.on_artist_clicked)
        self.view.album_table.clicked.connect(self.on_album_clicked)

        self.view.artist_table.doubleClicked.connect(self.on_anything_doubleclicked)
        self.view.album_table.doubleClicked.connect(self.on_anything_doubleclicked)
        self.view.songs_table.doubleClicked.connect(self.on_anything_doubleclicked)

        self.view.clear_button.clicked.connect(self.do_clear)

        self.view.search_input.textChanged.connect(self.handle_search)


    def handle_search(self, value):
        self.do_clear()
        self.songs_model.beginResetModel()
        self.songs_model.set_filter(SongModel.title.ilike(f"%{value}%"))
        self.songs_model.endResetModel()


    def on_artist_clicked(self):
        log.debug("Artist table clicked")
        idx = self.view.artist_table.selectionModel().selection().indexes()[0]
        artist_id = self.artist_model.index(idx.row(), 0).data(Qt.DisplayRole)

        if artist_id == -1:
            self.album_model.clear_filters()
            self.songs_model.clear_filters()
        else:
            self.album_model.clear_filters().set_filter_by(artist_id=artist_id)
            self.songs_model.clear_filters().set_filter_by(artist_id=artist_id)

        self.album_model.beginResetModel()
        self.songs_model.beginResetModel()
        self.album_model.endResetModel()
        self.songs_model.endResetModel()

    def on_album_clicked(self):

        idx = self.view.album_table.selectionModel().selection().indexes()[0]
        album_id = self.album_model.index(idx.row(), 0).data(Qt.DisplayRole)

        if album_id == -1:
            self.songs_model.clear_filter_by("album_id")
        else:
            self.songs_model.set_filter_by(album_id=album_id)

        self.songs_model.beginResetModel()
        self.songs_model.endResetModel()



    def on_anything_doubleclicked(self):
        if self.songs_model.sa_query.count() > 0:
            log.debug("Would emit %d songs", self.songs_model.sa_query.count())
            song_ids = []
            for record in self.songs_model.sa_query:  # type: SongModel
                song_ids.append(record.id)

            self.signals.new_playlist.emit(song_ids)


    def do_clear(self):
        self.artist_model.beginResetModel()
        self.album_model.beginResetModel()
        self.songs_model.beginResetModel()

        self.artist_model.clear_filters()
        self.album_model.clear_filters()
        self.songs_model.clear_filters()

        self.artist_model.endResetModel()
        self.album_model.endResetModel()
        self.songs_model.endResetModel()