import enum
import logging
import pathlib

import taglib
import tinytag
import mutagen

from .ffprobe import FFProbe


class TagSource(enum.Enum):
    ERROR = enum.auto()
    tag = enum.auto()
    tiny = enum.auto()
    muta = enum.auto()
    ffprobe = enum.auto()


class SongCache:

    _CACHE = {}

    @classmethod
    def has(cls, song_path):
        return song_path in cls._CACHE

    @classmethod
    def get(cls, song_path):
        return cls._CACHE[song_path]

    @classmethod
    def set(cls, song_path, data):
        cls._CACHE[song_path] = data



class SongInfo:

    def __init__(self, song_file):

        self.data = dict()

        self.song_file = pathlib.Path(song_file)
        self.source = TagSource.ERROR

        def safe_first(val):
            try:
                return val[0]
            except IndexError:
                if isinstance(val, list):
                    return None
                else:
                    return val

        if SongCache.has(song_file):
            self.data = SongCache.get(song_file)
        else:

            try:
                # taglib opens some but not all files in an exclusive like lock
                #  which is somewhat problematic.
                #  That said it is one of the best id3 parsers I can get my hands on.
                self.meta = taglib.File(self.song_file.as_posix())
                try:
                    self.data['artist'] = safe_first(self.meta.tags.get('ARTIST', [None]))
                    self.data['album'] =  safe_first(self.meta.tags.get("ALBUM", [None]))
                    self.data['title'] = safe_first(self.meta.tags.get("TITLE", [None]))
                    self.data['length'] = self.meta.length
                    self.meta.close()
                except IndexError as iex:
                    logging.exception()

                self.source = TagSource.tag
            except OSError as ose:
                self.meta = FFProbe.Load(self.song_file.as_posix())

                self.data['artist'] = self.meta.metadata.get("artist")
                self.data['album'] = self.meta.metadata.get("album")
                self.data['title'] = self.meta.metadata.get("title")
                self.data['length'] = self.meta.info['duration']


                self.source = TagSource.ffprobe

            SongCache.set(song_file, self.data)

    @property
    def duration(self):
        return self.data['length'] if isinstance(self.data['length'], float) else float(self.data['length'])


    @property
    def artist(self):
        if self.data['artist'] is not None:
            return self.data['artist']
        else:
            if "-" in self.song_file.name:
                guess, _ = pathlib.Path(self.song_file).stem.split("-", 1)
                return guess
            else:
                # Given Artist Feat. Blah - Song title.mp3 - stem is returning "Artist Feat"
                name, _ = pathlib.Path(self.song_file).name.rsplit(".", 1)
                return name

    @property
    def title(self):
        if self.data['title'] is not None:
            return self.data["title"]
        else:
            name, _ = self.song_file.name.rsplit(".", 1)
            if "-" in self.song_file.name:
                # assume Artist - Title
                _, title = name.rsplit("-", 1)
                return title
            else:
                return name



    @property
    def duration_str(self):
        seconds = int(self.duration % 60)
        minutes = int(self.duration / 60)
        return f"{minutes}:{seconds:02}"

    @property
    def duration_ms(self):
        return self.duration * 1000

    @property
    def listing(self):
        artist = self.artist
        title = self.title

        if None in [artist, title]:
            return self.song_file.stem
        else:
            return f"{artist} - {title}"



