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

        signal.signal(signal.SIGTERM, self.sigtermHandler) # listen for SIGTERM

    def createPidFile(self):
        if os.path.isfile(PID_FILE):
            print("PID file already exists in '{}'".format(PID_FILE))
            return False

        open(PID_FILE, 'w+').write("{}\n".format(os.getpid()))
        print("PID file created as {}".format(PID_FILE))

        return True

    def deletePidFile(self):
        os.remove(PID_FILE)
        print('PID file removed')

    def sigtermHandler(self, sigNum, frame):
        self.doRun = False
        self.deletePidFile()

    def run(self):
        res = self.createPidFile()
        if not res:
            sys.exit(1)

        print('Started with PID', os.getpid())

        i = 0
        while self.doRun and i< 10:
            i += 1
            print("T: %s" % (i))
            time.sleep(1)

        self.deletePidFile()


if __name__ == "__main__":
    t = UpsCheckerThread()
    t.start()

