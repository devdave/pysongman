"""
    God module anti-pattern
"""
import pathlib
import logging

from PySide2.QtWidgets import QApplication

from .player import PlayerController

log = logging.getLogger(__name__)

class Application(QApplication):

    def __init__(self, *args, song_file=None):
        super(Application, self).__init__()

        self.song_file = song_file

    def startup(self, song_file):
        self.player = PlayerController()

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


