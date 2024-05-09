import multiprocessing as mp
import pathlib

import asyncio
import subprocess
import time

import orjson


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


def worker(name, queue: mp.Queue):
    print(f"{name} started")

    while item := queue.get(timeout=2):
        ffprobe(pathlib.Path(item))
