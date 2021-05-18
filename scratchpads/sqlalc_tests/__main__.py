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

    with conn.s.begin() as trx: # type: SessionTransaction
        for file in files:
            record, is_old = SongModel.GetCreateByPath(file, parent)
            if is_old is True:
                log.debug("Old song record %s found", record)
            else:
                log.debug("Adding %r to db", record)
                conn.s.add(record)


    for file_dir in dirs:
        load_directory(file_dir, parent)







def main(song_dirs: [Path]):
    setup_logging()

    db_location = Path(__file__).parent / "test.sqlite3"
    if db_location.exists():
        db_location.unlink()
    conn = initialize_db(create=True, db_location=db_location)

    log.debug("SP %s", song_dirs)

    if len(song_dirs) == 0:
        raise ValueError("Must provide atleast one path")

    for song_dir in song_dirs:  # type: Path
        with conn.s.begin() as trx: # type: SessionTransaction
            parent = ParentDir()
            parent.path = song_dir.as_posix()
            conn.s.add(parent)
            
            parent = ParentDir.GetCreate(song_dir)
            if parent.id is None:
                conn.s.add(parent)

        load_directory(song_dir, parent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("song_paths", nargs="*", type=Path)

    args = parser.parse_args()
    main(args.song_paths)