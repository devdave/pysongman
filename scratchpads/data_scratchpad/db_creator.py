"""

"""
import sys
import sqlite3
import pathlib
import argparse


DB_FILENAME = "pysongman.sqlite3"

PARENT_DIR_TABLE = """
CREATE TABLE ParentDir (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE
);
"""

ALBUM_TABLE = """
CREATE TABLE ArtistAlbum (
    id integer PRIMARY KEY AUTOINCREMENT,
    artist_id INTEGER,
    name TEXT,
    CONSTRAINT ux_artist_name UNIQUE (artist_id, name)
);
"""

ARTIST_TABLE = """
CREATE TABLE Artist(
    id integer PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);
"""

SONGS_TABLE = """
CREATE TABLE Song (
    id integer PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    track TEXT,
    artist_id INTEGER,
    album_id INTEGER,
    filesize INTEGER,
    duration REAL,

    filename TEXT,
    rel_path TEXT,
    parent_dir INTEGER,
    FOREIGN KEY (album_id) REFERENCES ArtistAlbum,
    FOREIGN KEY (parent_dir) REFERENCES ParentDir,
    UNIQUE(rel_path, parent_dir)
);
"""


def create_schema(override_name=None):

    db_name = override_name or DB_FILENAME

    db_path = pathlib.Path(db_name)

    if db_path.exists():
        print("DB Exists, deleting")
        db_path.unlink(False)


    conn = sqlite3.connect(db_name)

    cursor = conn.cursor()

    print("Creating tables")
    cursor.execute(ARTIST_TABLE)
    cursor.execute(ALBUM_TABLE)
    cursor.execute(PARENT_DIR_TABLE)
    cursor.execute(SONGS_TABLE)

    conn.commit()
    conn.close()


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_name", default=None)

    args = parser.parse_args(argv)

    create_schema(args.db_name)


if __name__ == "__main__":
    main(sys.argv[1:])


