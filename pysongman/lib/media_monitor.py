
from pybass3.pys2_playlist import Pys2Playlist

from .qtd import QObject, Slot
from ..models import get_db
from ..models.song import Song as SongModel

class MediaMonitor(QObject):

    playlist: Pys2Playlist

    def __init__(self, playlist: Pys2Playlist):
        super(MediaMonitor, self).__init__()
        self.playlist = playlist

        self.setup_connections()


    def setup_connections(self):
        self.playlist.signals.song_changed.connect(self.on_song_changed)


    @Slot()
    def on_song_changed(self, song_id):
        if self.playlist.current is not None:
            record = SongModel.query.filter(SongModel.path == self.playlist.current.file_path).first()
            if record is not None:
                record.play_count = record.play_count + 1
                conn = get_db()
                conn.s.add(record)
                conn.s.commit()
                conn.s.close()
                del conn




