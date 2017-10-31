#!/usr/bin/python3


import sys
import syslog
import subprocess


def printBatteryVoltage():
    print("BATTERY VOLTAGE")


def printIfOnBattery():
    print("on battery? nevim :P");


def printVersion():
    print("printVersion()")


def printTimeOnBattery():
    print("printTimeOnBattery()")


def printBatteryLow():
    print("printBatteryLow()")


def doShutdown(timeout=None):
    print("doShutdown(%s)" % timeout)

    #TODO read-out timeout if None
    #TODO initiate power-off countdown

    message = "UPS POWER OFF in {} seconds!".format(timeout)
    log(message)
    wall(message)

def cancelShutdown():
    print("cancelShutdown()")

    #TODO cancel shutdown

    message = "UPS power off cancelled"
    log(message)
    wall(message)


def checkPowerStatus():
    #TODO vycist z upsky
    batteryVoltage = 3.78
    onBattery = True
    timeOnBattery = 45
    batteryLow = False

    message = "Status check: battery voltage: {:.2f}V; on battery: {}".format(batteryVoltage, onBattery)
    if onBattery:
        message = "{}; time on battery: {:}s; battery low: {}".format(message, timeOnBattery, batteryLow)

    log(message)


def log(message):
    syslog.syslog(syslog.LOG_INFO, message)

def wall(message):
    subprocess.run(['/usr/bin/wall', message])


def printHelp():
    print('## raspiUps ## control script\nusage: piUps.py [ver] [batt] [onbatt] [time] [halt [t]] [cancel]')
    print('\tver\t\treturns UPS version in form of hw.fw')
    print('\tbatt\t\treturns battery voltage [V]')
    print('\tonbatt\t\treturns whether we run on battery (1) or on external power (0)')
    print('\ttime\t\treturns run time on battery in [s] or 0 if powered from external source')
    print('\tbattlow\t\treturns (1) if battery voltage is too low, (0) otherwise')
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
        elif cmd == 'battlow':
            printBatteryLow()
        elif cmd == 'halt':
            if len(sys.argv) == 3:
                doShutdown(int(sys.argv[2]))
            else:
                doShutdown()
        elif cmd == 'cancel':
            cancelShutdown()
        elif cmd == 'check':
            checkPowerStatus()
        else:
            printHelp()
    else:
        printHelp()


if __name__ == "__main__":
    parseArguments()
