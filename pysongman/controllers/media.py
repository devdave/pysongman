import logging
from ..lib.qtd import QtCore, Signal, QtWidgets, Qt, Slot

from pybass3.pys2_playlist import Pys2Playlist

from ..lib.mdi_controller import MDIController
from ..views.media_window import MediaWindow
from ..controllers.library.audio import AudioLibraryController

log = logging.getLogger(__name__)

class MediaSignals(QtCore.QObject):
    new_playlist = Signal(list)

class MediaController(MDIController):

    DEFAULT_VIEW = MediaWindow

    signals: MediaSignals

    def __init__(self):
        super(MediaController, self).__init__()
        self.signals = MediaSignals()
        log.debug("%s initialized", self.__class__.__name__)

    def setup_subwindows(self):
        audio_controller = AudioLibraryController()
        audio_controller.signals.new_playlist.connect(self.handle_new_playlist)

        self.add_controller(audio_controller, "local_media", "Audio", show=True)
        log.debug("Subwindow(s) added")


    @Slot(list)
    def handle_new_playlist(self, song_ids):
        # Relay upward
        log.debug("Relaying %d songs", len(song_ids))
        self.signals.new_playlist.emit(song_ids)




