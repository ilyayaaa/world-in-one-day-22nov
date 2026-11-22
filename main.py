"""Write the day's front page to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

The picture is pre-rendered by tools/build.py; this program only copies it,
using the standard library and paths taken from this file's location.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
