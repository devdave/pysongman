"""
    I've found that QMediaPlayer's duration can be horribly wrong.
    So I am going to rely on ffprobe to get the duration and use that to compute tags and duration.

    https://blog.1a23.com/2020/03/16/read-and-write-tags-of-music-files-with-ffmpeg/

"""
import sys

import os
import json
import typing as T
import pathlib
import argparse

import delegator
from invoke import run


class AttrDict(dict):

    def __getattr__(self, name):
        return self.get(name, None)

    def __getitem__(self, item):
        return self.get(item, None)




class FFProbe:

    def __init__(self, song_path: T.Union[str, pathlib.Path]):

        self._env = dict(PATH=os.environ['PATH'])

        self.song_path = pathlib.Path(song_path)

        if self.song_path.exists() is False:
            raise ValueError(f"File path is wrong or song is missing: {self.song_path!r}")

        if self.song_path.is_file() is False:
            raise ValueError(f"Song path is not a valid file: {self.song_path!r}")

        if self.assure_ffprobe_on_path() is not True:
            raise RuntimeError("Unable to find ffprobe on OS PATH")

        self.all = AttrDict()
        self.metadata = AttrDict()
        self.info = AttrDict()
        self.format = AttrDict()
        self.streams = AttrDict()



    @classmethod
    def Load(cls, song_path: T.Union[str, pathlib.Path]):

        obj = cls(pathlib.Path(song_path))
        obj.probe_file()
        return obj


    def probe_file(self) -> None:
        r"""
        ffprobe
            -show_format
            -hide_banner
            -print_format json
            {song_path}
        Returns:
        """

        cmd = f"ffprobe -show_format -show_streams -hide_banner -print_format json \"{self.song_path}\""
        res = delegator.run(cmd, env=self._env)

        # res = delegator.run(cmd, env=self._env)
        res = run(cmd, hide=True, env = self._env)
        if res.return_code != 0:
            print(res.err)
            raise RuntimeError("Failed processing song")

        data = json.loads(res.out) # type: dict
        data = json.loads(res.stdout) # type: dict
        self.all = data
        self.info = AttrDict(data.get("format"))
        self.format = AttrDict(data.get("format"))
        self.streams = data.get("streams")
        self.metadata = AttrDict(self.info.get("tags", {}))


    def assure_ffprobe_on_path(self):


        p = delegator.run("ffprobe -hide_banner -version", env=self._env)

        if p.return_code != 0:
            print(p.err)
            raise ValueError(f"Shit has gone wrong with ffprobe: {p.err}")

        p.kill()
        return True if p.return_code == 0 else False


    @property
    def duration(self):
        return float(self.info.duration) if self.info.duration is not None else 0

    @property
    def duration_ms(self):
        """
            ff* gives me seconds so this should be easy.
        Returns:
        """
        return self.duration * 1000

    @property
    def duration_str(self):
        duration = self.duration
        seconds = int(duration % 60)
        minutes = int(duration / 60)

        return f"{minutes}:{seconds:02}"

    @property
    def listing(self):
        if self.metadata.artist and self.metadata.track:
            return f"{self.metadata.artist} - {self.metadata.title}"
        else:
            name, _ = self.song_path.name.split(".", 1)
            return name



def main(song_path):
    probe = FFProbe(song_path)

    print(f"{probe.duration_ms=}")
    print(f"{probe.duration_str=}")
    print(f"{probe.listing=}")

    print("Info")
    print("-" * 80)
    for k, v in probe.info.items():
        print(f"{k}: {v}")

    print()
    print("Meta")
    print("-" * 80)
    for k, v in probe.metadata.items():
        print(f"{k}: {v}")




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("song_file")
    parser.add_argument('--ffprobe_dir')
    args = parser.parse_args()

    main(pathlib.Path(args.song_file))

