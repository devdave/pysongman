from pathlib import Path
import logging

from .qtd import QtCore, Signal, Slot

from pybass3.pys2_song import Pys2Song

from ..models import get_db
from ..models.parent_dir import ParentDir
from ..models.artist import Artist
from ..models.album import Album
from ..models.song import Song

log = logging.getLogger(__name__)


class MediaLibScannerSignals(QtCore.QObject):
    completed = Signal()
    file_processed = Signal(str)
    batch_added = Signal()


class MedialibScanner(QtCore.QRunnable):

    VALID_SUFFIXES = (".mp3", ".mp4", ".ogg", ".opus", ".wav",)
    parent: ParentDir

    signals: MediaLibScannerSignals

    def __init__(self, valid_suffixes=None):
        super(MedialibScanner, self).__init__()
        log.debug("Created new Media Library scanner")
        self.valid_suffixes = valid_suffixes or self.VALID_SUFFIXES
        self.signals = MediaLibScannerSignals()


    @Slot()
    def run(self) -> None:
        log.debug("Running")
        conn = get_db()
        for parent in ParentDir.query.all():  # type: ParentDir
            log.info("Processing: id=`%d`(%s)", parent.id, parent.path.as_posix())
            self.scan_directory_tree(parent.path, parent, conn)

        log.debug("Media scanner finished")
        self.signals.completed.emit()

        del conn

    def scan_directory_tree(self, working_path: Path, parent, conn, recurse: bool = True):
        log.debug("Scanning %s", working_path)
        added_records = 0
        files = (file for file in working_path.iterdir() if file.is_file() and file.suffix in self.VALID_SUFFIXES)
        dirs = (subdir for subdir in working_path.iterdir() if subdir.is_dir() and subdir.name.startswith(".") is False)

        for file in files:
            record = Song.GetCreateByPath(file, parent)
            conn.s.add(record)

            self.signals.file_processed.emit(file.as_posix())

        conn.s.commit()
        self.signals.batch_added.emit()

        if recurse is True:
            for subdir in dirs:
                self.scan_directory_tree(subdir, parent, conn, recurse=recurse)

