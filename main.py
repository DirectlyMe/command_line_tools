#!/anaconda3/bin/python
import argparse
import subprocess
from pathlib import Path
import time


def main():
    args = getArgs()

    localTime = time.asctime(time.localtime(time.time()))
    backupDir = Path(f"{args.directory}/backup_{args.user}_{localTime}")

    files = subprocess.run(["ls", "./"], text=True,
                           capture_output=True).stdout.split("\n")

    if (backupDir.is_dir() is False):
        subprocess.run(["mkdir", backupDir])

    for file in files:
        if file.endswith("@.py") or file.endswith(".lock"):
            output = subprocess.run(
                ["cp", f"{args.directory}/{file}", backupDir],
                capture_output=True)
            print(output)


def getArgs():
    parser = argparse.ArgumentParser(
        description="Copy and log the contents of a directory")

    parser.add_argument(
        "-u", "--user", help="this attached to backup directory and log file")
    parser.add_argument(
        "-ld", "--logdest", help="log file path", default="/tmp", nargs="1"
    )
    parser.add_argument("directory", help="directory to backup", nargs="1")
    parser.parse_args("a --logdest x".split())

    args = argparse.Namespace(directory="a", logdest="x")

    return args


if __name__ == "__main__":
    main()
