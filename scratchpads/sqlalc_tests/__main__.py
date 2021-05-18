import sys
import argparse
import logging
from pathlib import Path

from sqlalchemy.orm import SessionTransaction

from pybass3 import Song as BassSong
from pybass3 import BassException

from .models import initialize_db, get_db
from .models.song import Song as SongModel
from .models.artist import Artist
from .models.album import Album
from .models.parent_dir import ParentDir

log = logging.getLogger(__name__)

def setup_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def load_directory(song_path: Path, parent: ParentDir):
    conn = get_db()
    valid_types = [".mp3", ".mp4", ".ogg"]
    log.debug("Loading %s", song_path)
    files = (element for element in song_path.iterdir() if element.is_file() and element.suffix in valid_types)
    dirs = (element for element in song_path.iterdir() if element.is_dir())
    created = 0

    with conn.s.begin() as trx: # type: SessionTransaction
        for file in files:
            record, is_old = SongModel.GetCreateByPath(file, parent)
            if is_old is True:
                log.debug("Old song record %s found", record)
            else:
                log.debug("Adding %r to db", record)
                conn.s.add(record)
                if record.is_valid:
                    created += 1

    for file_dir in dirs:
        created += load_directory(file_dir, parent)

    return created




def destroy_main():
    log.info("Rebuilding DB")
    db_location = Path(__file__).parent / "test.sqlite3"
    if db_location.exists():
        db_location.unlink()
    conn = initialize_db(create=True, db_location=db_location)
    return

def load_main(song_dirs: [Path]):

    log.debug("SP %s", song_dirs)
    db_location = Path(__file__).parent / "test.sqlite3"
    conn = initialize_db(db_location=db_location)
    created = 0

    if len(song_dirs) == 0:
        raise ValueError("Must provide atleast one path")

    for song_dir in song_dirs:  # type: Path
        with conn.s.begin() as trx: # type: SessionTransaction
            parent = ParentDir.GetCreate(song_dir)
            if parent.id is None:
                conn.s.add(parent)

        created += load_directory(song_dir, parent)

    log.debug("Created %d new records", created)


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Commands", dest="command")

    load_parser = subparsers.add_parser("load", help="load data")
    load_parser.add_argument("song_paths", nargs="+", type=Path)

    destroy = subparsers.add_parser("destroy", help="Reset the database to blank slate")

    summarize_parser = subparsers.add_parser("summarize")

    args = parser.parse_args()
    if args.command == "load":
        load_main(args.song_paths)
    elif args.command == "destroy":
        destroy_main()
    else:
        raise ValueError("Unknown command %s" % args.command)
