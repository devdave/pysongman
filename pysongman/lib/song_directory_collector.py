import logging
import pathlib

import pysongman

from ..models import get_db
from ..models.song import Song as SongModel

from .qtd import QtCore, Qt, Signal, Slot
from pybass3.pys2_song import Pys2Song as Song


from pybass3 import BassException

log = logging.getLogger(__name__)

song_path = str
song_tags = dict
song_len_seconds = float
song_len_bytes = float


class SongDirectoryCollectorSignals(QtCore.QObject):
    song_found = Signal(song_path, song_tags, song_len_seconds, song_len_bytes)
    work_complete = Signal()
    song_errored = Signal(song_path)
    songs_found = Signal(list)

    def emit_found_song(self, song: Song):
        try:
            self.song_found.emit(song.file_path.as_posix(), song.tags, song.duration, song.duration_bytes)
        except OverflowError:
            log.exception("Overflow on %s", song.file_path)




class SongDirectoryCollector(QtCore.QRunnable):

    VALID_SUFFIX = [".mp3", ".mp4", ".wav", ".ogg", ".opus"]

    starting_dir: pathlib.Path
    recurse: bool
    signals: SongDirectoryCollectorSignals
    valid_suffix: list
    bulk_songs: list

    def __init__(self, starting_dir: pathlib.Path, recurse: bool = False, valid_suffix: list = None):
        super(SongDirectoryCollector, self).__init__()
        self.starting_dir = starting_dir
        self.recurse = recurse
        self.valid_suffix = valid_suffix or self.VALID_SUFFIX
        self.bulk_songs = []

        self.signals = SongDirectoryCollectorSignals()

    def transform_song_to_primitives(self, song: Song):
        return song.file_path.as_posix(), song.tags, song.duration, song.duration_bytes

    @Slot()
    def run(self):
        conn = get_db()
        self._walk_directory_tree(self.starting_dir, conn)
        self.signals.songs_found.emit(self.bulk_songs)
        self.signals.work_complete.emit()

    def _walk_directory_tree(self, work_dir: pathlib.Path, conn):

        files = (element for element in work_dir.iterdir() if element.is_file() and element.suffix in self.valid_suffix)
        dirs = (element for element in work_dir.iterdir() if element.is_dir())

        for file in files:

            try:
                record = SongModel.GetByPath(file) # type: SongModel
                if record:
                    song = Song(file, tags=dict(
                        title=record.title,
                        album=record.album.name,
                        artist=record.artist.name,
                    ), length_seconds=record.length_seconds, length_bytes=record.length_bytes)
                else:
                    song = Song(file)
                    song.touch()

            except BassException:
                self.signals.song_errored.emit(file.as_posix())
            else:
                if song.duration > 9000 or song.duration_bytes >= 17200000000:
                    song = self.fix_invalid_song(song)

                self.signals.emit_found_song(song)
                self.bulk_songs.append(self.transform_song_to_primitives(song))

        for dir_path in dirs:
            self._walk_directory_tree(dir_path, conn)


    def fix_invalid_song(self, song: Song):

        song._length_bytes = None
        song.touch()
        if song.duration >= 17241847040 or song.duration_bytes >= 17241847040:
            log.error("Song %s is still overflowing in duration time and bytes", song.file_path.name)

        if song.duration > 9000 or song.duration_bytes >= 17200000000:
            import mutagen
            meta = mutagen.File(song.file_path)
            song._length_bytes = song.file_path.stat().st_size
            song._length_seconds = meta.info.length


        return song
