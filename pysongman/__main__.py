import sys
import argparse
import pathlib

import PySide2
from PySide2 import QtWidgets

from .controllers.player import PlayerController


def main(song_file = None):

    app = QtWidgets.QApplication(sys.argv)

    player = PlayerController()
    player.show()

    if song_file is not None:
        player.add_song(song_file)
        player.play()

    return sys.exit(app.exec_())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("song_file", nargs="?", default=None)
    args = parser.parse_args()

    main(args.song_file)