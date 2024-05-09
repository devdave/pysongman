import pathlib

import asyncio
import subprocess
import time

import orjson

from PySongMan.lib.models import Song, Library, db_with


async def ffprobe(path):
    cleaned = str(path).replace("\\", "/")
    cmd = " ".join(
        [
            "ffprobe",
            "-hide_banner",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            f'"{cleaned}"',
        ]
    )

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )

    stdout, stderr = await proc.communicate()

    return orjson.loads(stdout)


counter = 0
lock = asyncio.Lock()


async def worker(name, queue):
    global counter, lock

    print(f"Worker {name} ready")
    uow = await queue.get()
    while uow is not None:
        p = pathlib.Path(uow)
        result = await ffprobe(p)
        # print(p.name)
        queue.task_done()

        try:
            await asyncio.wait_for(lock.acquire(), timeout=1)
            counter += 1
        except asyncio.TimeoutError:
            print(f"{name} - Failed to acquire lock")
        finally:
            lock.release()

        uow = await queue.get()


def find_music(parent: pathlib.Path):
    for elm in parent.iterdir():
        if elm.is_dir():
            yield from find_music(elm)

        yield elm


async def main():
    global counter, lock
    queue = asyncio.Queue(maxsize=500)

    workers = []
    for i in range(16):
        task = asyncio.create_task(worker(f"worker-{i}", queue))
        workers.append(task)

    timer = time.monotonic()
    idx = 0
    for file in find_music(
        pathlib.Path(r"C:\Users\lived\Google Drive Streaming\My Drive\music_new_era")
    ):
        await queue.put(file)
        idx += 1
        # print(f"{file.name} has been queued")
        if counter % 100 == 0 and counter >= 100:
            print(counter, {time.monotonic() - timer})
            timer = time.monotonic()

        if idx % 100 == 0:
            print(f"{idx=}")

    await queue.join()
    print(counter, {time.monotonic() - timer})

    for task in workers:
        task.cancel()

    print("workers cancelled")
    await asyncio.gather(*workers, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
