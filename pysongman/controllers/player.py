
import logging
from pathlib import Path

from .. import USE_PYSIDE
from ..views.player_window import PlayerWindow
from ..lib.qtd import QObject, Signal, QtWidgets, QtGui, Qt, Slot

from pybass3.pys2_playlist import Pys2Playlist


log = logging.getLogger(__name__)


class PlayerControlSignals(QObject):
    view_closed = Signal()
    show_playlist = Signal(bool)
    show_medialib = Signal(bool)
    show_config = Signal()
    key_pressed = Signal(QtGui.QKeyEvent)


class PlayerControl(QObject):

    playlist: Pys2Playlist
    view: PlayerWindow
    signals: PlayerControlSignals

    def __init__(self, playlist: Pys2Playlist):
        super(PlayerControl, self).__init__()
        self.signals = PlayerControlSignals()
        self.playlist = playlist
        self.view = PlayerWindow()
        self.tracked_keys = [Qt.Key_Z, Qt.Key_X, Qt.Key_C, Qt.Key_V, Qt.Key_B]

        #behavior management
        self.progress_slider_pressed = False

        log.debug("Initialized Player controller")

        self.setup_connections()


    def setup_connections(self):
        log.debug("Setting up Player control connections")

        self.view.load_btn.clicked.connect(self.on_add_file)

        #Playlist direct wires
        self.view.previous_btn.clicked.connect(self.on_previous)
        self.view.play_btn.clicked.connect(self.on_play)
        self.view.stop_btn.clicked.connect(self.on_stop)
        self.view.pause_btn.clicked.connect(self.on_pause)
        self.view.next_btn.clicked.connect(self.on_next)

        # Playlist events
        self.playlist.signals.song_changed.connect(self.on_song_changed)
        self.playlist.signals.ticked.connect(self.on_playlist_tick)

        # Playlist behavior
        self.view.random_button.clicked.connect(self.on_random_clicked)
        self.view.signals.key_pressed.connect(self.on_keypress)

        #Song controls
        self.view.progress_bar.sliderPressed.connect(self.on_progress_pressed)
        self.view.progress_bar.sliderReleased.connect(self.on_progress_released)
        self.view.progress_bar.progress_changed.connect(self.on_progress_clicked)
        self.view.progress_bar.valueChanged.connect(self.on_progress_slider_value_changed)

        #View controls
        self.view.playlist_btn.clicked.connect(self.toggle_playlist)
        self.view.medialib_btn.clicked.connect(self.toggle_medialib)
        self.view.signals.on_close.connect(self.on_close)

        # Menu controls
        self.view.a_config.triggered.connect(lambda : self.signals.show_config.emit())

    def show(self):
        log.debug("Showing Player control view(s)")
        self.view.show()

    def on_add_file(self):

        dialog = QtWidgets.QFileDialog(self.view)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        dialog.setNameFilters(["Music files (*.mp3 *.ogg *.wav)", "Any (*)"])

        music_dir = Path.home() / "music"
        if music_dir.exists() is False:
            music_dir = Path.home()

        dialog.setDirectory(music_dir.as_posix())

        if dialog.exec_():
            paths = dialog.selectedFiles()
            log.debug("User add file request %s", paths)

            for song_path in paths:
                song = self.playlist.add_song(Path(song_path))
                if song is not None:
                    mb = QtWidgets.QMessageBox.information(self.view, "Added files", f"Song {song.title} was added")

    def on_add_dir(self):
        dialog = QtWidgets.QFileDialog(self.view)
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)

        music_dir = (Path.home() / "music").as_posix() if (Path.home() / "music").exists() else Path.home().as_posix()

        dialog.setDirectory(music_dir)

        if dialog.exec_():
            paths = dialog.selectedFiles()
            log.debug("User directory add request %s", paths)

            for dir_path in paths:
                ids = self.playlist.add_directory(Path(dir_path))

            if len(ids) > 0:
                mb = QtWidgets.QMessageBox.information(self.view, "Song added", "%s songs were added" % len(ids))
                mb.exec_()


    @Slot()
    def on_previous(self):
        self.playlist.previous()

    @Slot()
    def on_play(self):
        self.playlist.play()

    @Slot()
    def on_pause(self):
        self.playlist.pause()

    @Slot()
    def on_stop(self):
        self.playlist.stop()

    @Slot()
    def on_next(self):
        self.playlist.next()

    @Slot()
    def on_song_changed(self, song_id):
        log.debug("Song was changed")
        current_song_label = f"{self.playlist.current.title}({self.playlist.current.duration_time})"
        self.view.current_song.setText(current_song_label)
        self.view.current_song.setToolTip(current_song_label)
        self.view.progress_bar.setRange(0, self.playlist.current.duration_bytes)
        self.view.progress_bar.setValue(self.playlist.current.position_bytes)

    @Slot()
    def on_playlist_tick(self):
        if self.playlist.current is not None:
            self.view.time_display.setText(self.playlist.current.position_time)
            self.view.progress_bar.setValue(self.playlist.current.position_bytes)
        else:
            log.error("Playlist ticked but current is None, that shouldn't be happening")

    @Slot()
    def on_random_clicked(self, is_toggled):
        log.debug("Random toggled %s", is_toggled)

        if is_toggled is True:
            self.playlist.set_randomize(restart_and_play=False)
        else:
            self.playlist.set_sequential(restart_and_play=False)

    @Slot()
    def on_progress_pressed(self):
        self.progress_slider_pressed = True

    @Slot()
    def on_progress_released(self):
        self.progress_slider_pressed = False

    @Slot()
    def on_progress_changed_unsafe(self):
        if self.playlist.current is not None:
            self.playlist.current.move2position_bytes(self.view.progress_bar.value())

    @Slot()
    def on_progress_clicked(self, value):
        if self.playlist.current is not None:
            self.playlist.current.move2position_bytes(value)

    @Slot()
    def on_progress_slider_value_changed(self):
        """
            To prevent a recursive nightmare, only move position if the user is doing it.

        """
        if self.progress_slider_pressed is True and self.playlist.current is not None:
            self.playlist.current.move2position_bytes(self.view.progress_bar.value())

    @Slot()
    def on_close(self):
        log.debug("Player closed")
        self.signals.view_closed.emit()


    def toggle_playlist(self):
        log.debug("Please toggle playlist")
        self.signals.show_playlist.emit(True)

    def toggle_medialib(self):
        self.signals.show_medialib.emit(True)

    @Slot()
    def on_keypress(self, event: QtGui.QKeyEvent):

        if event.key() in self.tracked_keys:
            log.debug("%s was pressed, emitting", event.key())
            self.signals.key_pressed.emit(event)

        event.accept()