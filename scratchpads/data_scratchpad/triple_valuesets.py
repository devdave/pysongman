
import sys
import sqlite3
import pathlib
import argparse

from db_creator import DB_FILENAME


def artist2album_song_counts(conn):

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()


    data_set = []

    cursor.execute("SELECT * FROM Artist;")


    artists = cursor.fetchall()
    # A join would likely be much quicker here
    for artist in artists:
        try:
            cursor.execute("SELECT count() as 'count' from ArtistAlbum WHERE artist_id = ?", [artist['id']])
            album_count = cursor.fetchone()['count']
        except ValueError:
            print(f"Bad value: {artist['id']=}")
            album_count = 0


        cursor.execute("SELECT count() as 'count' from Song where artist_id = ?", [artist['id']])
        song_count = cursor.fetchone()['count']
        data_set.append({"name":artist['name'], "album_count":album_count, "song_count":song_count})

    return data_set









def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_file", default=DB_FILENAME)
    args = parser.parse_args(argv)

    conn = sqlite3.connect(args.db_file)

    data = artist2album_song_counts(conn)
    for row in data:
        print(row)



if __name__ == '__main__':
    main(sys.argv[1:])