"""
    Point of entry for the app.
"""

import logging
import pathlib
import subprocess
import multiprocessing as mp

import time
from pathlib import Path
from wsgiref.simple_server import make_server
import sys

import flask
from werkzeug import wsgi

import tap
import webview  # type: ignore

from PySongMan.lib.models import get_scoped_session
from lib.api import API
from lib.application import App


IS_FROZEN = getattr(sys, "frozen", False)

LOG = logging.getLogger(__name__)
HERE = Path(__file__).parent if IS_FROZEN is False else Path(sys.executable).parent
UI_DIR = (HERE / "ui") if (HERE / "ui").exists() else (HERE / ".." / "ui")


class Arguments(tap.Tap):
    """
    PySongMan Python & ReactJS Music player
    """

    debug: bool = False
    port: str = "9000"


def setup_logging(level=logging.DEBUG):
    """
    Setup logging so that it prints to console with the provided level

    :param level:
    :return:
    """
    root = logging.getLogger(__name__)
    lib = logging.getLogger("lib")

    root.setLevel(level)
    lib.setLevel(level)

    console = logging.StreamHandler()
    console.setLevel(level)

    basic_format = logging.Formatter(
        "%(levelname)s - %(name)s.%(funcName)s@%(lineno)s - %(message)s"
    )
    console.setFormatter(basic_format)

    root.addHandler(console)
    lib.addHandler(console)

    root.info("Logging enabled")


def spinup_pnpm(url_path: pathlib.Path, port: str):
    """
    For debugging start the pnpm start/dev script

    :param url_path:
    :param port:
    :return:
    """
    ui_dir = url_path
    LOG.debug(
        f"Spinup CWD {ui_dir}",
    )

    process = subprocess.Popen(
        ["pnpm", "dev", "--port", port, "--host"],
        cwd=str(ui_dir),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )

    status = process.poll()
    if status is not None:
        raise RuntimeError(f"pnpm failed to run {status}")

    time.sleep(2)

    return process


def run_flask(ui_dir: pathlib.Path, port: str):
    DIST_DIR = ui_dir / "dist"
    if DIST_DIR.exists() is False:
        raise RuntimeError(f"Dist dir does not exist @ {ui_dir}")

    app = flask.Flask(__name__)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        file_path = DIST_DIR / path
        if (
            file_path.exists()
            and file_path.is_relative_to(DIST_DIR)
            and file_path.is_file()
        ):
            return flask.send_file(file_path)

        return (DIST_DIR / "index.html").read_text()

    with make_server("127.0.0.1", int(port), app) as httpd:
        httpd.serve_forever()

    app.run(host="127.0.0.1", port=int(port))


def spinup_flask(ui_dir: pathlib.Path, port: str) -> mp.Process:
    worker = mp.Process(target=run_flask, args=(ui_dir, port))
    worker.start()
    return worker


def transform_api(dest: pathlib.Path):
    from lib import transformer

    dest.touch(exist_ok=True)

    app_types_str = transformer.process_types_source(
        HERE / "lib/app_types.py", UI_DIR / "src/lib/app_types.ts"
    )

    transformer.process_source(
        (HERE / "lib/api.py"),
        dest,
        header=app_types_str,
    )


def main():

    app = App()
    api = API(app=app)

    args = Arguments().parse_args()

    print(f"{args=}")
    print(f"{args.debug=}")
    print(f"{args.port=}")

    setup_logging()

    app = App(port=args.port, db_path="sqlite:///pysongman.sqlite3")
    api = API(app=app)

    if args.debug:
        transform_api(UI_DIR / "src/lib/api.ts")

    window_args = {
        "title": "PySongMan",
        "js_api": api,
        "url": f"http://127.0.0.1:{args.port}/",
    }

    worker = (
        spinup_pnpm(UI_DIR, args.port)
        if args.debug
        else spinup_flask(UI_DIR, args.port)
    )

    app.main_window = webview.create_window(**window_args)

    webview.start(debug=args.debug)

    if args.debug:
        import signal

        LOG.debug("Stopping worker")
        worker.send_signal(signal.CTRL_BREAK_EVENT)
        worker.send_signal(signal.CTRL_C_EVENT)
        LOG.debug("Waiting for worker")
        time.sleep(2)

    else:
        LOG.debug("Stopping worker")
        worker.terminate()
        worker.kill()
        LOG.debug("Waiting for worker")
        worker.join()
        worker.close()

    sys.exit(0)


if __name__ == "__main__":
    main()
