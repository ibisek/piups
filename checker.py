#!/usr/bin/python3

import os
import sys
import time
import signal
import threading


PID_FILE = "/tmp/piUps.pid"


class UpsCheckerThread(threading.Thread):
    doRun = True

    def __init__(self):
        super(UpsCheckerThread, self).__init__()

        signal.signal(signal.SIGTERM, self.sigtermHandler)  # listen for SIGTERM

    def isThisScriptAlreadyRunning(self):
        try:
            oldpid = open(PID_FILE, 'r').read()
            cmdline = open(os.path.join('/proc', str(oldpid), 'cmdline'), 'rb').read().decode('ascii')
            if sys.argv[0] in cmdline:
                return True
            else:
                return False

        except FileNotFoundError:  # not running with that old pid
            return False

    def createPidFile(self):
        open(PID_FILE, 'w+').write(str(os.getpid()))
        print("PID file created as {}".format(PID_FILE))

    def deletePidFile(self):
        if os.path.isfile(PID_FILE):
            os.remove(PID_FILE)
            print('PID file removed')

    def sigtermHandler(self, sigNum, frame):
        print("SIGTERM requested")
        self.doRun = False

    def run(self):
        if self.isThisScriptAlreadyRunning():
            print("One instance already running. Exiting..")
            sys.exit(1)

        self.createPidFile()
        print('Started with PID', os.getpid())

        while self.doRun:
            print("T")
            time.sleep(1)

        self.deletePidFile()


if __name__ == "__main__":
    t = UpsCheckerThread()
    t.start()

