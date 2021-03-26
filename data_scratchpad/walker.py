import sys
import argparse
import pathlib


def walker(root_dir:str) -> None:
    """

    Args:
        root_dir: A valid root directory to look for music

    Returns: None

    """
    print(f"Processing {root_dir=}")
    path = pathlib.Path(root_dir)
    if path.exists() is False or path.is_dir() is False:
        raise RuntimeError(f"{path} is not a valid directory")

    for element in path.iterdir():
        if element.is_dir() is True:
            yield from walker(element)
        else:
            yield element







def main(argv):
    parser = argparse.ArgumentParser(description="Walk over a directory of directories containing muisc")
    parser.add_argument("root_dir")
    args = parser.parse_args(argv[1:])
    for file in walker(args.root_dir):
        print(f"FOUND: {file=}")


if __name__ == "__main__":
    main(sys.argv)