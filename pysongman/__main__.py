import argparse

from .lib.application import Application


def main(song_path = None, nuke_everything = False):
    app = Application(song_path, nuke_everything)
    app.startup()
    return app.exec_()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("song_path", nargs="?", default=list())
    parser.add_argument("-nuke_everything", default=False, help="Wipe out the database and reset config files")
    args = parser.parse_args()
    main(args.song_path, nuke_everything=args.nuke_everything)