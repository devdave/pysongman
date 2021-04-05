import sys
import argparse
import pathlib

# from PySide2 import QtCore
# from PySide2 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtWidgets



from .controllers.player import PlayerController



def main(song_file):
    # player = PlayerController(song_file)
    #
    # player.view.show()

    from .views.player_window import PlayerWindow
    view = PlayerWindow()

    print("Player shown")

    app = QtWidgets.QApplication()

    return sys.exit(app.exec_())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("song_file", nargs="?", default=None)
    args = parser.parse_args()

    main(args.song_file)