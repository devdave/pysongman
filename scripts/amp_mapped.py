import asyncio
import multiprocessing as mp
import subprocess
import sys
import time

import orjson

import pathlib
import queue

import tap
from sqlalchemy.orm import Session

from PySongMan.lib.models import db_with, Song, Library, Tag, async_db


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


async def affprobe(path):

    cleaned = str(path).replace("\\", "/").replace("//", "/")
    my_cmd = " ".join(
        [
            "ffprobe",
            "-hide_banner",
            "-print_format json",
            "-show_format",
            "-show_streams",
            f'"{cleaned}"',
        ]
    )

    proc = await asyncio.create_subprocess_shell(
        my_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, _ = await proc.communicate()

    return orjson.loads(stdout)


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

                print(f"Processing {element.name=}:{artist=}, {title=}")

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


async def aprocess_song(session: Session, library_id, element: pathlib.Path):

    if element.suffix.lower() not in [".mp3", ".mp4", ".ogg"]:
        print(f"Skipping {element.suffix}")
    else:
        try:
            result = await affprobe(element)
        except subprocess.CalledProcessError:
            print(f"ffprobe failed: {element=} ")

        else:
            try:
                tag_dict = result["streams"][0].get("tags", {})
                artist = try_artist(tag_dict, element)
                title = try_title(tag_dict, element)

                # print(f"Processing {element.name=}:{artist=}, {title=}")

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
        processed = asyncio.run(
            delegator(db_path, library_id, workq, worker_id, counter)
        )
    except asyncio.QueueEmpty:
        print(f"{worker_id} Queue empty")
    except Exception as e:
        print(f"Handler exception: {type(e)}{e}")
        sys.exit(-1)
    finally:
        total_time = time.monotonic() - start_time
        print(f"Done -> {worker_id}: {total_time} seconds - {processed/total_time}")

    sys.exit(0)


async def delegator(
    db_path: str | pathlib.Path,
    library_id: int,
    workq: mp.JoinableQueue,
    process_id: int | str,
    counter: mp.Value,
):

    song_queue = asyncio.Queue(maxsize=50)
    workers = []
    processed = 0

    for i in range(4):
        task = asyncio.create_task(
            worker(db_path, f"{process_id}-{i}", song_queue, library_id, counter)
        )
        workers.append(task)

    while uow := pathlib.Path(workq.get(True, 5)):
        for element in uow.iterdir():  # type: pathlib.Path
            if element.is_dir():
                workq.put(str(element))
            else:
                await song_queue.put(str(element))
                processed += 1

    print(f"{process_id} - waiting on song queue")
    await song_queue.join()

    for task in workers:
        task.cancel()

    return processed


async def worker(db_path, worker_id, song_queue: asyncio.Queue, library_id, counter):

    processed = 0

    try:
        async with async_db(f"sqlite+aiosqlite:///{db_path}", create=False) as session:
            try:
                while song_element := pathlib.Path(song_queue.get_nowait()):
                    try:
                        await asyncio.wait_for(
                            aprocess_song(session, library_id, song_element), timeout=4
                        )
                    except Exception as e:
                        print(f"{worker_id} Unexpected error: {type(e)}{e}")
                        # todo dead letter
                    else:
                        processed += 1
                        if processed % 10 == 0:
                            counter.value += 10
            except Exception as exc:
                print(f"{worker_id} queue error: {type(exc)}{exc}")
            finally:
                try:
                    await session.commit()
                except Exception as exc:
                    print(f"{worker_id} commit error: {type(exc)}{exc}")

    except Exception as e:
        print(f"{worker_id} Unexpected error: ", str(e))
    else:
        print(f"{worker_id} - finished")

    return processed


class Arguments(tap.Tap):

    seed_path: str
    db_path: str = "../pysongman.sqlite3"


def import_library(seed, db_path):

    workq = mp.JoinableQueue()

    library_id = None
    with db_with(f"sqlite:///{db_path}", create=True) as session:
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
    for worker_id in range(mp.cpu_count() - 1):
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
    print(f"Work finished: {time.monotonic() - start} {workq.qsize()}:{counter.value}")
    workq.join()


def main():

    args = Arguments().parse_args()

    seed = pathlib.Path(args.seed_path)
    db_path = args.db_path

    if seed.is_dir() is False or seed.exists() is False:
        raise RuntimeError(f"Seed path {seed=} does not exist")

    import_library(seed, db_path)


if __name__ == "__main__":
    main()
