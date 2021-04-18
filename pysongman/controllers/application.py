"""
    God module anti-pattern
"""
import pathlib
import logging

from PySide2.QtWidgets import QApplication

from .. import HOME, HERE
from ..models import initialize_db
from .player import PlayerController

log = logging.getLogger(__name__)

class Application(QApplication):

    def __init__(self, *args, song_file=None):
        super(Application, self).__init__()

        self.song_file = song_file
        self.player = PlayerController()

        self.focusChanged.connect(self.on_focus_changed)

    def first_startup(self):
        return (HOME / "started.txt").exists()

    def startup(self, song_file):

        if self.first_startup() is False:
            log.info("First startup")
            log.debug("Creating DB @ %s", HOME.as_posix())
            initialize_db(create=True)


        if song_file is not None:

            song_file = pathlib.Path(song_file)
            if song_file.is_file():
                log.debug("Adding song %s", song_file)
                self.player.add_song(song_file)
            elif song_file.is_dir():
                log.debug("Adding directory to play %s", song_file)
                self.player.add_directory(song_file)

            self.player.show()
            self.player.play()

    def on_focus_changed(self, old, new):
        if old is None:
            self.player.focus()


        log.debug("Focus changed %s to %s", old, new)



