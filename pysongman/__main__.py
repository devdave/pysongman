import sys
import argparse
import logging

print("Prestart - Fetching App")
from . import App, HERE, HOME, CONFIGURED_FLAG
from .lib.application import Application

log = logging.getLogger(__name__)

def setup_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    log.debug("Basic config logging enabled")


def main(song_path = None, nuke_everything = False, debug_flag=False):
    setup_logging()

    log.debug(f"Pysongman.main called with {song_path=}, {nuke_everything=}, {debug_flag=}")

    App = Application(here=HERE, home=HOME, configured=CONFIGURED_FLAG)

    App.configure(song_path=song_path, nuke_everything=nuke_everything, debug_flag=debug_flag)
    return App.exec_()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("song_path", nargs="*", default=list(), help="Optional individual songs or whole directories to play on start")
    parser.add_argument("--nuke_everything", default=False, help="Wipe out the database and reset config files")
    parser.add_argument("--debug", dest="debug_flag", action="store_true", default=False, help="Enable extensive debugging tools")
    args = parser.parse_args()
    main(args.song_path, nuke_everything=args.nuke_everything, debug_flag=args.debug_flag)