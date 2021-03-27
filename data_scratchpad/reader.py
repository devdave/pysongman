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
    albumartist:str
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
        round_minutes = int(self.duration_minutes)
        remainder = int((self.duration_minutes - int(self.duration_minutes))*60)
        return f"{round_minutes}:{remainder:02d}"



def read(filepath:pathlib.Path):
    tags = tinytag.TinyTag.get(filepath) # type: tinytag.TinyTag

    # DONE - handle scenario where title is missing or none
    title = filepath.name if tags.title is None or tags.title.strip() == "" else tags.title
    # TODO - handle scenario where albumartist is missing or none
        # fallback to artist
            # fallback to filepath parent directory name

    return Song(title, tags.track, tags.albumartist, tags.album, tags.filesize, tags.duration, filepath.name, None)





def main(song_path:str):
    path = pathlib.Path(song_path)
    song = read(path)

    assert song.artist is not None

    print("Tags")
    for k,v in dataclasses.asdict(song).items():
        print(f"\t {k}={v!r}")

    print()
    print("Durations")
    print(f"\t{song.duration}")
    print(f"\t{song.duration_minutes=}")
    print(f"\t{song.duration_str=}")
    print()
    print("File sizes")
    print(f"\t{song.filesize=}")
    print(f"\t{song.filesize_kb=}")
    print(f"\t{song.filesize_mb=}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("song_path")

    args = parser.parse_args(sys.argv[1:])

    main(args.song_path)
