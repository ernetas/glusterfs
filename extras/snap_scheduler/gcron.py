#!/usr/bin/env python
#
# Copyright (c) 2015 Red Hat, Inc. <http://www.redhat.com>
# This file is part of GlusterFS.
#
# This file is licensed to you under your choice of the GNU Lesser
# General Public License, version 3 or any later version (LGPLv3 or
# later), or the GNU General Public License, version 2 (GPLv2), in all
# cases as published by the Free Software Foundation.

from __future__ import print_function
import subprocess
import os
import os.path
import sys
import time
import logging
import logging.handlers
import fcntl


GCRON_TASKS = "/var/run/gluster/snaps/shared_storage/glusterfs_snap_cron_tasks"
GCRON_CROND_TASK = "/etc/cron.d/glusterfs_snap_cron_tasks"
LOCK_FILE_DIR = "/var/run/gluster/snaps/shared_storage/lock_files/"
log = logging.getLogger("gcron-logger")
start_time = 0.0


def initLogger(script_name):
    log.setLevel(logging.DEBUG)
    logFormat = "[%(asctime)s %(filename)s:%(lineno)s %(funcName)s] "\
        "%(levelname)s %(message)s"
    formatter = logging.Formatter(logFormat)

    sh = logging.handlers.SysLogHandler()
    sh.setLevel(logging.ERROR)
    sh.setFormatter(formatter)

    process = subprocess.Popen(["gluster", "--print-logdir"],
                               stdout=subprocess.PIPE)
    out, err = process.communicate()
    if process.returncode == 0:
        logfile = os.path.join(out.strip(), script_name[:-3]+".log")

    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    log.addHandler(sh)
    log.addHandler(fh)


def takeSnap(volname=""):
    success = True
    if volname == "":
        log.debug("No volname given")
        return False

    timeStr = time.strftime("%Y%m%d%H%M%S")
    cli = ["gluster",
           "snapshot",
           "create",
           "%s-snapshot-%s %s" % (volname, timeStr, volname)]
    log.debug("Running command '%s'", " ".join(cli))

    p = subprocess.Popen(cli, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    rv = p.returncode

    log.debug("Command '%s' returned '%d'", " ".join(cli), rv)

    if rv:
        log.error("Snapshot of %s failed", volname)
        log.error("Command output:")
        log.error(err)
        success = False
    else:
        log.info("Snapshot of %s successful", volname)

    return success


def doJob(name, lockFile, jobFunc, volname):
    success = True
    try:
        f = os.open(lockFile, os.O_RDWR | os.O_NONBLOCK)
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            mtime = os.path.getmtime(lockFile)
            global start_time
            log.debug("%s last modified at %s", lockFile, time.ctime(mtime))
            if mtime < start_time:
                log.debug("Processing job %s", name)
                if jobFunc(volname):
                    log.info("Job %s succeeded", name)
                else:
                    log.error("Job %s failed", name)
                    success = False
                os.utime(lockFile, None)
            else:
                log.info("Job %s has been processed already", name)
            fcntl.flock(f, fcntl.LOCK_UN)
        except IOError as (errno, strerror):
            log.info("Job %s is being processed by another agent", name)
        os.close(f)
    except IOError as (errno, strerror):
        log.debug("Failed to open lock file %s : %s", lockFile, strerror)
        log.error("Failed to process job %s", name)
        success = False

    return success


def main():
    script_name = os.path.basename(__file__)
    initLogger(script_name)
    global start_time
    if sys.argv[1] == "--update":
        if os.lstat(GCRON_TASKS).st_mtime > \
           os.lstat(GCRON_CROND_TASK).st_mtime:
            try:
                process = subprocess.Popen(["touch", "-h", GCRON_CROND_TASK],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                out, err = process.communicate()
                if process.returncode != 0:
                    log.error("Failed to touch %s. Error: %s.",
                              GCRON_CROND_TASK, err)
            except IOError as (errno, strerror):
                log.error("Failed to touch %s. Error: %s.",
                          GCRON_CROND_TASK, strerror)
        return

    volname = sys.argv[1]
    locking_file = os.path.join(LOCK_FILE_DIR, sys.argv[2])
    log.debug("locking_file = %s", locking_file)
    log.debug("volname = %s", volname)

    start_time = int(time.time())

    doJob("Snapshot-" + volname, locking_file, takeSnap, volname)


if __name__ == "__main__":
    main()
