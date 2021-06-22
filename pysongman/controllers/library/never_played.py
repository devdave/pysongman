
from pysongman.lib.qtd import QtWidgets, QObject, Signal
from pysongman.tables.query import QueryTable
from pysongman.models.song import Song as SongModel
from pysongman.views.library.never_played import NeverPlayed


class NeverPlayedSignals(QObject):
    new_playlist = Signal(list)


class NeverPlayedLibraryController(QObject):

    model: QueryTable
    view: NeverPlayed

    def __init__(self):
        super(NeverPlayedLibraryController, self).__init__()
        self.signals = NeverPlayedSignals()
        self.view = NeverPlayed()
        self.setup_model()
        self.setup_connections()

    def setup_model(self):
        query = SongModel.query.filter(SongModel.play_count == 0)
        self.model = QueryTable(query,
                                     {
                                         "Play count": dict(fetcher=lambda r: r.play_count),
                                         "Artist": dict(fetcher=lambda r: r.artist.name),
                                         "Title": dict(fetcher=lambda r: r.title),
                                         "Album": dict(fetcher=lambda r: r.album),
                                         "Length": dict(fetcher=lambda r: r.time)
                                     },
                                     show_all_row=False
                                     )

        self.view.table.setModel(self.model)
        self.view.table.horizontalHeader().hideSection(0)
        self.view.table.verticalHeader().hide()

    def reload(self):
        self.model.beginResetModel()
        self.model.endResetModel()

    def setup_connections(self):
        pass