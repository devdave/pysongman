"""
    TODO - group by album/sub dir
"""
import sys
import sqlite3
import pathlib
import argparse
from collections import defaultdict


from reader import read
from walker import walker
from db_creator import DB_FILENAME, create_schema


class Artist:
    CACHE = defaultdict(lambda: None)

    @classmethod
    def Create(cls, conn: sqlite3.Connection, artist: str, recursed=False):

        cursor = conn.cursor()
        cursor.execute("INSERT INTO Artist(name) VALUES(?)", [artist])
        conn.commit()
        cursor.close()

        return cls.Fetch(conn, artist, True)



    @classmethod
    def Fetch(cls, conn: sqlite3.Connection, artist: str, recursed=False):

        cursor = conn.cursor()
        cursor.execute("SELECT id from Artist WHERE name=?", [artist])
        try:
            artist_id = cursor.fetchone()[0]
        except TypeError:
            artist_id = None

        cursor.close()

        if artist_id is not None:
            cls.CACHE[artist] = artist_id
            return artist_id
        elif recursed is False:
            cursor.close()
            return cls.Create(conn, artist, True)

        else:
            raise RuntimeError(f"recursion! {artist=}")



    @classmethod
    def Get(cls, conn, artist):

        cached_id = cls.CACHE[artist]
        if cached_id is not None:
            return cached_id
        else:
            return cls.Fetch(conn, artist)




class Album:
    # CACHE[ARTIST][ALBUM] -> album ID
    CACHE = defaultdict(lambda: defaultdict(lambda : None))


    @classmethod
    def Create(cls, conn: sqlite3.Connection, artist_id, album, recursed=False):

        if recursed is not False:
            raise RuntimeError(f"Recursed into create record with {artist_id=} {album=}")

        cursor = conn.cursor()
        cursor.execute("INSERT INTO ArtistAlbum(artist_id, name) VALUES (?, ?)", [artist_id, album])
        cursor.close()

        return cls.Fetch(conn, artist_id, album, recursed=True)



    @classmethod
    def Fetch(cls, conn: sqlite3.Connection, artist_id, album, recursed=False):
        cursor = conn.cursor()

        cursor.execute("SELECT id from ArtistAlbum WHERE artist_id=? AND name=?", [artist_id, album])

        try:
            album_id = cursor.fetchone()[0]
        except TypeError:
            album_id = None

        cursor.close()

        if album_id:
            cls.CACHE[artist_id][album] = album_id
            return album_id
        elif recursed is False:
            return cls.Create(conn, artist_id, album, recursed)
        else:
            raise RuntimeError(f"Attempted to fetch album.id but {recursed=} for {artist_id=} and {album=}")


    @classmethod
    def Get(cls, conn: sqlite3.Connection, artist_id: int, album: str):
        cached_id = cls.CACHE[artist_id][album]
        if cached_id is not None:
            return cached_id
        else:
            return cls.Fetch(conn, artist_id, album)




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
            columns = "title,track,artist_id,album_id,filesize,duration,filename,rel_path,parent_dir"
            rel_path = str(song).replace(str(parent), "")
            data = [
                tags.title,
                tags.track,
                Artist.Get(conn, tags.albumartist),
                Album.Get(conn, Artist.Get(conn, tags.albumartist), tags.album),
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





