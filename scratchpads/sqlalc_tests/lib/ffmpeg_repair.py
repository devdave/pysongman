from pathlib import Path
import logging

import delegator
from invoke import run, UnexpectedExit
from .ffprobe import FFProbe

log = logging.getLogger(__name__)

class FFMpegRepair:

    source: Path
    dest: Path

    def __init__(self, source: Path, dest: Path):
        self.source = source
        self.dest = dest

    def do(self):
        """

        """

        cmd = f"ffmpeg -i \"{self.source}\" -y -vn -acodec copy \"{self.dest}\""

        # proc = delegator.run(cmd)
        try:
            proc = run(cmd, hide=True)
        except UnexpectedExit as exc:
            print(exc)
            return False

        if proc.return_code != 0:
            raise RuntimeError("ffmpeg repair failed")

        return proc.return_code == 0

    def verify(self):
        dest_probe = FFProbe.Load(self.dest)
        src_probe = FFProbe.Load(self.source)

        if None in (dest_probe.info['duration'], src_probe.info['duration'],):
            return False
        else:
            log.debug(self.dest)
            log.debug(f"{dest_probe.info['duration']=} vs {src_probe.info['duration']=}")

        if dest_probe.info['nb_streams'] != 1:
            return False

        return dest_probe.info['duration'] == src_probe.info['duration']
