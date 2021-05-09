from pathlib import Path

from .. import USE_PYSIDE

if USE_PYSIDE:
    from pybass3.pys2_playlist import Pys2Playlist
    from PySide2.QtWidgets import QApplication


from ..controllers.player import PlayerControl


class Application(QApplication):

    def __init__(self, song_path: list = None, nuke_everything: bool = False):
        super(Application, self).__init__()
        self.song_path = song_path
        self.nuke_everything = nuke_everything

        self.playlist = Pys2Playlist()
        self.plc = PlayerControl(self.playlist)

    def startup(self):
        self.playlist_control.show()
        self.player_control.show()

        if self.song_path is not None:
            if isinstance(self.song_path, list) is False:
                raise ValueError(f"Expected song_path to be a list but got {type(self.song_path)} instead")

            for element in self.song_path:
                file_dir = Path(element)
                if file_dir.is_dir():
                    self.playlist.add_directory(file_dir)
                elif file_dir.is_file():
                    self.playlist.add_song(file_dir)

            if len(self.playlist) > 0:
                self.playlist.play()