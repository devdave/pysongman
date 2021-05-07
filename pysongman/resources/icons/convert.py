import os
import pathlib

import delegator

HERE = pathlib.Path(__file__).parent

svgs = [file for file in HERE.iterdir() if file.is_file() and file.name.endswith(".svg")]


env = {"PATH": os.environ['PATH']}

# magick -background none play.svg play.png
for svg in svgs:
    clean_name, _ = svg.name.split(".", 1)
    new_name = f"{clean_name}.png"
    cmd = f"magick -background none {svg.name} {new_name}"
    print(cmd)
    p = delegator.run(cmd, env=env )
    if p.return_code != 0:
        print(p.err)
