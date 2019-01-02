from typing import Dict, List
from pathlib import Path
import argparse
import asyncio
import subprocess
import requests
import time


async def main():
    args = getArgs()

    userFiles: Dict = setupFiles(args)

    backupFiles(args, userFiles)

    userInput: str = input(
        "Would you like to add attach this log to a ticket? Y/N: ")

    if userInput.upper() == "Y":
        updateTicket()


def getArgs():
    parser = argparse.ArgumentParser(
        description="Copy and log the contents of a directory")

    parser.add_argument(
        "-r",
        "--recursive",
        help="make the backup recursive",
        action="store_true")
    parser.add_argument(
        "-u", "--user", help="this attached to backup directory and log file")
    parser.add_argument(
        "-lp",
        "--logPath",
        help="the directory to place the backup log in",
        default="/tmp/backup")
    parser.add_argument("directory", help="directory to backup")

    args = parser.parse_args()

    return args


def setupFiles(args) -> Dict:
    localTime = time.asctime(time.localtime(time.time()))
    backupDirectory = Path(f"{args.directory}/backup_{args.user}")
    logDirectory = Path(f"{args.logPath}")
    backupLogFile = Path(f"{args.logPath}/log_{args.user}_{localTime}.log")

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


def backupFiles(args, userFiles: Dict):
    files: List = subprocess.run(["ls", args.directory],
                                 text=True,
                                 capture_output=True).stdout.split("\n")

    f = open(userFiles["bkLogFile"], userFiles["fileMode"])

    print("copying files...")
    for file in files:
        if file.endswith(".py") or file.endswith(".lock"):
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

            localTime = userFiles["localTime"]
            f.write(f"{file} copied at {localTime} with output: {output}")
            f.write("\n")

            print(file)


def updateTicket():
    ticketId: str = input("Enter the ticket Id: ")
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


if __name__ == "__main__":
    asyncio.run(main())
