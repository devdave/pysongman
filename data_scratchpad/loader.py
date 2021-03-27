import sys
import sqlite3
import pathlib
import argparse

from reader import read
from walker import walker
from db_creator import DB_FILENAME, create_schema




def loader(parent_dir, override_db_name=False):

    parent = pathlib.Path(parent_dir)
    db_name = override_db_name or DB_FILENAME

    if parent.exists() is False:
        raise RuntimeError(f"Provided {parent=!r} but this dir couldn't be found")

    if parent.is_dir() is False:
        raise RuntimeError(f"Provided {parent=!r} is not a directory")

    print(f"Creating DB")
    create_schema(db_name)

    print("Connecting to DB")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    print("Storing parent path")

    cursor.execute("INSERT INTO ParentDir(path) VALUES(?)", [str(parent)])
    conn.commit()

    cursor.execute("SELECT id FROM ParentDir WHERE path=?", [str(parent)])
    parent_id = cursor.fetchone()[0]


    print(f"Processing {parent=!r}")

    for index, song in enumerate(walker(parent)):
        if song.name.endswith((".mp3", ".ogg",)):
            print(f"Found {song.name=}")
            tags = read(song)
            columns = "title,track,artist,album,filesize,duration,filename,rel_path,parent_dir"
            rel_path = str(song).replace(str(parent), "")
            data = [
                tags.title,
                tags.track,
                tags.artist,
                tags.album,
                tags.filesize,
                tags.duration,
                tags.filename,
                rel_path,
                parent_id
            ]

            try:
                cursor.execute(f"INSERT INTO Song({columns}) VALUES(?,?,?,?,?,?,?,?,?)", data )
            except sqlite3.IntegrityError:
                print(f"Sus duplicate: {song=}, {tags.title=}, {parent_id=}")

    conn.commit()
    conn.close()





def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("parent_dir")
    parser.add_argument("--db_name", default=None)

    args = parser.parse_args(argv)

    loader(args.parent_dir, args.db_name)


if __name__ == "__main__":
    main(sys.argv[1:])





