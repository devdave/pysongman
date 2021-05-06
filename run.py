import sys
import argparse
import pathlib

# from PySide2 import QtCore
# from PySide2 import QtWidgets
import PyQt5
from PyQt5 import QtCore
from PyQt5 import QtWidgets



# from .controllers.player import PlayerController
from pysongman_old.controllers.player import PlayerController

class Test(PyQt5.QtWidgets.QTabWidget):
    pass


def main(song_file):
    # player = PlayerController(song_file)
    #
    # player.view.show()
    # print("Player shown")
    test = Test()
    test.show()

    app = QtWidgets.QApplication()

    return sys.exit(app.exec_())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("song_file", nargs="?", default=None)
    args = parser.parse_args()

    main(args.song_file)