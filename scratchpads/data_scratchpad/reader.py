import math
import argparse
import sys

import pathlib
import dataclasses

import tinytag
import mutagen

from db_repair_duration import fetch_ffprobe_duration


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

    try:
        tags = tinytag.TinyTag.get(filepath) # type: tinytag.TinyTag
        title = filepath.name if tags.title is None or tags.title.strip() == "" else tags.title

        if tags.album is None:
            album = filepath.parts[-2]
        else:
            album = tags.album

        if tags.albumartist is None:
            if tags.artist is not None:
                artist = tags.artist

            else:
                if "-" in filepath.name:
                    left, right = filepath.name.split("-", 1)
                    artist = left.strip()
                else:
                    artist = filepath.parts[-2]
                    artist += "-FIXME"
        else:
            artist = tags.albumartist

        if tags.duration <= 0:
            tags.duration = 0

        song = Song(title, tags.track, artist, album, tags.filesize, tags.duration, filepath.name, None)

    except TypeError:
        # TODO - Evaluate if mutagen should ALWAYS be used over tinytag
        media_info = mutagen.File(filepath)
        title = filepath.name if media_info.tags['title'] is None or media_info.tags['title'][0].strip() == "" else media_info.tags['title'][0]
        if 'albumartist' in media_info.tags:
            artist = media_info.tags['albumartist'][0]
        elif 'artist' in media_info.tags:
            artist = media_info.tags['artist'][0]
        else:
            if "-" in filepath.name:
                left,right = filepath.name.split("-", 1)
                artist = left.strip()
            else:
                artist = "UNKNOWN - FIXME!"

        if 'album' in media_info.tags:
            album = media_info.tags['album'][0]
        else:
            # /path/to/file.ext
            # -2 skips over the file.ext and "should" grab "to"
            album = filepath.parts[-2]

        if 'track' in media_info.tags:
            track = media_info.tags['track'][0]
        elif 'tracknumber' in media_info:
            track = media_info.tags['tracknumber'][0]
        elif "_" in filepath.name:
            left,right = filepath.name.split("_", 1)
            try:
                track = int(left.strip)
            except TypeError:
                track = 0

        else:
            track = 0


        # TODO - For 16 Volt - Skin the length is a negative number
        duration = media_info.info.length






        song = Song(title,
                    track,
                    artist,
                    album,
                    filepath.stat().st_size,
                    duration,
                    filepath.name,
                    None)

    if song.duration <= 1:
        # For some reason samplerate isn't being found for some ogg files.
        print(f"DURATION ISSUE - {filepath=}")
        song.duration = fetch_ffprobe_duration(filepath)

    if isinstance(song.track, str) and "/" in song.track:
        song.track, _ = song.track.split("/", 1)

    return song





def main(song_path:str):
    path = pathlib.Path(song_path)
    song = read(path)

    if song.artist is None:
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
