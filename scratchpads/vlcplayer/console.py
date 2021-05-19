import vlc
import pathlib
from PySide2 import QtCore, QtWidgets


class MediaPlayer:
    player = None
    instance = None

    @classmethod
    def Init(cls):
        cls.instance = vlc.Instance()
        cls.player = cls.instance.media_player_new()

    @classmethod
    def Play(cls, song):

