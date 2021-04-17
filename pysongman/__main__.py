import sys
import argparse
import pathlib
import logging

import PySide2
from PySide2 import QtWidgets

from .controllers.application import Application
# from .controllers.player import PlayerController


log = logging.getLogger(__name__)


def configure_logging():
    from . import log as root_log

    root_log.setLevel(logging.DEBUG)
    log.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    basic_line = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s:%(lineno)s@%(funcName)s - %(message)s')
    sh.setFormatter(basic_line)
    root_log.addHandler(sh)
    log.addHandler(sh)


def main(song_file = None):


    configure_logging()
    log.info("Starting")

    app = Application(sys.argv)

    # player = PlayerController()
    # player.show()

    app.startup(song_file)
    return sys.exit(app.exec_())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("song_file", nargs="?", default=None)
    args = parser.parse_args()

    main(args.song_file.strip("\""))