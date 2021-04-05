"""
https://stackoverflow.com/questions/15043620/cant-play-ogg-and-flac

https://www.xiph.org/dshow/ - required by QT to play ogg files


To implement, a clickable range slider.
https://stackoverflow.com/questions/52689047/moving-qslider-to-mouse-click-position

"""
import sys
import argparse
import typing as T
import pathlib

from ffprobe_analyzer import FFProbe

import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets
from PySide2 import QtMultimedia


class PlayerWindow(QtWidgets.QWidget):
    
    def __init__(self, *args, **kwargs):
        super(PlayerWindow, self).__init__(*args, **kwargs)
        self.setupUI()

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

        #Main display body
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

        #Playlist controls
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



        #line1
        self.body_playlist_behavior = QtWidgets.QHBoxLayout()
        self.body_playlist_behavior.setObjectName("playlistBehavior")

        self.body_playlist_behavior.addLayout(self.info_dash)
        self.body_playlist_behavior.addLayout(self.playlist)


        #Line2
        self.progress_bar = QtWidgets.QSlider(Qt.Horizontal)
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setRange(0,100)
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



        #line3 - previous, play, pause, stop, next - mute - volume slider
        self.previous_btn = QtWidgets.QPushButton("PR")
        self.previous_btn.setObjectName("previousButton")

        self.play_btn = QtWidgets.QPushButton("PL")
        self.play_btn.setObjectName("playButton")

        self.pause_btn = QtWidgets.QPushButton("PS")
        self.pause_btn.setObjectName("pauseButton")

        self.stop_btn = QtWidgets.QPushButton("ST")
        self.stop_btn.setObjectName("stopButton")

        self.next_btn = QtWidgets.QPushButton("NXT")
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

        #Menu bar
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

    def load_stylesheet(self, filepath: T.Union[str, pathlib.Path]) -> None:
        """
            Given a valid file path(relative or absolute), load up the stylesheet file and
            inject it into the QWidget to ideally cascade downward.

            This is part of the UI plugin infrastructure envisioned.

        Args:
            filepath:

        """
        pass


class PlayerController(QtCore.QObject):
    def __init__(self):
        self.view = PlayerWindow()
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setPlaylist(self.playlist)

        self.progress_bar_pressed = False
        self.last_volume = None

        self.connect()

    def connect(self):

        self.view.volume_slider.setRange(0, 100)
        self.view.volume_slider.setValue(100)
        self.view.volume_slider.valueChanged.connect(self.player.setVolume)
        self.view.mute_btn.clicked.connect(self.muted)

        self.view.play_btn.clicked.connect(self.player.play)
        self.view.pause_btn.clicked.connect(self.player.pause)
        self.view.stop_btn.clicked.connect(self.player.stop)

        self.view.next_btn.clicked.connect(self.playlist.next)
        self.view.previous_btn.clicked.connect(self.playlist.previous)

        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.currentMediaChanged.connect(self.mediaChanged)
        self.player.error.connect(self.mediaError)

        self.view.progress_bar.sliderPressed.connect(self.progressPressed)
        self.view.progress_bar.sliderReleased.connect(self.progressReleased)

        self.view.progress_bar.valueChanged.connect(self.progress_changed)
        # self.view.progress_bar.clicked.connect(self.progress_bar_pressed)


        self.view.load_btn.clicked.connect(self.open_song)


    def progressPressed(self):
        self.progress_bar_pressed = True


    def progressReleased(self):
        self.progress_bar_pressed = False


    def progress_changed(self, position):
        if self.progress_bar_pressed is True:
            self.player.setPosition(position)


    def durationChanged(self, duration):
        #
        print(f"{duration=}")
        self.view.progress_bar.setRange(0, duration)

    def positionChanged(self, position):
        print(f"{position=}")
        self.view.progress_bar.setValue(position)
        seconds = int(position / 1000)

        minutes = int(seconds / 60)

        corrected_seconds = int(seconds - (minutes * 60))

        self.view.time_display.setText(f"{minutes}:{corrected_seconds:02}")

    def mediaChanged(self, media: QtMultimedia.QMediaContent):
        print(media, vars(media), dir(media))
        raw_path = media.canonicalUrl().toString()
        if raw_path.strip() != "":
            print(f"{raw_path=}")
            probe = FFProbe(raw_path)

            for k,v in probe.info.items():
                print(f"\t{k}: {v}")

            self.view.current_song.setText(f"{probe.listing} ({probe.duration_str})")

    def muted(self):
        if self.last_volume is not None:
            self.player.setVolume(self.last_volume)
            self.view.volume_slider.setValue(self.last_volume)
            self.last_volume = None
        else:
            self.last_volume = self.player.volume()
            self.player.setVolume(0)
            self.view.volume_slider.setValue(0)

    def mediaError(self, error: QtMultimedia.QMediaPlayer.Error.ResourceError):
        print(error)


    def open_song(self):
        print("load song to playlist")
        fileDialog = QtWidgets.QFileDialog(self.view)
        supportedMimeTypes = ['audio/mpeg', 'application/ogg','application/octet-stream']
        fileDialog.setMimeTypeFilters(supportedMimeTypes)
        if fileDialog.exec_() == QtWidgets.QDialog.Accepted:
            files = fileDialog.selectedFiles()

            for file in files:
                print("Adding", file)
                content = QtMultimedia.QMediaContent(QtCore.QUrl(file))
                self.playlist.addMedia(content)

            self.player.play()

    def add_song(self, song_file):
        sanitized = str(song_file).replace("\\", "/")
        url = QtCore.QUrl(sanitized)
        content = QtMultimedia.QMediaContent(url)
        self.playlist.addMedia(content)




def main(music_file, argv):

    app = QtWidgets.QApplication(argv)
    controller = PlayerController()
    controller.add_song(music_file)
    controller.view.show()

    app.exec_()
    return



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("music_file")
    args = parser.parse_args()

    main(args.music_file, sys.argv)