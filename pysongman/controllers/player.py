"""

MP2/Layer 2 mp3 codec - https://www.microsoft.com/en-us/p/mpeg-2-video-extension/9n95q1zzpmh4?activetab=pivot:overviewtab
"""


import sys
import argparse
import typing as T
import pathlib

from ..views.playlist_window import PlaylistWindow
from ..views.player_window import PlayerWindow
from ..lib.ffprobe import FFProbe

import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets
from PySide2 import QtMultimedia



class PlayerController(QtCore.QObject):
    def __init__(self, song_file = None):
        self.view = PlayerWindow()
        self.playlist_view = PlaylistWindow()
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setPlaylist(self.playlist)



        self.progress_bar_pressed = False
        self.last_volume = None

        self.connect()

        if song_file is not None:
            self.add_song(song_file)
            # TODO auto play?

    def show(self):
        self.view.show()
        self.playlist_view.show()


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


    def mediaInserted(self, start, end):
        print("mediaInserted", start, end)




    def progressPressed(self):
        self.progress_bar_pressed = True


    def progressReleased(self):
        self.progress_bar_pressed = False


    def progress_changed(self, position: int):
        if self.progress_bar_pressed is True:
            self.player.setPosition(position)


    def durationChanged(self, duration: int):
        #
        print(f"{duration=}")
        song_path = self.player.currentMedia().canonicalUrl().toString()
        if song_path not in ["", " ", "."]:
            probe = FFProbe.Load(song_path)

            if probe.duration_ms < duration:
                print(f"DirectShow screwed up again: {duration=}, {probe.duration_ms=}")
                self.view.progress_bar.setRange(0, probe.duration_ms)
            else:
                self.view.progress_bar.setRange(0, duration)
        else:
            pass

    def positionChanged(self, position: int):

        time = position / 1000
        print(f"{position} - {int(time / 60)}:{int(time % 60):02}")

        self.view.progress_bar.setValue(position)
        # TODO modula would be better here
        seconds = int(position / 1000)
        minutes = int(seconds / 60)
        corrected_seconds = int(seconds - (minutes * 60))

        self.view.time_display.setText(f"{minutes}:{corrected_seconds:02}")

    def mediaChanged(self, media: QtMultimedia.QMediaContent):
        # print(media, vars(media), dir(media))
        raw_path = media.canonicalUrl().toString()
        if raw_path.strip() != "":
            print(f"{raw_path=}")
            probe = FFProbe.Load(raw_path)

            self.view.current_song.setText(f"{probe.listing} ({probe.duration_str})")

    def muted(self):
        """
            Toggles volume mute
        Returns:

        """
        if self.last_volume is not None:
            self.player.setVolume(self.last_volume)
            self.view.volume_slider.setValue(self.last_volume)
            self.last_volume = None
            self.view.toggle_volume_icon(False)
        else:
            self.last_volume = self.player.volume()
            self.player.setVolume(0)
            self.view.volume_slider.setValue(0)
            self.view.toggle_volume_icon(True)

    def mediaError(self, error: QtMultimedia.QMediaPlayer.Error.ResourceError):
        print(error)
        current_song = self.playlist.currentMedia()
        qurl = current_song.canonicalUrl()
        print("Unable to play", qurl.toString())


    def open_song(self):
        print("load song to playlist")
        fileDialog = QtWidgets.QFileDialog(self.view)
        supportedMimeTypes = ['audio/mpeg', 'application/ogg','application/octet-stream']
        fileDialog.setMimeTypeFilters(supportedMimeTypes)

        index = self.playlist.currentIndex()


        if fileDialog.exec_() == QtWidgets.QDialog.Accepted:
            files = fileDialog.selectedFiles()

            for file in files:
                print("Adding", file)
                content = QtMultimedia.QMediaContent(QtCore.QUrl(file))
                self.playlist.addMedia(content)

            self.playlist.setCurrentIndex(index + 1)
            self.player.play()

    def add_song(self, song_file):
        sanitized = str(song_file).replace("\\", "/")
        url = QtCore.QUrl(sanitized)
        content = QtMultimedia.QMediaContent(url)

        self.playlist.addMedia(content)
