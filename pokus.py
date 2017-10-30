#!/usr/bin/python3

import sys

def showBatteryVoltage():
    print("BATTERY VOLTAGE")


def showIfOnBattery():
    print("on battery? nevim :P");


def showVersion():
    print("showVersion()")


def showTimeOnBattery():
    print("showTimeOnBattery()")


def doShutdown(timeout=None):
    print("doShutdown(%s)" % timeout)
    print("POWER CUT-OFF in (%s) seconds!" % timeout)


def parseArguments():
    if len(sys.argv) > 1:
        cmd = str(sys.argv[1]).lower()
        if cmd == 'batt':
            showBatteryVoltage()
        elif cmd == 'onbatt':
            showIfOnBattery()
        elif cmd == 'ver':
            showVersion()
        elif cmd == 'time':
            showTimeOnBattery()
        elif cmd == 'halt':
            if len(sys.argv) == 3:
                doShutdown(int(sys.argv[2]))
            else:
                doShutdown()
    else:
        print('## raspiUps ## control script\nusage: piUps.py [ver] [batt] [onbatt] [time] [halt [t]]')
        print('\tver\t\tshows UPS version in form of hw.fw')
        print('\tbatt\t\tshows battery voltage [V]')
        print('\tonbatt\t\tshows whether we run on battery (1) or on external power (0)')
        print('\ttime\t\tshows run time on battery in [s] or 0 if powered from external source')
        print('\thalt [t]\tinitiate UPS power off after an optionally defined timeout (default 30s)')


if __name__ == "__main__":
    parseArguments()
