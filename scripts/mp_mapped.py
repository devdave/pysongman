import multiprocessing as mp
import subprocess
import time

import orjson

import pathlib


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


def worker(workq: mp.JoinableQueue, worker_id, counter):
    processed = 0

    try:
        while uow := pathlib.Path(workq.get(True, 10)):
            for element in uow.iterdir():  # type: pathlib.Path
                if element.is_dir():
                    workq.put(str(element))
                else:
                    try:
                        ffprobe(element)
                        processed += 1
                        if processed % 100 == 0:
                            print(f"{worker_id}: Processed {processed} songs")
                        elif processed % 10 == 0:
                            counter.value += 10
                    except subprocess.CalledProcessError:
                        print(f"Failed: {element=} ")

            workq.task_done()
    except Exception as e:
        # print(f"Uncaught exception: {e}")
        pass

    print(f"{worker_id} processed {processed} songs")


def main():
    workq = mp.JoinableQueue()

    seed = pathlib.Path(r"C:\Users\lived\Google Drive Streaming\My Drive\music_new_era")

    print("Seeding queue")
    start = time.monotonic()
    for element in seed.iterdir():
        if element.is_dir():
            workq.put(str(element))
        else:
            try:
                ffprobe(element)
            except subprocess.CalledProcessError:
                print(f"Failed: {element=} ")

    counter = mp.Value("i", 0)

    pool = []
    print("Generating pool")
    for id in range(mp.cpu_count() - 1):
        p = mp.Process(
            target=worker,
            args=(
                workq,
                id,
                counter,
            ),
        )
        p.start()
        pool.append(p)

    time.sleep(2)

    while workq.empty() is False:
        print(f"Waiting for work to finish: {workq.qsize()}:{counter.value}")
        time.sleep(4)

    print("Queue is empty")
    workq.join()
    print(f"Work finished: {time.monotonic()-start} {workq.qsize()}:{counter.value}")


if __name__ == "__main__":
    main()
