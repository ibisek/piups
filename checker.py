#!/usr/bin/python3

import os
import sys
import time
import signal
import threading



class RaspiUpsCheckerThread(threading.Thread):
    PID_FILE = "/tmp/piUps.pid"

    doRun = True

    def __init__(self):
        super(RaspiUpsCheckerThread, self).__init__()
        signal.signal(signal.SIGTERM, self.sigtermHandler)  # listen for SIGTERM

    def isThisScriptAlreadyRunning(self):
        try:
            oldpid = open(self.PID_FILE, 'r').read()
            cmdline = open(os.path.join('/proc', str(oldpid), 'cmdline'), 'rb').read().decode('ascii')
            if sys.argv[0] in cmdline:
                return True
            else:
                return False

        except FileNotFoundError:  # not running with that old pid
            return False

    def createPidFile(self):
        open(self.PID_FILE, 'w+').write(str(os.getpid()))
        print("PID file created as {}".format(self.PID_FILE))

    def deletePidFile(self):
        if os.path.isfile(self.PID_FILE):
            os.remove(self.PID_FILE)
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
    t = RaspiUpsCheckerThread()
    t.start()
    
    time.sleep(4)
    
    print("KOHEU.")

