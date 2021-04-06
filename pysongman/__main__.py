import sys
import argparse
import pathlib

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from .controllers.player import PlayerController


def main(song_file):

    app = QtWidgets.QApplication(sys.argv)

    player = PlayerController()
    player.view.show()

    return sys.exit(app.exec_())

if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("song_file", nargs="?", default=None)
    # args = parser.parse_args()

    main(None)