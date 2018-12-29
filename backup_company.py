#! /usr/local/bin/python3
import argparse
import subprocess
import requests
from pathlib import Path
import time


def main():
    args = getArgs()

    userFiles = checkFiles(args)

    files = subprocess.run(["ls", args.directory],
                           text=True,
                           capture_output=True).stdout.split("\n")

    f = open(userFiles["bkLogFile"], "w")

    for file in files:
        if file.endswith(".py") or file.endswith(".lock"):
            output = subprocess.run(
                ["cp", f"{args.directory}/{file}", userFiles["bkDir"]],
                capture_output=True)

            localTime = userFiles["localTime"]
            f.write(f"{file} copied at {localTime} with output: {output}")
            f.write("\n")

            print(file)

    userInput = input(
        "Would you like to add attach this log to a ticket? Y/N: ")
    
    if userInput.upper() == "Y":
        ticketId = input("Enter the ticket Id: ")
        print("Uploading now...")

        req = requests.get("http://www.google.com")
        print(req)


def getArgs():
    parser = argparse.ArgumentParser(
        description="Copy and log the contents of a directory")

    parser.add_argument(
        "-u", "--user", help="this attached to backup directory and log file")
    parser.add_argument(
        "-lp", "--logPath", help="log path", default="/tmp/backup")
    parser.add_argument("directory", help="directory to backup")

    args = parser.parse_args()

    return args


def checkFiles(args):
    localTime = time.asctime(time.localtime(time.time()))
    backupDirectory = Path(f"{args.directory}/backup_{args.user}")
    logDirectory = Path(f"{args.logPath}")
    backupLogFile = Path(f"{args.logPath}/log_{args.user}_{localTime}.log")

    if (backupDirectory.is_dir() is False):
        subprocess.run(["mkdir", backupDirectory])

    if (logDirectory.is_dir() is False):
        subprocess.run(["mkdir", logDirectory])

    if (backupLogFile.is_file() is False):
        subprocess.run(["touch", backupLogFile])
        subprocess.run(["chmod", "666", backupLogFile])

    return {
        "localTime": localTime,
        "bkDir": backupDirectory,
        "logDir": logDirectory,
        "bkLogFile": backupLogFile
    }


if __name__ == "__main__":
    main()
