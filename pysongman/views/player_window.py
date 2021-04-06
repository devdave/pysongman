import typing as T
import pathlib

import PyQt5
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

from .. import ICON_DIR

class PlayerWindow(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(PlayerWindow, self).__init__()
        self.icons = {}
        self.setupUI()

    def load_icons(self):


    def setupUI(self):
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

        # icons = {}
        # ico_files = [file for file in ICON_DIR.iterdir() if file.is_file() and file.name.endswith("png")]
        # for file in ico_files:
        #     fname, _ = file.name.split(".", 1)
        #     icons[fname] = QPixmap(file)

        # Main display body
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
        self.repeat_button = QtWidgets.QPushButton("L")
        self.repeat_button.setObjectName("repeatButton")

        self.random_button = QtWidgets.QPushButton("RA")
        self.random_button.setObjectName("randonButton")

        self.playlist = QtWidgets.QVBoxLayout()
        self.playlist.setObjectName("playListControls")

        for button in [self.repeat_button, self.random_button]:
            button.setMinimumWidth(3)
            button.setMaximumWidth(25)
            self.playlist.addWidget(button)

        # line1
        self.body_playlist_behavior = QtWidgets.QHBoxLayout()
        self.body_playlist_behavior.setObjectName("playlistBehavior")

        self.body_playlist_behavior.addLayout(self.info_dash)
        self.body_playlist_behavior.addLayout(self.playlist)

        # Line2
        self.progress_bar = QtWidgets.QSlider(Qt.Horizontal)
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFocusPolicy(Qt.NoFocus)

        self.load_btn = QtWidgets.QPushButton("LD")
        self.load_btn.setObjectName("loadButton")

        self.playlist_btn = QtWidgets.QPushButton("PL")
        self.playlist_btn.setObjectName("playlistButton")

        self.medialib_btn = QtWidgets.QPushButton("ML")
        self.medialib_btn.setObjectName("medialibButton")

        self.status_and_views = QtWidgets.QHBoxLayout()
        self.status_and_views.setObjectName("statusAndViews")

        self.status_and_views.addWidget(self.progress_bar)

        for button in [self.load_btn, self.playlist_btn, self.medialib_btn]:
            button.setMinimumWidth(3)
            button.setMaximumWidth(25)
            self.status_and_views.addWidget(button)



        # line3 - previous, play, pause, stop, next - mute - volume slider
        self.previous_btn = QtWidgets.QPushButton("PR")
        # self.previous_btn.setIcon(ico_files['previous'])
        self.previous_btn.setObjectName("previousButton")

        self.play_btn = QtWidgets.QPushButton("PL")
        # self.previous_btn.setIcon(ico_files['play'])
        self.play_btn.setObjectName("playButton")

        self.pause_btn = QtWidgets.QPushButton("PS")
        # self.previous_btn.setIcon(ico_files['pause'])
        self.pause_btn.setObjectName("pauseButton")

        self.stop_btn = QtWidgets.QPushButton("ST")
        # self.stop_btn.setIcon(ico_files['stop'])
        self.stop_btn.setObjectName("stopButton")

        self.next_btn = QtWidgets.QPushButton("NXT")
        # self.next_btn.setIcon(ico_files['next'])
        self.next_btn.setObjectName("nextButton")

        self.mute_btn = QtWidgets.QPushButton("MUTE")
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
            self.controls.addWidget(button)

        self.controls.addWidget(self.volume_slider)

        # Menu bar
        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_file = QtWidgets.QMenu("&File")
        self.menu_play = QtWidgets.QMenu("&Play")
        self.menu_options = QtWidgets.QMenu("&Options")
        self.menu_view = QtWidgets.QMenu("&View")
        self.menu_help = QtWidgets.QMenu("&Help")

        for menu in [self.menu_file, self.menu_play, self.menu_options, self.menu_view, self.menu_help]:
            self.menu_bar.addMenu(menu)

        # Put it all together
        self.main_body = QtWidgets.QVBoxLayout()
        self.main_body.setObjectName("mainBody")
        self.main_body.layout().setMenuBar(self.menu_bar)
        self.main_body.addLayout(self.body_playlist_behavior)
        self.main_body.addLayout(self.status_and_views)
        self.main_body.addLayout(self.controls)

        self.setLayout(self.main_body)
        self.setWindowTitle("PySongMan")
        self.setMinimumWidth(350)

    def load_stylesheets(self, filepath: T.Union[str, pathlib.Path]) -> None:
        """
            Given a valid file path(relative or absolute), load up the stylesheet file and
            inject it into the QWidget to ideally cascade downward.

            This is part of the UI plugin infrastructure envisioned.

        Args:
            filepath:

        """
        pass
