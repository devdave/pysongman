from pathlib import Path

from PySide2 import QtCore

from bass_module import Bass
from bass_channel import BassChannel
from bass_stream import BassStream

class Song(QtCore.QObject):
    position_updated = QtCore.Signal(int)
    song_finished = QtCore.Signal()

    def __init__(self, file_path, precision=250):
        super(Song, self).__init__()
        Bass.Init()
        self.file_path = Path(file_path)
        assert self.file_path.exists(), f"{self.file_path} doesn't exist!"
        assert self.file_path.is_file(), f"{self.file_path} is not a valid file!"
        self._handle = None
        self._handle_length = None
        self._handle_position = None

        self._tracking_finish = False

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(precision) # TODO, do I really need 1/4th a second precision?
        self.timer.timeout.connect(self.pulser)

    @QtCore.Slot(int)
    def pulser(self):
        position = BassChannel.GetPositionSeconds(self.handle)
        self.position_updated.emit(position)




    def __del__(self) -> None:
        """
        I vaguely remember that exceptions from __del__ can be problematic but I'd rather
         this entire thing crash and burn than create a growing memory leak.
        Returns: None
        """
        self.free_stream()


    def free_stream(self):
        if self._handle is not None:
            retval = BassStream.Free(self._handle)
            if retval is not True:
                Bass.RaiseError()

        self._handle = None

    @property
    def handle(self):
        if self._handle is None:
            self._handle = BassStream.CreateFile(False, bytes(self.file_path))
            self._handle_length = BassChannel.GetLengthSeconds(self._handle)
        return self._handle


    @handle.deleter
    def handle(self):
        self.free_stream()

    def __len__(self):
        # position = BassChannel.GetPositionBytes(self.handle)
        length = BassChannel.GetLengthBytes(self.handle)

        return length

    @property
    def seconds(self):
        return BassChannel.GetLengthSeconds(self.handle, len(self))


    def play(self):
        code = BassChannel.Play(self.handle)
        if code is not True:
            #raise BassError
            print("Play failed")
            pass

        self.timer.start()

    def stop(self):
        BassChannel.Stop(self.handle)
        self.timer.stop()

    def pause(self):
        BassChannel.Pause(self.handle)

    def resume(self):
        BassChannel.Resume(self.handle)
