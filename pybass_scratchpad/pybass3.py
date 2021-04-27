import dataclasses
import ctypes
from pathlib import Path

from PySide2 import QtCore
from PySide2 import QtWidgets


from bass_module import bass_module, func_type, Bass
from bass_stream import BassStream
from bass_channel import BassChannel

from codes import errors


QT = QtCore.Qt

get_error_description = errors.get_description

class Song(QtCore.QObject):
    position_updated = QtCore.Signal()
    song_finished = QtCore.Signal()

    def __init__(self, file_path):
        super(Song, self).__init__()
        Bass.Init()
        self.file_path = Path(file_path)
        assert self.file_path.exists()
        assert self.file_path.is_file()
        self._handle = None

    def __del__(self):
        if BassStream.Free(self._handle) is not True:
            Bass.RaiseError()

        self.handle = None

    @property
    def handle(self):
        if self._handle is None:
            self._handle = BassStream.CreateFile(False, bytes(self.file_path))
        return self._handle

    def play(self):
        code = BassChannel.Play(self.handle)
        if code is not True:
            #raise BassError
            print("Play failed")
            pass

    def stop(self):
        BassChannel.Stop(self.handle)

    def pause(self):
        BassChannel.Pause(self.handle)

    def resume(self):
        BassChannel.Resume(self.handle)


class Simple(QtWidgets.QWidget):

    def __init__(self, song_file):
        super(Simple, self).__init__()
        self.song_file = song_file
        self.song = Song(song_file)

        self.setupUI()
        self.connectUI()


    def setupUI(self):

        self.play_btn = QtWidgets.QPushButton("Play")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.pause_btn = QtWidgets.QPushButton("Pause")
        self.duration = QtWidgets.QLabel("00:00")
        self.table = QtWidgets.QTableWidget(1, 2)
        self.configureTable()

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.play_btn)
        vbox.addWidget(self.stop_btn)
        vbox.addWidget(self.pause_btn)
        vbox.addWidget(self.duration)
        vbox.addWidget(self.table)

        self.setLayout(vbox)

    def configureTable(self):
        columns = ["Name", "Value"]
        self.table.setHorizontalHeaderLabels(columns)



    def connectUI(self):
        self.play_btn.clicked.connect(self.on_play_clicked)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        self.pause_btn.clicked.connect(self.on_pause_clicked)


    def on_play_clicked(self):
        print("Play clicked")
        self.song.play()

    def on_stop_clicked(self):
        print("Stop clicked")
        self.song.stop()

    def on_pause_clicked(self):
        print("Pause clicked")
        self.song.pause()



def main(song_file):
    app = QtWidgets.QApplication()
    player = Simple(song_file)
    player.show()
    return app.exec_()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("song_file")
    args = parser.parse_args()

    main(args.song_file)
