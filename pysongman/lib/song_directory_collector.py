import logging
import pathlib

import pysongman

if pysongman.USE_PYSIDE is True:
    from .qtd import QtCore, Qt, Signal, Slot

    from pybass3.pys2_song import Pys2Song as Song


    Signal = QtCore.Signal
    Slot = QtCore.Slot

from pybass3 import BassException



log = logging.getLogger(__name__)

song_path = str
song_tags = dict
song_len_seconds = float
song_len_bytes = int


class SongDirectoryCollectorSignals(QtCore.QObject):
    song_found = Signal(song_path, song_tags, song_len_seconds, song_len_bytes)
    work_complete = Signal()
    song_errored = Signal(song_path)

    def emit_found_song(self, song: Song):
        self.song_found.emit(song.file_path.as_posix(), song.tags, song.duration, song.duration_bytes)



class SongDirectoryCollector(QtCore.QRunnable):

    starting_dir: pathlib.Path
    recurse: bool
    signals: SongDirectoryCollectorSignals

    def __init__(self, starting_dir: pathlib.Path, recurse: bool=False):
        super(SongDirectoryCollector, self).__init__()
        self.starting_dir = starting_dir
        self.recurse = recurse
        self.signals = SongDirectoryCollectorSignals()


    @Slot()
    def run(self):
        self._walk_directory_tree(self.starting_dir)
        self.signals.work_complete.emit()

    def _walk_directory_tree(self, work_dir: pathlib.Path):

        files = (element for element in work_dir.iterdir() if element.is_file())
        dirs = (element for element in work_dir.iterdir() if element.is_dir())

        for file in files:
            try:
                song = Song(file)
                song.touch()
            except BassException:
                self.signals.song_errored.emit(file.as_posix())
            else:
                self.signals.emit_found_song(song)

        for dir_path in dirs:
            self._walk_directory_tree(dir_path)

