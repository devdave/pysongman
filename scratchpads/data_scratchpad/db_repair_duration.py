import sys
import json
import argparse
import pathlib
import sqlite3
import subprocess
import shlex

from db_creator import DB_FILENAME

FFPROBE_BIN = pathlib.Path(r""".\bin_ffmpeg\ffprobe.exe""")

assert FFPROBE_BIN.exists()

FFPROBE_ARGS = [r"""%s""" % FFPROBE_BIN, "-v", "quiet", "-print_format", "json", "-show_streams"]

class RepairParentSong:

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row

    def __iter__(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT * from ParentDir")
        parents = cursor.fetchall()
        for parent in parents:
            base = pathlib.Path(parent['path'])
            assert base.exists() is True
            assert base.is_dir() is True

            cursor.execute(f"SELECT * from Song where duration <= 1 and parent_dir={parent['id']};")
            broken_songs = cursor.fetchall()

            for song in broken_songs:
                # skip over starting /
                yield song, base / song['rel_path'][1:]

    @classmethod
    def Repair(self, conn: sqlite3.Connection, record_id: int, new_duration: float):
        cursor = conn.cursor()
        cursor.execute("UPDATE Song SET duration=? WHERE id = ?", [new_duration, record_id])
        conn.commit()
        cursor.close()



def ffprobe_scan_for_duration(payload):
    for stream in payload['streams']:
        if "duration" in stream:
            return stream['duration']

    return None


def fetch_ffprobe_duration(song_path):
    exec_str = FFPROBE_ARGS + ["%s" % song_path.absolute()]
    process = subprocess.run(exec_str, capture_output=True)

    if process.returncode == 0:
        payload = json.loads(process.stdout)
        return ffprobe_scan_for_duration(payload)
    else:
        print(f"ffprobe fail:\n{process.stderr}")
        raise RuntimeError("FFprobe failure")





def main():
    conn = sqlite3.connect(DB_FILENAME)
    songs = RepairParentSong(conn)
    for (record, song,) in songs:
        new_duration = fetch_ffprobe_duration(song)
        if new_duration is not None:
            print(song.name, record['id'], record['duration'], new_duration)
            RepairParentSong.Repair(conn, record['id'], new_duration)



if __name__ == "__main__":
    main()