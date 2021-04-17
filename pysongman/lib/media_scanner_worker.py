
import pathlib
import logging

import PySide2
from PySide2 import QtCore
from PySide2.QtCore import QRunnable, Slot

from ..lib.ffprobe import FFProbe
from ..models import initialize_db
from ..models.song import Song
from ..models.parent_dir import ParentDir
from ..models.artist import Artist
from ..models.album import Album

log = logging.getLogger(__name__)


class MediaScannerWorker(QRunnable):
    """
        Work in the background to load a directory into
            the media library.
    """
    def __init__(self, working_dir, add_to_db = False):
        super(MediaScannerWorker, self).__init__(*args, **kwargs)
        self.working_path = working_dir
        self.add_to_db = add_to_db

        if self.add_to_db:
            self.conn = initialize_db()  # wake up SA but keep a single handle to the scoped sesssion

    @Slot(str)
    def run(self, working_dir):
        working_dir = pathlib.Path(working_dir)
        if working_dir.is_dir():

            self.process_directory(working_dir)
        elif working_dir.is_file():
            self.process_file(working_dir)
        else:
            log.error("I don't know how to handle %s", working_dir)

    def process_directory(self, work: pathlib.Path, master_dir):
        assert work.is_dir(), f"Process directory got {work} which is not a directory."

        # use generators to cut down on wasted memory of loading what might be THOUSANDS of files
        #  or hundreds of directories.
        # yes, my music library is that big.

        files = (file for file in work.iterdir() if work.is_file() and work.suffix.endswith('ogg', 'wav', 'mp3',))
        dirs = (file for file in work.iterdir() if work.is_dir())
        for file in files:
            self.process_file(file)

    def process_file(self, music_file):
        # kick this bitch off
        probe = FFProbe.Load(music_file)

