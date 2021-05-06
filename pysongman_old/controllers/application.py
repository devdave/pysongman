"""
    God module anti-pattern
"""
import pathlib
import logging

from PySide2.QtWidgets import QApplication

from .. import HOME, HERE, CONFIGURED_FLAG, DB_FILE
from ..models import initialize_db
from .player import PlayerController

log = logging.getLogger(__name__)

class Application(QApplication):

    def __init__(self, *args):
        super(Application, self).__init__(*args)

        self.player = None

    def first_startup(self):
        return CONFIGURED_FLAG.exists()

    def set_as_configured(self):
        return CONFIGURED_FLAG.touch(exist_ok=True)

    def nuke_everything(self):
        DB_FILE.unlink(True)
        CONFIGURED_FLAG.unlink(True)




    def startup(self, song_file, nuke_everything=False):

        self.player = PlayerController()
        self.focusChanged.connect(self.on_focus_changed)

        if nuke_everything is True:
            self.nuke_everything()

        if self.first_startup() is False:
            log.info("First startup")
            log.debug("Creating DB @ %s", HOME.as_posix())
            initialize_db(create=True)
            self.set_as_configured()


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
            pass
            # log.debug("Focus changed %s to %s", old, new)
            # self.player.focus()








