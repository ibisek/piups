#!/usr/bin/python3


import sys


def printBatteryVoltage():
    print("BATTERY VOLTAGE")


def printIfOnBattery():
    print("on battery? nevim :P");


def printVersion():
    print("printVersion()")


def printTimeOnBattery():
    print("printTimeOnBattery()")


def doShutdown(timeout=None):
    print("doShutdown(%s)" % timeout)
    print("POWER CUT-OFF in (%s) seconds!" % timeout)

def cancelShutdown():
    print("cancelShutdown()")


def printHelp():
    print('## raspiUps ## control script\nusage: piUps.py [ver] [batt] [onbatt] [time] [halt [t]] [cancel]')
    print('\tver\t\treturns UPS version in form of hw.fw')
    print('\tbatt\t\treturns battery voltage [V]')
    print('\tonbatt\t\treturns whether we run on battery (1) or on external power (0)')
    print('\ttime\t\treturns run time on battery in [s] or 0 if powered from external source')
    print('\thalt [t]\tinitiates UPS power off after an optionally defined timeout (default 30s)')
    print('\tcancel\t\tcancels UPS power off countdown')


def parseArguments():
    if len(sys.argv) > 1:
        cmd = str(sys.argv[1]).lower()
        if cmd == 'batt':
            printBatteryVoltage()
        elif cmd == 'onbatt':
            printIfOnBattery()
        elif cmd == 'ver':
            printVersion()
        elif cmd == 'time':
            printTimeOnBattery()
        elif cmd == 'halt':
            if len(sys.argv) == 3:
                doShutdown(int(sys.argv[2]))
            else:
                doShutdown()
        elif cmd == 'cancel':
            cancelShutdown()
        else:
            printHelp()
    else:
        printHelp()


if __name__ == "__main__":
    parseArguments()
