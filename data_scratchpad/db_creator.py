"""

"""
import sys
import sqlite3
import pathlib
import argparse


DB_FILENAME = "pysongman.sqlite3"

PARENT_DIR_TABLE = """
CREATE TABLE ParentDir (
    id integer PRIMARY KEY,
    path string
) WITHOUT ROWID;
"""

SONGS_TABLE = """
CREATE TABLE Songs (
    id integer PRIMARY KEY,
    title string,
    track string,
    artist string,
    album string,
    filesize integer,
    duration integer,

    filename string,
    parent_dir int,
    FOREIGN KEY (parent_dir) REFERENCES ParentDir
) WITHOUT ROWID;
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


