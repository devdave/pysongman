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


class Simple(QtWidgets.QWidget):

    def __init__(self, song_file):
        super(Simple, self).__init__()
        self.song_file = song_file
        self.song = Song(song_file)

        self.setupUI()
        self.connectUI()

        self.song.position_updated.connect(self.on_song_position_updated)

    def on_song_position_updated(self, seconds):
        self.duration.setText(repr(seconds))


    def setupUI(self):

        self.play_btn = QtWidgets.QPushButton("Play")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.pause_btn = QtWidgets.QPushButton("Pause")
        self.duration = QtWidgets.QLabel("0000")
        self.length = QtWidgets.QLabel("0000")
        self.table = QtWidgets.QTableWidget(1, 2)
        self.configureTable()

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.play_btn)
        vbox.addWidget(self.stop_btn)
        vbox.addWidget(self.pause_btn)
        vbox.addWidget(self.duration)
        vbox.addWidget(self.length)
        vbox.addWidget(self.table)

        self.setLayout(vbox)

    def add_table_row(self, row_id, label, value):
        label_item = QtWidgets.QTableWidgetItem(label)
        value_item = QtWidgets.QTableWidgetItem(value)
        self.table.setItem(row_id, 0, label_item)
        self.table.setItem(row_id, 1, value_item)


    def configureTable(self):
        columns = ["Name", "Value"]
        self.table.setHorizontalHeaderLabels(columns)
        row_id = 0

        lib_info = Bass.GetLibInfo()

        def advance_row(row_id):
            row_id = row_id + 1
            return row_id

        lib_fields = ["flags", "hwsize", "hwfree", "freesam", "free3d", "minrate", "maxrate", "eax", "minbuf", "dsver",
                  "latency", "initflags", "speakers", "freq"]

        device_fields = ["name", "driver", "flags"]

        self.table.setRowCount(len(lib_fields)+1+len(device_fields)+1)

        self.add_table_row(0, "Library info", "")
        for pos, field_name in enumerate(lib_fields, 1):
            field_value = getattr(lib_info, field_name)
            print(field_name, str(field_value))

            self.add_table_row(pos, field_name, repr(field_value))

        # IMPORTANT, fucking kill this struct as soon as possible to avoid memory leaks
        del lib_info

        device_info = Bass.GetDeviceInfo()

        self.add_table_row(len(lib_fields)+1,"Device info", "")
        for pos, field_name, in enumerate(device_fields, len(lib_fields)+2):
            field_value = getattr(device_info, field_name)
            self.add_table_row(pos, field_name, repr(field_value))



        self.table.resizeColumnsToContents()








    def connectUI(self):
        self.play_btn.clicked.connect(self.on_play_clicked)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        self.pause_btn.clicked.connect(self.on_pause_clicked)


    def on_play_clicked(self):
        print("Play clicked")
        self.length.setText(repr(self.song.seconds))
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
