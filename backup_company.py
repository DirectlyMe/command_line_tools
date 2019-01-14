import argparse
import asyncio
import requests
import subprocess
import time
import re
from pathlib import Path
from typing import Dict, List


async def main():
    args = getArgs()

    userFiles = setupFiles(args)

    isSuccessful = backupFiles(args, userFiles)

    if isSuccessful:
        userInput: str = input(
            "Would you like to add attach this log to a ticket? Y/N: ")

        if userInput.upper() == "Y":
            updateTicket()
    else:
        print("Backup failed, check error logs for more info.\n...exiting now")


def setupFiles(args: object) -> Dict({str: str}):
    localTime = time.asctime(time.localtime(time.time()))
    backupDirectory = Path(f"{args.directory}/backup_{args.user}")
    logDirectory = Path(f"{args.logPath}")
    backupLogFile = Path(f"{args.logPath}/log_{args.user}_{localTime}.log")

    try:
        if not backupDirectory.is_dir():
            subprocess.run(["mkdir", backupDirectory])

        if not logDirectory.is_dir():
            subprocess.run(["mkdir", logDirectory])

        if not backupLogFile.is_file():
            fileMode = "w"
            subprocess.run(["touch", backupLogFile])
            subprocess.run(["chmod", "666", backupLogFile])
        else:
            fileMode = "a"

        return {
            "fileMode": fileMode,
            "localTime": localTime,
            "bkDir": backupDirectory,
            "logDir": logDirectory,
            "bkLogFile": backupLogFile,
        }
    except Exception as err:
        print(err)
        raise Exception("Couldn't setup files", err)


def backupFiles(args: object, userFiles: Dict) -> bool:
    f = open(userFiles["bkLogFile"], userFiles["fileMode"])
    localTime = userFiles["localTime"]

    try:

        files: List = subprocess.run(["ls", args.directory],
                                     text=True,
                                     capture_output=True).stdout.split("\n")

        print("copying files...")

        for file in files:
            if re.search(args.regex, file):
                if args.recursive:
                    output = subprocess.run(
                        ["cp", f"{args.directory}/{file}", userFiles["bkDir"]],
                        capture_output=True,
                    )
                else:
                    output = subprocess.run(
                        [
                            "cp", "-r", f"{args.directory}/{file}",
                            userFiles["bkDir"]
                        ],
                        capture_output=True,
                    )

                f.write(f"{file} copied at {localTime} with output: {output}")
                f.write("\n")

        return True

    except Exception as err:
        f.write(f"{localTime}: {err}")
        print(err)

        return False


async def updateTicket() -> None:
    ticketId = input("Enter the ticket Id: ")
    print("Uploading now...")

    token = "b1f95f81d5760a6f76d867bdf3b5ec89"
    orgId = "664576196"

    # looks like we need a oauth token
    headers = {"Authorization": "Zoho-authtoken " + token, "orgId": orgId}
    req = requests.get(
        f"https://desk.zoho.com/api/v1/tickets/{ticketId}?" +
        "include=contacts,products,assignee,departments,team",
        headers=headers)
    print(req.text)


def getArgs() -> object:
    parser = argparse.ArgumentParser(
        description="Copy and log the contents of a directory")

    parser.add_argument(
        "-r",
        "--recursive",
        help="make the backup recursive",
        action="store_true")
    parser.add_argument(
        "-u", "--user", help="attached to backup directory and log file")
    parser.add_argument(
        "-lp",
        "--logPath",
        help="the directory to place the backup log in",
        default="/tmp/backup")
    parser.add_argument(
        "-reg",
        "--regex",
        help="add a regex expression to copy",
        default="(@.[r||x])")
    parser.add_argument("directory", help="directory to backup")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    asyncio.run(main())
