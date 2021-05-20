import sys
import argparse
import logging
from pathlib import Path

from sqlalchemy import or_, and_
from sqlalchemy.orm import SessionTransaction

from pybass3 import Song as BassSong
from pybass3 import BassException
from pybass3.bass_tags import BassTags

from .models import initialize_db, get_db, SAConnection
from .models.song import Song as SongModel
from .models.artist import Artist
from .models.album import Album
from .models.parent_dir import ParentDir

from .lib.ffprobe import FFProbe
from .lib.ffmpeg_repair import FFMpegRepair

log = logging.getLogger(__name__)

def setup_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def setup_db() -> SAConnection:
    db_location = Path(__file__).parent / "test.sqlite3"
    return initialize_db(db_location=db_location)

def fix_tags_main():
    conn = setup_db()
    for music in SongModel.query.filter(SongModel.title == None):
        probe = FFProbe.Load(music.path)
        try:
            tags = probe.streams[0]['tags']
            music.title = tags['TITLE']
            music.artist = Artist.GetCreate(tags['ARTIST'])
            music.album = Album.GetCreate(music.artist, tags['ALBUM'])
            conn.s.add(music)
            log.debug("Saving %s", music.path.name)
        except KeyError:
            log.error("%s is missing tag data %s", music.path.name, tags)
        else:
            log.debug("Flushing to DB")
            conn.s.commit()

    conn.s.commit()


def clean_missing():
    conn = setup_db()
    for music in SongModel.query.filter(SongModel.is_valid == False):
        if music.path.exists() is False:
            conn.s.delete(music)

    conn.s.commit()

def bass_validate():

    conn = setup_db()
    # statement = SongModel.query.filter(or_(SongModel.is_valid == False, SongModel.title == None))
    statement = SongModel.query
    log.debug("%s to process", statement.count())

    for music in statement:
        try:
            song = BassSong(music.path.as_posix())
            song.touch()
            log.debug("Processing %s", music.path)
        except BassException as exc:
            log.exception("Failed to load into BASS")
            music.is_valid = False
        else:
            music.length_seconds = song.duration
            music.length_bytes = song.duration_bytes
            music.title = song.tags['title']
            music.artist = Artist.GetCreate(song.tags['artist'])
            music.album = Album.GetCreate(music.artist, song.tags['album'])

        conn.s.add(music)

    conn.s.commit()


    log.debug(SongModel.query.filter(SongModel.is_valid == False).count())


def repair_main(repair_destination: Path):
    assert repair_destination.exists()

    conn = setup_db()

    dest_str = repair_destination.as_posix()
    repair_count = SongModel.query.filter(SongModel.is_valid == False).count()
    log.info("%d songs to repair", repair_count)

    for music in SongModel.query.filter(SongModel.is_valid == False):
        source = music.path # type: Path
        src_str = str(source.as_posix())
        full_dest = src_str.replace(music.parent.path.as_posix(), dest_str)
        log.debug(f"Would copy to `{full_dest}`")
        full_path = Path(full_dest)
        log.debug(f"{full_path.parent=} exists {full_path.parent.exists()}")
        if full_path.parent.exists() is False:
            full_path.parent.mkdir(parents=True, exist_ok=True)

        if full_path.exists() is False:
            source.replace(full_path)


def fix_main(copy_dir: Path):
    conn = setup_db()
    assert copy_dir.exists()
    copy_dir_str = copy_dir.as_posix()
    count = SongModel.query.filter(SongModel.is_valid is False).count()
    log.info("To fix %s", count)

    for music in SongModel.query.filter(SongModel.is_valid == False):
        copy_path = str(music.path.as_posix()).replace(music.parent.path.as_posix(), copy_dir_str)

        repair = FFMpegRepair(Path(copy_path), music.path)

        if repair.do() is True and repair.verify() is True:
            music.is_valid = True
            conn.s.add(music)
            conn.s.commit()



def get_audio_stream(probe: FFProbe):
    for stream in probe.streams:
        if stream['codec_type'] == "audio":
            return stream

    return None


def load_diagnose():
    conn = setup_db()
    has_video = 0
    has_dual = 0
    triple_stream = 0
    unicode_fail = 0
    total_invalid = SongModel.query.filter(SongModel.is_valid == False).count()

    for music in SongModel.query.filter(SongModel.is_valid == False):  # type: SongModel


        try:
            probe = FFProbe(music.path)
            # print("Processing: %s" % music.rel_path)
            probe.probe_file()
        except ValueError:
            if music.path.exists() is False:
                log.debug("Missing %s", music.path)
            else:
                raise
        except (UnicodeDecodeError, IndexError,) as exc:
            log.error("Failed with codec processing on %s", music.path)
            unicode_fail += 1
            music.invalid_reason = "unicode"


        else:

            if probe.format['nb_streams'] > 1:
                has_dual = True

            if probe.format['nb_streams'] > 2:
                triple_stream += 1
                log.debug("Triple %s", music.path)

            if has_dual is True:
                for stream in probe.streams:
                    if stream['codec_type'] == "video":
                        music.invalid_reason = "video"
                        has_video += 1
                        break

            # Find the audio stream
            if probe.info['duration'] is not None:
                music.length_seconds = probe.info['duration']

        if probe.info['duration'] is not None:
            music.length_seconds = probe.info['duration']

        audio_stream = get_audio_stream(probe)
        if audio_stream is not None:

            if "TITLE" in audio_stream['tags']:
                music.title = audio_stream['tags']['TITLE']

            if "ARTIST" in audio_stream['tags']:
                music.artist = Artist.GetCreate(audio_stream['tags']["ARTIST"])

            if "ALBUM" in audio_stream['tags'] and music.artist is not None:
                music.album = Album.GetCreate(music.artist, audio_stream['tags']['ALBUM'])


        if conn.s.is_modified(music):
            conn.s.add(music)

        if len(conn.s.dirty) > 100:
            conn.s.commit()

    conn.s.commit()

    print(f"{total_invalid=}")
    print(f"{has_video=}")
    print(f"{has_dual=}")
    print(f"{triple_stream=}")
    print(f"{unicode_fail=}")



def load_directory(song_path: Path, parent: ParentDir):
    conn = get_db()
    valid_types = [".mp3", ".mp4", ".ogg"]
    log.debug("Loading %s", song_path)
    files = (element for element in song_path.iterdir() if element.is_file() and element.suffix in valid_types)
    dirs = (element for element in song_path.iterdir() if element.is_dir())
    created = 0

    with conn.s.begin() as trx: # type: SessionTransaction
        for file in files:
            record, is_old = SongModel.GetCreateByPath(file, parent)
            if is_old is True:
                log.debug("Old song record %s found", record)
            else:
                log.debug("Adding %r to db", record)
                conn.s.add(record)
                if record.is_valid:
                    created += 1

    for file_dir in dirs:
        created += load_directory(file_dir, parent)

    return created


def shell_main():
    from .lib.ffprobe import FFProbe
    conn = setup_db()
    invalid = SongModel.query.filter(SongModel.is_valid == False).first() # type: SongModel

    probe = FFProbe.Load(invalid.path) if invalid else None
    import IPython; IPython.embed()


def destroy_main():
    log.info("Rebuilding DB")
    db_location = Path(__file__).parent / "test.sqlite3"
    if db_location.exists():
        db_location.unlink()
    conn = initialize_db(create=True, db_location=db_location)
    return

def load_main(song_dirs: [Path]):

    log.debug("SP %s", song_dirs)
    db_location = Path(__file__).parent / "test.sqlite3"
    conn = initialize_db(db_location=db_location)
    created = 0

    if len(song_dirs) == 0:
        raise ValueError("Must provide atleast one path")

    for song_dir in song_dirs:  # type: Path
        with conn.s.begin() as trx: # type: SessionTransaction
            parent = ParentDir.GetCreate(song_dir)
            if parent.id is None:
                conn.s.add(parent)

        created += load_directory(song_dir, parent)

    log.debug("Created %d new records", created)


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Commands", dest="command")

    load_parser = subparsers.add_parser("load", help="load data")
    load_parser.add_argument("song_paths", nargs="+", type=Path)

    destroy = subparsers.add_parser("destroy", help="Reset the database to blank slate")

    shell = subparsers.add_parser("shell", help="run embedded ipython terminal")

    diagnose = subparsers.add_parser("diagnose", help="Evaluate why BASS doesn't like these files")

    bas_val = subparsers.add_parser("bass")

    summarize_parser = subparsers.add_parser("summarize")

    repair_parser = subparsers.add_parser("repair")
    repair_parser.add_argument("repair_dir", type=Path)

    fix_parser = subparsers.add_parser("fix")
    fix_parser.add_argument("copied_dir", type=Path)

    clean_parser = subparsers.add_parser("clean")

    fix_tags_parser = subparsers.add_parser("fix_tags")

    args = parser.parse_args()
    if args.command == "load":
        load_main(args.song_paths)
    elif args.command == "destroy":
        destroy_main()
    elif args.command == "shell":
        shell_main()
    elif args.command == "diagnose":
        load_diagnose()
    elif args.command == "repair":
        repair_main(args.repair_dir)
    elif args.command == "fix":
        fix_main(args.copied_dir)
    elif args.command == "bass":
        bass_validate()
    elif args.command == "clean":
        clean_missing()
    elif args.command == "repair_fix":
        pass
    elif args.command == "fix_tags":
        fix_tags_main()
    else:
        raise ValueError("Unknown command %s" % args.command)
