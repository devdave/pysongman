import pathlib


import subprocess
import time

import orjson

from PySongMan.lib.models import Song, Library, db_with


def ffprobe(path):
    cleaned = str(path).replace("\\", "/")
    res = subprocess.run(
        [
            "ffprobe",
            "-hide_banner",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            cleaned,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return orjson.loads(res.stdout)


def find_music(parent: pathlib.Path):
    for elm in parent.iterdir():
        if elm.is_dir():
            yield from find_music(elm)
        elif elm.is_file():
            yield ffprobe(elm)


with db_with(db_url="sqlite:///../pysongman.sqlite3", create=True) as session:

    p = pathlib.Path(r"C:\Users\lived\Google Drive Streaming\My Drive\music_new_era")

    idx = 0
    timer = time.time()
    total = 0
    for data in find_music(p):
        idx += 1
        if idx % 100 == 0:
            total += time.time() - timer
            print(idx, time.time() - timer)
            timer = time.time()

    print(idx, total)
    # print(
    #     elm.name,
    #     data["format"]["duration"],
    #     data["format"]["size"],
    #     data["streams"][0]["tags"].get("ARTIST", "missing"),
    #     data["streams"][0]["tags"].get("TITLE", "missing"),
    # )
