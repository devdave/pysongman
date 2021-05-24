from pathlib import Path

from .qtd import QtCore, Signal, Slot

from pybass3.pys2_song import Pys2Song

from ..models import get_db
from ..models.parent_dir import ParentDir
from ..models.artist import Artist
from ..models.album import Album
from ..models.song import Song

class MediaLibScannerSignals(QtCore.QObject):
    completed = Signal()
    batch_added = Signal()


class MedialibScanner(QtCore.QRunnable):

    VALID_SUFFIXES = (".mp3", ".mp4", ".ogg", ".opus", ".wav",)
    parent: ParentDir

    signals: MediaLibScannerSignals

    def __init__(self, parent_dir: Path):
        super(MedialibScanner, self).__init__()
        self.parent = ParentDir.GetCreate(parent_dir)
        self.signals = MediaLibScannerSignals()


    @Slot()
    def run(self) -> None:

        conn = get_db()
        if self.parent.id is None:
            conn.s.add(self.parent)
            conn.s.commit()

        self.scan_directory_tree(self.parent.path)
        self.signals.completed.emit()

    def scan_directory_tree(self, working_path: Path):
        conn = get_db()
        added_records = 0
        files = (file for file in working_path.iterdir() if file.is_file() and file.suffix in self.VALID_SUFFIXES)
        dirs = (subdir for subdir in working_path.iterdir() if subdir.is_dir() and subdir.name.startswith(".") is False)

        for file in files:
            record = Song.GetCreateByPath(file)
            conn.s.add(record)
            added_records += 1

        if added_records > 0:
            conn.s.commit()
            self.signals.batch_added.emit()

        conn.s.close()

        for subdir in dirs:
            self.scan_directory_tree(subdir)

