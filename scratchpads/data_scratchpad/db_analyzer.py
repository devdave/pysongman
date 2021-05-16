
import argparse
import sqlite3
import pathlib
import sys

from db_creator import DB_FILENAME
from loader import loader


def analyze(database_path):
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()


    print("Fetching parents")
    cursor.execute("SELECT * from ParentDir")
    parents = cursor.fetchall()

    for row in parents:
        print(f" {row['id']=}, {row['path']=}")
        parent_path = pathlib.Path(row['path'])
        parent_id = row['id']
        if parent_path.exists() is False:
            raise RuntimeError(f"Unable to find parent path {parent_path}")

        # If I remember right, the entire result is buffered in memory, deal with this later
        #  when I do a burn out test against the master music library.

        cursor.execute("SELECT count() as 'count' FROM Song where parent_dir=?", [parent_id])
        count = cursor.fetchone()['count']
        print(f"Song count: {count}")

        cursor.execute("Select sum(duration) as 'duration' FROM Song WHERE parent_dir=?", [parent_id])
        duration = cursor.fetchone()['duration']

        print(f"{duration=}")
        print(f"minutes: {duration/60}")
        print(f"hours: {duration / 60 / 60}")
        print(f"Days: {duration / 60 / 60 / 24}")

        cursor.execute("SELECT sum(filesize) as 'filesize' FROM Song WHERE parent_dir=?", (parent_id,))
        filesize = cursor.fetchone()['filesize']

        print(f"{filesize=}")
        print(f"KB {filesize/1024}")
        print(f"MB {filesize/1024/1024}")
        print(f"GB {filesize/1024/1024/1024}")


        cursor.execute("SELECT count() as 'count' FROM Artist")
        artists = cursor.fetchone()
        print(f"{artists['count']=}")

        cursor.execute("SELECT count() as 'count' FROM ArtistAlbum")
        albums = cursor.fetchone()
        print(f"{albums['count']=}")


        cursor.execute("SELECT count() as 'count' from Song WHERE duration < 1")
        damaged_files = cursor.fetchone()
        print(f"Damaged files: {damaged_files['count']}")







def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_name", default=DB_FILENAME)

    args = parser.parse_args(argv)

    analyze(args.db_name)


if __name__ == "__main__":
    main(sys.argv[1:])


