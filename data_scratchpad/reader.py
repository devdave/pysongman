import math
import argparse
import sys
import tinytag
import pathlib
import dataclasses

@dataclasses.dataclass
class Song(object):
    title:str
    track:str
    artist:str
    album:str
    filesize:int
    duration:int

    filename:str
    parent_dir:str

    @property
    def filesize_kb(self):
        return self.filesize / 1024

    @property
    def filesize_mb(self):
        return self.filesize_kb / 1024

    @property
    def duration_minutes(self):
        return self.duration / 60

    @property
    def duration_str(self):
        remainder = (self.duration_minutes - int(self.duration_minutes))*60
        return f"{self.duration_minutes}:{remainder:02d}"



def read(filepath:pathlib.Path):
    tags = tinytag.TinyTag.get(filepath) # type: tinytag.TinyTag

    return Song(tags.title, tags.track, tags.artist, tags.album, tags.filesize, tags.duration, filepath.name, None)





def main(song_path:str):
    path = pathlib.Path(song_path)
    song = read(path)

    assert song.artist is not None

    for k,v in dataclasses.asdict(song).items():
        print(f"\t {k}={v!r}")

    print(\t"Durations")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("song_path")

    args = parser.parse_args(sys.argv[1:])

    main(args.song_path)
