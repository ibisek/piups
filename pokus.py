#!/usr/bin/python3


import sys
import syslog
import subprocess


def log(message):
    syslog.syslog(syslog.LOG_INFO, message)

def wall(message):
    subprocess.run(['/usr/bin/wall', message])


class RaspiUpsCli(object):
    
    def __init__(self):
        print("INIT")
    

    def printBatteryVoltage(self):
        print("BATTERY VOLTAGE")
    
    
    def printIfOnBattery(self):
        print("on battery? nevim :P");
    
    
    def printVersion(self):
        print("printVersion()")
    
    
    def printTimeOnBattery(self):
        print("printTimeOnBattery()")
    
    
    def printBatteryLow(self):
        print("printBatteryLow()")
    
    
    def doShutdown(self, timeout=None):
        print("doShutdown(%s)" % timeout)
    
        message = "UPS POWER OFF in {} seconds!".format(timeout)
        SystemTools.log(message)
        SystemTools.wall(message)
    
    def cancelShutdown(self):
        print("cancelShutdown()")
    
        self.ups.cancel()
    
        message = "UPS power off cancelled"
        SystemTools.log(message)
        SystemTools.wall(message)
    
    
    def checkPowerStatus(self):
        #TODO vycist z upsky
        batteryVoltage = 3.78
        onBattery = True
        timeOnBattery = 45
        batteryLow = False
    
        message = "Status check: battery voltage: {:.2f}V; on battery: {}".format(batteryVoltage, onBattery)
        if onBattery:
            message = "{}; time on battery: {:}s; battery low: {}".format(message, timeOnBattery, batteryLow)
    
        log(message)
        
    def printAllInfo(self):
        print("printAllInfo")
    
    
    
    def printHelp(self):
        print('## raspiUps ## control script\nusage: piUps.py [ver] [batt] [onbatt] [time] [halt [t]] [cancel]')
        print('\tinfo\t\tprints all available information from the UPS')
        print('\tver\t\tprints UPS version in form of hw.fw')
        print('\tbatt\t\tprints battery voltage [V]')
        print('\tonbatt\t\tprints whether we run on battery (1) or on external power (0)')
        print('\ttime\t\tprints run time on battery in [s] or 0 if powered from external source')
        print('\tbattlow\t\tprints (1) if battery voltage is too low, (0) otherwise')
        print('\thalt [t]\tinitiates UPS power off after an optionally defined timeout (default 30s)')
        print('\tcancel\t\tcancels UPS power off countdown')
    
    
    def parseArguments(self):
        if len(sys.argv) > 1:
            cmd = str(sys.argv[1]).lower()
            if cmd == 'batt':
                self.printBatteryVoltage()
            elif cmd == 'onbatt':
                self.printIfOnBattery()
            elif cmd == 'ver':
                self.printVersion()
            elif cmd == 'time':
                self.printTimeOnBattery()
            elif cmd == 'battlow':
                self.printBatteryLow()
            elif cmd == 'halt':
                if len(sys.argv) == 3:
                    self.doShutdown(int(sys.argv[2]))
                else:
                    self.doShutdown()
            elif cmd == 'cancel':
                self.cancelShutdown()
            elif cmd == 'check':
                self.checkPowerStatus()
            if cmd == 'info':
                self.printAllInfo()
            else:
                self.printHelp()
        else:
            self.printHelp()


if __name__ == "__main__":

    cli = RaspiUpsCli()
    cli.parseArguments()
    