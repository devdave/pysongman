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
        song_file = pathlib.Path(song_file)
        if song_file.is_file():
            player.add_song(song_file)
        elif song_file.is_dir():
            player.add_directory(song_file)

        player.play()

    return sys.exit(app.exec_())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("song_file", nargs="?", default=None)
    args = parser.parse_args()

    main(args.song_file.strip("\""))