import cython
import subprocess
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
