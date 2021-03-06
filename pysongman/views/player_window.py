"""
To research
    https://gist.github.com/lambdalisue/9110299
"""
import logging
import typing as T
import pathlib

from pysongman.lib.qtd import QtCore, Qt, QtWidgets, QtGui
from pysongman.lib.qtd import QPixmap, QAction, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from pysongman.lib.qtd import QIcon

from .. import ICON_DIR
from .. import CSS_DIR
from ..lib.qclickable_slider import QClickableSlider

log = logging.getLogger(__name__)

class PlayerWindowSignals(QtCore.QObject):
    on_close = QtCore.Signal()
    key_pressed = QtCore.Signal(QtGui.QKeyEvent)

class PlayerWindow(QtWidgets.QMainWindow):

    signals: PlayerWindowSignals

    m_file: QtWidgets.QMenu
    a_open_playlist: QAction
    a_play_dir: QAction
    a_play_file: QAction
    a_save_playlist: QAction
    act_exit: QAction

    m_play: QtWidgets.QMenu

    m_options: QtWidgets.QMenu
    a_config: QAction

    m_help: QtWidgets.QMenu

    body_playlist_behavior: QHBoxLayout
    controls: QHBoxLayout

    info_dash1: QHBoxLayout
    time_display: QLabel
    diagnostics: QLabel
    spectrogram: QLabel

    info_dash: QVBoxLayout
    current_song: QLabel

    playlist: QVBoxLayout
    repeat_button: QPushButton
    random_button: QPushButton

    status_and_views: QHBoxLayout
    progress_bar: QClickableSlider
    load_btn: QPushButton
    playlist_btn: QPushButton
    medialib_btn: QPushButton

    controls: QHBoxLayout
    previous_btn: QPushButton
    play_btn: QPushButton
    pause_btn: QPushButton
    stop_btn: QPushButton
    next_btn: QPushButton
    mute_btn: QPushButton
    volume_slider: QtWidgets.QSlider



    def __init__(self, *args, **kwargs):
        super(PlayerWindow, self).__init__()
        self.signals = PlayerWindowSignals()
        self.icons = self.load_icons()
        self.setup_UI()
        self.load_stylesheet()

    def keyPressEvent(self, event):
        super(PlayerWindow, self).keyPressEvent(event)
        self.signals.key_pressed.emit(event)


    def closeEvent(self, event):
        self.signals.on_close.emit()
        event.accept()


    def load_icons(self):
        icons = {}
        ico_files = [file for file in ICON_DIR.iterdir() if file.is_file() and file.name.endswith(".png")]
        for ifile in ico_files:  # type: pathlib.Path
            name, _ = ifile.name.split(".", 1)
            pmap = QPixmap(str(ifile.absolute()))
            icons[name] = QIcon(pmap)

        self.icons = icons
        return icons

    def setup_UI(self):
        """

            main body
            ----------------------------------------------------------
            Time progress - misc info - spectragraph
            marque
            ----------------------------------------------------------
            one vertical


            playlist controls
            ----------------------------------------------------------
            Repeat 1/all
            random playlist
            ----------------------------------------------------------
            one vertical

            layout
            ---------------------------------------------------------
            LINE1 => Main body - playlist controls
            LINE2 => progress bar - load file - playlist view - media view
            LINE3 => previous, play, pause, stop, next - mute - volume slider
            ---------------------------------------------------------
            three horz layouts wrapped in one vertical

        """

        self.setupMainBody()
        self.setupProgressAndViews()
        self.setupControlBar()
        self.setupMenuBar()


        # Put it all together
        self.main_body = QtWidgets.QVBoxLayout()
        self.main_body.setObjectName("mainBody")
        # self.main_body.layout().setMenuBar(self.menu_bar)
        self.main_body.addLayout(self.body_playlist_behavior)
        self.main_body.addLayout(self.status_and_views)
        self.main_body.addLayout(self.controls)

        self.main_widget = QtWidgets.QWidget(self)
        self.main_widget.setLayout(self.main_body)
        self.setCentralWidget(self.main_widget)
        self.setLayout(self.main_body)

        self.setWindowTitle("PySongMan")
        self.setMinimumWidth(350)
        self.setMaximumWidth(350)
        self.setFocusPolicy(Qt.StrongFocus)

    def setupMainBody(self):
        self.time_display = QtWidgets.QLabel("0:00")
        self.time_display.setObjectName("timeDisplay")

        self.diagnostics = QtWidgets.QLabel("Place holder")
        self.diagnostics.setObjectName("diagnostics")

        self.spectrogram = QtWidgets.QLabel("Spectrogram")
        self.spectrogram.setObjectName("Spectrogram")

        self.info_dash1 = QtWidgets.QHBoxLayout()
        self.info_dash1.setObjectName("infoDash1")

        self.info_dash1.addWidget(self.time_display)
        self.info_dash1.addWidget(self.diagnostics)
        self.info_dash1.addWidget(self.spectrogram)

        self.info_dash = QtWidgets.QVBoxLayout()
        self.info_dash.setObjectName("infoDash2")

        self.current_song = QtWidgets.QLabel("Artist - Title (12:34)")
        self.current_song.setObjectName("currentSong")

        self.info_dash.addLayout(self.info_dash1)
        self.info_dash.addWidget(self.current_song)

        # Playlist controls
        self.repeat_button = QtWidgets.QPushButton()
        self.repeat_button.setObjectName("repeatButton")
        self.repeat_button.setIcon(self.icons['repeat'])
        self.repeat_button.setCheckable(True)

        self.random_button = QtWidgets.QPushButton()
        self.random_button.setObjectName("randomButton")
        self.random_button.setIcon(self.icons["shuffle"])
        self.random_button.setCheckable(True)

        self.playlist = QtWidgets.QVBoxLayout()
        self.playlist.setObjectName("playListControls")

        for button in [self.repeat_button, self.random_button]:
            button.setMinimumWidth(25)
            button.setMaximumWidth(25)
            self.playlist.addWidget(button)

        # line1
        self.body_playlist_behavior = QtWidgets.QHBoxLayout()
        self.body_playlist_behavior.setObjectName("playlistBehavior")

        self.body_playlist_behavior.addLayout(self.info_dash)
        self.body_playlist_behavior.addLayout(self.playlist)


    def setupProgressAndViews(self):

        self.status_and_views = QtWidgets.QHBoxLayout()
        self.status_and_views.setObjectName("statusAndViews")

        # self.progress_bar = QtWidgets.QSlider(Qt.Horizontal)
        self.progress_bar = QClickableSlider(Qt.Horizontal)
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setTickInterval(5)
        self.progress_bar.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFocusPolicy(Qt.NoFocus)

        self.load_btn = QtWidgets.QPushButton()
        self.load_btn.setObjectName("loadButton")
        self.load_btn.setIcon(self.icons['folder'])

        self.playlist_btn = QtWidgets.QPushButton()
        self.playlist_btn.setObjectName("playlistButton")
        self.playlist_btn.setIcon(self.icons['list'])

        self.medialib_btn = QtWidgets.QPushButton()
        self.medialib_btn.setObjectName("medialibButton")
        self.medialib_btn.setIcon(self.icons['board'])

        self.status_and_views.addWidget(self.progress_bar)

        for button in [self.load_btn, self.playlist_btn, self.medialib_btn]:
            button.setMinimumWidth(35)
            button.setMaximumWidth(55)
            self.status_and_views.addWidget(button)

    def setupControlBar(self):
        # line3 - previous, play, pause, stop, next - mute - volume slider
        self.previous_btn = QtWidgets.QPushButton()
        self.previous_btn.setIcon(self.icons['previous'])
        self.previous_btn.setObjectName("previousButton")

        self.play_btn = QtWidgets.QPushButton()
        self.play_btn.setIcon(self.icons['play'])
        self.play_btn.setObjectName("playButton")

        self.pause_btn = QtWidgets.QPushButton()
        self.pause_btn.setIcon(self.icons['pause'])
        self.pause_btn.setObjectName("pauseButton")

        self.stop_btn = QtWidgets.QPushButton()
        self.stop_btn.setIcon(self.icons['stop'])
        self.stop_btn.setObjectName("stopButton")

        self.next_btn = QtWidgets.QPushButton()
        self.next_btn.setIcon(self.icons['next'])
        self.next_btn.setObjectName("nextButton")

        self.mute_btn = QtWidgets.QPushButton()
        self.mute_btn.setIcon(self.icons['volume-up'])
        self.mute_btn.setObjectName("muteButton")

        self.volume_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setTickInterval(10)
        self.volume_slider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.volume_slider.setRange(0, 100)

        self.controls = QtWidgets.QHBoxLayout()
        self.controls.setObjectName("controlBar")

        for button in [self.previous_btn, self.play_btn, self.pause_btn, self.stop_btn, self.next_btn, self.mute_btn]:
            button.setMinimumWidth(3)
            button.setMaximumWidth(25)
            button.setProperty("cssClass", "controlButton")
            self.controls.addWidget(button)

        self.controls.addWidget(self.volume_slider)

    def setupMenuBar(self):
        # Menu bar
        self.m_file = self.menuBar().addMenu("&File")
        self.a_play_file = self.m_file.addAction("Play &file")
        self.a_play_dir = self.m_file.addAction("Play &directory")
        self.a_open_playlist = self.m_file.addAction("Open &playlist")
        self.a_save_playlist = self.m_file.addAction("&Save playlist")
        self.m_file.addSeparator()
        self.act_exit = self.m_file.addAction("E&xit")

        self.m_play = self.menuBar().addMenu("&Play")

        self.m_options = self.menuBar().addMenu("&Options")
        self.a_config = self.m_options.addAction("Open &Configuration")

        self.m_help = self.menuBar().addMenu("&Help")

        return

    def load_stylesheet(self, filepath: T.Union[str, pathlib.Path] = None) -> None:
        """
            Given a valid file path(relative or absolute), load up the stylesheet file and
            inject it into the QWidget to ideally cascade downward.

            This is part of the UI plugin infrastructure envisioned.

        Args:
            filepath:

        """
        sheet = (CSS_DIR / "player.css").read_text()
        self.setStyleSheet(sheet)
        pass

    def toggle_volume_icon(self, volume_muted=False):
        if volume_muted is True:
            self.mute_btn.setIcon(self.icons['volume-off'])
        else:
            self.mute_btn.setIcon(self.icons['volume-up'])

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        super(PlayerWindow, self).focusInEvent(event)
        logging.debug("Got focus")