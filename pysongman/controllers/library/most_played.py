
from pysongman.lib.qtd import QtWidgets, QObject
from pysongman.models.song import Song as SongModel
from pysongman.views.library.most_played import MostPlayed


class MPLControllerSignals(QObject):
    pass


class MostPlayedLibraryController(QObject):

    def __init__(self):
        super(MostPlayedLibraryController, self).__init__()
        self.signals = MPLControllerSignals()
        self.view = MostPlayed()

    def setup_model(self):
        query = SongModel.query.filter(SongModel.play_count > 1)


    def setup_connections(self):
        pass