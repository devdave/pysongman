import logging
from ..lib.qtd import QtCore, Signal, QtWidgets, Qt

from pybass3.pys2_playlist import Pys2Playlist

from ..lib.mdi_controller import MDIController
from ..views.media_window import MediaWindow
from ..controllers.library.audio import AudioLibraryController
from ..tables.artist import ArtistTable
from ..tables.album import AlbumTable

log = logging.getLogger(__name__)


class MediaController(MDIController):

    DEFAULT_VIEW = MediaWindow
    
    def __init__(self):
        super(MediaController, self).__init__()

    def setup_subwindows(self):
        self.add_controller(AudioLibraryController, "local_media", "Audio", show=True)
        log.debug("Subwindows added")

