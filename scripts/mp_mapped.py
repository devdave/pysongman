import multiprocessing as mp
import subprocess
import sys
import time

import orjson

import pathlib
import queue

import tap
from sqlalchemy.orm import Session

from PySongMan.lib.models import db_with, Song, Library, Tag


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
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return orjson.loads(res.stdout)


class Missing:
    """
    Sentinel meant for checking if a return value is missing.
    This allows setting a variable to None if desired while still being able to
    track if there was no match.
    """

    pass


def try_title(tag_dict, element: pathlib.Path):
    """
    Custom title finder.

    Largely my library is <lib path>/<artist name>/<album name>/#_title

    :param tag_dict:
    :param element:
    :return:
    """
    title = key_try(
        tag_dict,
        "TITLE",
        "title",
        "NAME",
        "name",
        default=Missing(),
    )

    if isinstance(title, Missing):
        title = element.name

    return title


def try_artist(tag_dict, element: pathlib.Path):
    """
    Largely my library is <lib path>/<artist name>/<album name>/#_title

    :param tag_dict:
    :param element:
    :return:
    """
    artist = key_try(
        tag_dict,
        "ARTIST",
        "artist",
        "album_artist",
        default=Missing(),
    )

    if isinstance(artist, Missing):
        if element.parent.name.lower() != "unsorted":
            artist = element.parent.parent.name
        else:
            artist = element.name

    return artist


def process_song(session: Session, library_id, element: pathlib.Path):

    if element.suffix not in [".mp3", ".mp4", ".ogg"]:
        print(f"Skipping {element.suffix}")
    else:
        try:
            result = ffprobe(element)
        except subprocess.CalledProcessError:
            print(f"ffprobe failed: {element=} ")

        else:
            try:
                tag_dict = result["streams"][0].get("tags", {})
                artist = try_artist(tag_dict, element)
                title = try_title(tag_dict, element)

                song = Song(
                    name=title,
                    artist=artist,
                    size=result["format"].get("size", 0),
                    length_seconds=key_try(result["format"], "duration", default=0),
                    file_name=element.name,
                    path=str(element),
                    codec=key_try(result["streams"][0], "codec_name", default=""),
                    format=key_try(result["format"], "format_name", default=""),
                    library_id=library_id,
                )
                for mname, mvalue in tag_dict.items():
                    tag = Tag(name=mname.lower(), value=mvalue)
                    song.tags.append(tag)

                session.add(song)

            except KeyError as e:
                print(
                    f"Meta failure: {e} for {element} ",
                    result["streams"][0].get("tags", {}).keys(),
                )


def key_try(src, *keys, default=None):
    for key in keys:
        if key in src:
            return src[key]

    return default


def handler(
    db_path: str | pathlib.Path,
    library_id: int,
    workq: mp.JoinableQueue,
    worker_id: str,
    counter: mp.Value,
):
    start_time = time.monotonic()
    processed = 1

    try:
        with db_with(db_path) as session:

            try:
                processed = worker(session, library_id, workq, worker_id, counter)
            except queue.Empty:
                session.commit()
            else:
                session.commit()

    except Exception as e:
        print(f"Handler exception: {e}")
        sys.exit(-1)
    finally:
        total_time = time.monotonic() - start_time
        print(f"Done -> {worker_id}: {total_time} seconds - {processed/total_time}")

    sys.exit(0)


def worker(
    session: Session,
    library_id: int,
    workq: mp.JoinableQueue,
    worker_id: int | str,
    counter: mp.Value,
):
    processed = 0

    while uow := pathlib.Path(workq.get(True, 10)):
        for element in uow.iterdir():  # type: pathlib.Path
            if element.is_dir():
                workq.put(str(element))
            else:
                try:
                    process_song(session, library_id, element)
                except Exception as e:
                    print(f"{worker_id} Unexpected error: ", str(e))

                processed += 1
                if processed % 100 == 0:
                    session.flush()
                elif processed % 10 == 0:
                    counter.value += 10

        session.commit()
        workq.task_done()

    return processed


class Arguments(tap.Tap):

    seed_path: str
    db_path: str = "sqlite:///../pysongman.sqlite3"


def import_library(seed, db_path):

    workq = mp.JoinableQueue()

    library_id = None
    with db_with(db_path, create=True) as session:
        library = Library.GetOrCreate(session, path=str(seed))
        session.add(library)
        session.commit()
        library_id = library.id

        print(f"Library ID: {library_id}")

        print("Seeding queue")
        start = time.monotonic()
        for element in seed.iterdir():
            if element.is_dir():
                workq.put(str(element))
            else:
                try:
                    process_song(session, library_id, element)
                except Exception as exc:
                    print(f"Failed {element} due to {type(exc)}:{exc=}")
                    raise

        session.commit()

    counter = mp.Value("i", 0)

    pool = []
    print("Generating pool")
    for worker_id in range(mp.cpu_count() - 2):
        p = mp.Process(
            target=handler,
            args=(
                db_path,
                library_id,
                workq,
                worker_id,
                counter,
            ),
        )
        p.start()
        pool.append(p)

    time.sleep(2)

    while workq.empty() is False:
        print(f"Waiting for work to finish: {workq.qsize()}:{counter.value}")
        time.sleep(4)
        if any((p.exitcode is None for p in pool)) is False:
            print("All children are dead")
            sys.exit(-1)

    print("Queue is empty")
    workq.join()
    print(f"Work finished: {time.monotonic()-start} {workq.qsize()}:{counter.value}")


def main():

    args = Arguments().parse_args()

    seed = pathlib.Path(args.seed_path)
    db_path = args.db_path

    if seed.is_dir() is False or seed.exists() is False:
        raise RuntimeError(f"Seed path {seed=} does not exist")

    import_library(seed, db_path)


if __name__ == "__main__":
    main()
