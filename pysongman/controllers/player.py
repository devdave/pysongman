"""

MP2/Layer 2 mp3 codec - https://www.microsoft.com/en-us/p/mpeg-2-video-extension/9n95q1zzpmh4?activetab=pivot:overviewtab
"""
import logging
import sys
import argparse
import typing as T
import pathlib

from ..views.playlist_window import PlaylistWindow
from ..views.player_window import PlayerWindow
from ..views.media_window import Media as MediaWindow
from ..lib.ffprobe import FFProbe
from .playlist import PlaylistController

import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets
from PySide2 import QtMultimedia
from PySide2 import QtGui

log = logging.getLogger(__name__)

class PlayerController(QtCore.QObject):

    def __init__(self, song_file = None):

        self.playlist_obj = QtMultimedia.QMediaPlaylist()

        self.playlist = PlaylistController(self.playlist_obj)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setPlaylist(self.playlist_obj)

        self.view = PlayerWindow()
        self.media_view = MediaWindow()


        self.progress_bar_pressed = False
        self.last_volume = None

        self.connect()

        if song_file is not None:
            self.add_song(song_file)
            # TODO auto play?

    def show(self):
        self.media_view.show()
        self.playlist.view.show()
        self.view.show()

        player_bottom = self.view.height() + self.view.y()
        player_right = self.view.width() + self.view.x()

        self.media_view.move(self.media_view.x(), player_bottom + 1)
        self.playlist.view.move(player_right, self.playlist.view.y())

    def focus(self):

        if self.media_view.isVisible():
            self.media_view.activateWindow()

        if self.playlist.view.isVisible():
            self.playlist.view.activateWindow()

        self.view.activateWindow()




    def play(self):
        self.player.play()


    def on_repeat_clicked(self):
        log.debug("Repeat clicked")
        if self.view.repeat_button.isChecked():
            self.playlist_obj.setPlaybackMode(self.playlist_obj.PlaybackMode.Loop)
        else:
            self.playlist_obj.setPlaybackMode(self.playlist_obj.PlaybackMode.CurrentItemOnce)


    def on_random_clicked(self):
        log.debug("Random clicked")
        if self.view.random_button.isChecked():
            self.playlist_obj.setPlaybackMode(self.playlist_obj.PlaybackMode.Random)
        else:
            self.playlist_obj.setPlaybackMode(self.playlist_obj.PlaybackMode.Sequential)



    def connect(self):

        self.view.random_button.clicked.connect(self.on_random_clicked)
        self.view.repeat_button.clicked.connect(self.on_repeat_clicked)

        self.view.volume_slider.setRange(0, 100)
        self.view.volume_slider.setValue(100)
        self.view.volume_slider.valueChanged.connect(self.player.setVolume)
        self.view.mute_btn.clicked.connect(self.muted)



        self.view.play_btn.clicked.connect(self.player.play)
        self.view.pause_btn.clicked.connect(self.player.pause)
        self.view.stop_btn.clicked.connect(self.player.stop)

        self.view.next_btn.clicked.connect(self.playlist_obj.next)
        self.view.previous_btn.clicked.connect(self.playlist_obj.previous)

        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.currentMediaChanged.connect(self.mediaChanged)
        self.player.error.connect(self.mediaError)

        self.view.progress_bar.sliderPressed.connect(self.progressPressed)
        self.view.progress_bar.sliderReleased.connect(self.progressReleased)
        self.view.progress_bar.progress_changed.connect(self.progress_changed_unsafe)
        self.view.progress_bar.valueChanged.connect(self.progress_changed)


        self.view.onClose.connect(self.do_close)

        self.view.playlist_btn.clicked.connect(self.toggle_playlist_view)
        self.view.medialib_btn.clicked.connect(self.toggle_media_view)

        self.view.load_btn.clicked.connect(self.open_song)



        # controller to controller
        # self.playlist.song_selected.connect(self.on_song_selected)
        self.playlist_obj.currentMediaChanged.connect(self.on_song_selected)

        self.view.keyPressed.connect(self.on_keypress)

        # Wire up menu's
        self.view.act_exit.triggered.connect(self.on_action_exit)


    def on_keypress(self, event: QtGui.QKeyEvent):
        if event.key() == Qt.Key_Z:
            self.playlist_obj.previous()
        elif event.key() == Qt.Key_X:
            self.player.play()
        elif event.key() == Qt.Key_C:
            self.player.pause()
        elif event.key() == Qt.Key_V:
            self.player.stop()
        elif event.key() == Qt.Key_B:
            self.playlist_obj.next()

        event.accept()


    def on_song_selected(self, media: QtMultimedia.QMediaContent, *args):
        self.player.play()

    def toggle_playlist_view(self):
        if self.playlist.view.isVisible():
            self.playlist.view.hide()
        else:
            self.playlist.view.show()

    def toggle_media_view(self):
        if self.media_view.isVisible():
            self.media_view.hide()
        else:
            self.media_view.show()

    def on_action_exit(self):
        self.do_close()

    def do_close(self):
        self.view.close()
        self.playlist.view.close()

        self.media_view.close()

    def mediaInserted(self, start, end):
        print("mediaInserted", start, end)




    def progressPressed(self):
        self.progress_bar_pressed = True


    def progressReleased(self):
        self.progress_bar_pressed = False


    def progress_changed(self, position: int):
        if self.progress_bar_pressed is True:
            self.player.setPosition(position)

    def progress_changed_unsafe(self, position: int):
        self.player.setPosition(position)


    def durationChanged(self, duration: int):

        log.debug("Duration=%s", duration)
        song_path = self.player.currentMedia().canonicalUrl().toString()
        if song_path not in ["", " ", "."]:
            probe = FFProbe.Load(song_path)

            if probe.duration_ms < duration:
                log.debug("DirectShow screwed up again: duration=%d probed=%d", duration, probe.duration_ms)

                self.view.progress_bar.setRange(0, probe.duration_ms)
            else:
                self.view.progress_bar.setRange(0, duration)
        else:
            pass

    def positionChanged(self, position: int):

        time = position / 1000


        self.view.progress_bar.setValue(position)
        # TODO modula would be better here
        seconds = int(position / 1000)
        minutes = int(seconds / 60)
        corrected_seconds = int(seconds - (minutes * 60))

        self.view.time_display.setText(f"{minutes}:{corrected_seconds:02}")

    def mediaChanged(self, media: QtMultimedia.QMediaContent):

        raw_path = media.canonicalUrl().toString()
        if raw_path.strip() != "":
            log.debug("raw_path=%s", raw_path)

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
        current_song = self.playlist_obj.currentMedia()
        qurl = current_song.canonicalUrl()
        log.critical("Unable to play %s because %s", qurl, error)


    def open_song(self):
        # print("load song to playlist")
        log.debug("Loading song to playlist")
        fileDialog = QtWidgets.QFileDialog(self.view)
        supportedMimeTypes = ['audio/mpeg', 'application/ogg','application/octet-stream']
        fileDialog.setMimeTypeFilters(supportedMimeTypes)


        index = self.playlist_obj.currentIndex()


        if fileDialog.exec_() == QtWidgets.QDialog.Accepted:
            files = fileDialog.selectedFiles()

            for file in files:
                log.debug("Adding %s", file)
                content = QtMultimedia.QMediaContent(QtCore.QUrl(file))
                self.playlist_obj.addMedia(content)

            self.playlist_obj.setCurrentIndex(index + 1)
            self.player.play()

    def add_song(self, song_file):
        sanitized = pathlib.Path(song_file).as_posix()
        url = QtCore.QUrl(sanitized)
        content = QtMultimedia.QMediaContent(url)

        self.playlist_obj.addMedia(content)

    def add_directory(self, songs_path):
        path = pathlib.Path(songs_path)
        assert path.is_dir() and path.exists(), f"{path.is_dir()=} and {path.exists()=}"
        files = (file for file in path.iterdir() if file.is_file() and file.suffix in [".ogg", ".mp3"])
        dirs = (file for file in path.iterdir() if file.is_dir())
        for song_file in files:
            self.add_song(song_file)

        for subdir in dirs:
            self.add_directory(subdir)
