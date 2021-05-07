import sys
import argparse
import logging

from .lib.application import Application

log = logging.getLogger(__name__)

def setup_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    log.debug("Basic config logging enabled")


def main(song_path = None, nuke_everything = False):
    setup_logging()
    # TODO put a QMessageBox.confirm for nuke everything

    app = Application(song_path, nuke_everything)
    app.startup()
    return app.exec_()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("song_path", nargs="?", default=list())
    parser.add_argument("-nuke_everything", default=False, help="Wipe out the database and reset config files")
    args = parser.parse_args()
    main(args.song_path, nuke_everything=args.nuke_everything)