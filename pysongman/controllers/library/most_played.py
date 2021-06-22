
from pysongman.lib.qtd import QtWidgets, QObject, Signal
from pysongman.tables.query import QueryTable
from pysongman.models.song import Song as SongModel
from pysongman.views.library.most_played import MostPlayed


class MPLControllerSignals(QObject):
    new_playlist = Signal(list)


class MostPlayedLibraryController(QObject):

    most_model: QueryTable
    view: MostPlayed

    def __init__(self):
        super(MostPlayedLibraryController, self).__init__()
        self.signals = MPLControllerSignals()
        self.view = MostPlayed()
        self.setup_model()
        self.setup_connections()

    def setup_model(self):
        query = SongModel.query.filter(SongModel.play_count > 1)
        self.most_model = QueryTable(query,
                                     {
                                         "Play count": dict(fetcher=lambda r:r.play_count),
                                         "Artist": dict(fetcher=lambda r: r.artist.name),
                                         "Title": dict(fetcher=lambda r: r.title),
                                         "Album": dict(fetcher=lambda r: r.album),
                                         "Length": dict(fetcher=lambda r: r.time)
                                     },
                                     show_all_row=False
                                     )

        self.view.table.setModel(self.most_model)
        self.view.table.horizontalHeader().hideSection(0)

    def reload(self):
        self.most_model.beginResetModel()
        self.most_model.endResetModel()

    def setup_connections(self):
        pass