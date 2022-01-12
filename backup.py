#!/usr/bin/python3

"""Backup most of a filesystem to a backup disk, using rsync."""

import subprocess
import time
import os

SOURCE = "/"
DESTINATION = "/mnt/backup"
EXCLUDES = [
    "/proc",
    "/sys",
    "/lost+found",
    "/mnt",
    "/media",
    "/tmp",
    "/var/run",
    "/var/lock",
    "/home/dripton/download",
]
RSYNC = "/usr/bin/rsync"
MOUNT = "/bin/mount"
UMOUNT = "/bin/umount"

def mount_backup_disk():
    cmd = [MOUNT]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, unused = proc.communicate()
    if DESTINATION in stdout.decode():
        print("%s already mounted" % DESTINATION)
        return
    cmd = [MOUNT, DESTINATION]
    returncode = subprocess.call(cmd)
    print("%s returned %d" % (cmd, returncode))

def umount_backup_disk():
    cmd = [UMOUNT, DESTINATION]
    returncode = subprocess.call(cmd)
    print("%s returned %d" % (cmd, returncode))

def find_latest_destdir():
    latest = 0
    for fn in os.listdir(DESTINATION):
        if fn.isdigit() and len(fn) == 14:
            timestamp = int(fn)
            latest = max(timestamp, latest)
    if latest:
        return str(latest)
    return None

def do_rsync():
    cmd = [RSYNC]
    cmd.append("-ab")
    for exclude in EXCLUDES:
        cmd.append("--exclude=%s" % exclude)
    latest = find_latest_destdir()
    if latest:
        cmd.append("--link-dest=%s" % (os.path.join(DESTINATION, latest)))
    cmd.append(SOURCE)
    timestamp = time.strftime("%Y%m%d%H%M%S")
    cmd.append(os.path.join(DESTINATION, timestamp))
    print(cmd)
    returncode = subprocess.call(cmd)
    print("%s returned %d" % (cmd, returncode))

def main():
    mount_backup_disk()
    do_rsync()
    umount_backup_disk()


if __name__ == "__main__":
    main()
