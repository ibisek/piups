#!/usr/bin/python3

#
# piUps python interface and control script
#
# @author ibisek
# @version 2017-11-08
# @see https://github.com/ibisek
#

################# [ CONFIGURATION ] ###################

# To enable system shutdown run you need to add this to /etc/sudoers:
# <your username> ALL=(ALL) NOPASSWD: /sbin/shutdown

HALT_AFTER_SECS_ON_BATT = 120   # 0 disables this functionality
HALT_WHEN_BATT_VOLTAGE_BELOW = 3.4  # 0 disables this functionality; 3.4 is a reasonable value
HALT_WHEN_BATTERY_LOW = False   # False disables this functionality

#######################################################


import os
import sys
from time import sleep
import datetime
import signal
import smbus
import syslog
import subprocess
import threading


class SystemTools(object):

    @staticmethod
    def log(message):
        syslog.syslog(syslog.LOG_INFO, message)

    @staticmethod
    def wall(message):
        subprocess.run(['/usr/bin/wall', message])
        
    @staticmethod
    def halt():
        subprocess.run(['/usr/bin/sudo', '/sbin/shutdown', '-h', 'now'])
        sys.exit(0)
    
    @staticmethod    
    def kill(pid):
        subprocess.run(['/bin/kill', str(pid)])

'''
An object to communicate with the UPS through I2C bus.
'''
class Ups(object):
    I2C_ADDRESS = 0x66
    
    REGISTER_ON_BATTERY = 0x01
    REGISTER_TIME_ON_BATTERY = 0x02
    REGISTER_BATTERY_VOLTAGE = 0x04
    REGISTER_BATTERY_LOW = 0x06
    REGISTER_DO_POWER_OFF = 0x07
    REGISTER_TIME_TO_POWER_OFF = 0x08
    REGISTER_VERSION_HW = 0xFE
    REGISTER_VERSION_SW = 0xFF

    bus = smbus.SMBus(1)

    '''
    @return: (hwVersion, swVersion)
    '''

    def getVersions(self):
        hwVer = self.bus.read_byte_data(self.I2C_ADDRESS, self.REGISTER_VERSION_HW)
        swVer = self.bus.read_byte_data(self.I2C_ADDRESS, self.REGISTER_VERSION_SW)
        return (hwVer, swVer)
    
    '''
    @return: 1 if we are on battery; 0 if powered from and external power source (e.g. mains)
    '''

    def onBattery(self):
        return self.bus.read_byte_data(self.I2C_ADDRESS, self.REGISTER_ON_BATTERY) 
    
    '''
    @return: battery voltage [V]
    '''
    
    def getBatteryVoltage(self):
        voltage = self.bus.read_byte_data(self.I2C_ADDRESS, self.REGISTER_BATTERY_VOLTAGE) << 8
        voltage += self.bus.read_byte_data(self.I2C_ADDRESS, self.REGISTER_BATTERY_VOLTAGE + 1)
    
        return voltage / 100
    
    '''
    @return LBO signal - 1 if battery voltage is low, 0 otherwise
    '''

    def isBatteryLow(self):
        return self.bus.read_byte_data(self.I2C_ADDRESS, self.REGISTER_BATTERY_LOW)
    
    '''
    @return: time in seconds since the external power was interrupted; 0 when on external power
    '''
    
    def getSecondsOnBattery(self):
        time = self.bus.read_byte_data(self.I2C_ADDRESS, self.REGISTER_TIME_ON_BATTERY) << 8
        time += self.bus.read_byte_data(self.I2C_ADDRESS, self.REGISTER_TIME_ON_BATTERY + 1)
    
        return time
    
    '''
    @param seconds: time after which to power off the UPS output when requested
    '''
    
    def setPowerOffTime(self, seconds=20):
        self.bus.write_byte_data(self.I2C_ADDRESS, self.REGISTER_TIME_TO_POWER_OFF, seconds)
        
    '''
    @return remaining seconds to UPS power off 
    '''

    def getRemainingPowerOffTime(self):
        return self.bus.read_byte_data(self.I2C_ADDRESS, self.REGISTER_TIME_TO_POWER_OFF)
    
    '''
    @param seconds: (optional) time after which to power off the UPS output; default 20
    '''
    
    def initiatePowerOff(self, seconds=None):
        if seconds:
            setPowerOffTime(seconds)
            sleep(0.1)
    
        self.bus.write_byte_data(self.I2C_ADDRESS, self.REGISTER_DO_POWER_OFF, 0x01)
        sleep(0.1)
        time = self.bus.read_byte_data(self.I2C_ADDRESS, self.REGISTER_TIME_TO_POWER_OFF)

    '''
    Cancels UPS power off count-down.
    '''

    def cancelPowerOff(self):
        self.bus.write_byte_data(self.I2C_ADDRESS, self.REGISTER_DO_POWER_OFF, 0x00)
        

'''
A thread that checks status of the UPS registers every second and responds accordingly
'''
class UpsObserverThread(threading.Thread):
    PID_FILE = "/tmp/piUps.pid"

    doRun = True
    prevOnBattery = False

    def __init__(self, ups, upsCli):
        super(UpsObserverThread, self).__init__()
        
        signal.signal(signal.SIGTERM, self.sigtermHandler)  # listen for SIGTERM
        self.ups = ups
        self.upsCli = upsCli

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
        print("PID file created in {}".format(self.PID_FILE))

    def deletePidFile(self):
        if os.path.isfile(self.PID_FILE):
            os.remove(self.PID_FILE)
            print('PID file removed')

    def sigtermHandler(self, sigNum, frame):
        print("SIGTERM requested")
        self.doRun = False

    def run(self):
        if self.isThisScriptAlreadyRunning():
            print("An instance already running. Exiting..")
            sys.exit(1)

        self.createPidFile()
        message = "UPS observer started with pid {}".format(os.getpid())
        SystemTools.log(message)
        print(message)

        while self.doRun:
            onBattery = self.ups.onBattery()
            
            if onBattery:
                if not self.prevOnBattery:
                    self.prevOnBattery = True
                    message = "External power lost, running on battery"
                    SystemTools.log(message) 
                    SystemTools.wall(message)

                # log UPS status when running on battery:                    
                s = self.ups.getSecondsOnBattery()
                if s % 5 == 0:
                    self.upsCli.logStatus()
                    
                if HALT_WHEN_BATTERY_LOW and self.ups.isBatteryLow():
                    SystemTools.log("UPS battery too low ({}V). Initiating system shutdown.".format(self.ups.getBatteryVoltage()))
                    self.ups.initiatePowerOff()
                    SystemTools.halt()
                    
                if HALT_AFTER_SECS_ON_BATT > 0:
                    timeOnBatt = self.ups.getSecondsOnBattery()
                    if timeOnBatt > HALT_AFTER_SECS_ON_BATT:
                        SystemTools.log("Runtime on battery ({}s) exceeded configured limit ({}s). Initiating system shutdown.".format(timeOnBatt, HALT_AFTER_SECS_ON_BATT))
                        self.ups.initiatePowerOff()
                        SystemTools.halt()
                        
                if HALT_WHEN_BATT_VOLTAGE_BELOW > 0:
                    battVoltage = self.ups.getBatteryVoltage() 
                    if battVoltage < HALT_WHEN_BATT_VOLTAGE_BELOW:
                        SystemTools.log("Battery voltage ({}V) below configured limit ({}V). Initiating system shutdown.".format(battVoltage, HALT_WHEN_BATT_VOLTAGE_BELOW))
                        self.ups.initiatePowerOff()
                        SystemTools.halt()
                
            elif not onBattery and self.prevOnBattery:
                self.prevOnBattery = False
                message = "External power restored"
                SystemTools.log(message) 
                SystemTools.wall(message)
                
            # once an hour log UPS status:
            now = datetime.datetime.now()
            if now.minute == 0 and now.second == 0:
                self.upsCli.logStatus()
                
            sleep(1)

        self.deletePidFile()
        SystemTools.log("UPS observer terminated")


'''
An object to parse command line arguments and perform appropriate actions. 
'''
class UpsCli(object):
    
    def __init__(self):
        self.ups = Ups()

    def printBatteryVoltage(self):
        print("{:.2f}".format(self.ups.getBatteryVoltage()))
    
    def printIfOnBattery(self):
        print(self.ups.onBattery())
    
    def printVersion(self):
        ver = self.ups.getVersions()
        print("{}.{}".format(ver[0], ver[1]))
    
    def printTimeOnBattery(self):
        print(self.ups.getSecondsOnBattery())
    
    def printBatteryLow(self):
        print(self.ups.isBatteryLow())
    
    def doPowerOff(self, timeout=None):
        self.ups.initiatePowerOff(timeout)

        message = "UPS POWER OFF in {}s!".format(self.ups.getRemainingPowerOffTime())
        SystemTools.log(message)
        SystemTools.wall(message)
    
    def cancelPowerOff(self):
        self.ups.cancelPowerOff()

        message = "UPS power off cancelled"
        SystemTools.log(message)
        SystemTools.wall(message)
    
    def printAllInfo(self):
        ver = self.ups.getVersions()
        batteryVoltage = self.ups.getBatteryVoltage()
        onBattery = self.ups.onBattery()
        secsOnBattery = self.ups.getSecondsOnBattery()
        batteryLow = self.ups.isBatteryLow()
        remainingTimeToPowerOff = self.ups.getRemainingPowerOffTime()
    
        message = "UPS status:\n battery voltage: {:.2f}V \n on battery: {}".format(batteryVoltage, onBattery)
        if onBattery:
            message = "{}\n time on battery: {:}s\n battery low: {}".format(message, secsOnBattery, batteryLow)
            
        if remainingTimeToPowerOff > 0:
            message = "{}\n POWER OFF in {}s".format(message, remainingTimeToPowerOff)
    
        print(message)

    def logStatus(self):
        ver = self.ups.getVersions()
        batteryVoltage = self.ups.getBatteryVoltage()
        onBattery = self.ups.onBattery()
        secsOnBattery = self.ups.getSecondsOnBattery()
        batteryLow = self.ups.isBatteryLow()
        remainingTimeToPowerOff = self.ups.getRemainingPowerOffTime()
    
        message = "UPS status: onBatt: {}; battVoltage: {:.2f}V".format(onBattery, batteryVoltage)
        if onBattery:
            message = "{}; timeOnBatt: {:}s; battLow: {}".format(message, secsOnBattery, batteryLow)
            
        if remainingTimeToPowerOff > 0:
            message = "{}; POWER OFF in {}s".format(message, remainingTimeToPowerOff)

        SystemTools.log(message)
        
    def startObserverThread(self):
        t = UpsObserverThread(self.ups, self)
        t.start()
        
    def stopObserver(self):
        if not os.path.isfile(UpsObserverThread.PID_FILE):
            print("PID file not found in '{}'".format(UpsObserverThread.PID_FILE))
            return
        
        text = open(UpsObserverThread.PID_FILE, 'r').read()
        try:
            pid = int(text)
            print("Sending SIGTERM to PID {}. That shall do the job.".format(pid))
            SystemTools.kill(pid)           
            
        except Exception as e:
            print(e)
            return

    def printHelp(self):
        print('UPS control script\n usage: piUps.py [info|status] [ver] [batt] [onbatt] [time] [halt [t]] [cancel] [start|stop]')
        print('\tinfo|status\tprints all available information from the UPS')
        print('\tver\t\tprints UPS version in form of hw.fw')
        print('\tbatt\t\tprints battery voltage [V]')
        print('\tonbatt\t\tprints whether we run on battery (1) or on external power (0)')
        print('\ttime\t\tprints run time on battery in seconds or 0 if powered from external source')
        print('\tbattlow\t\tprints (1) if battery voltage is too low, (0) otherwise')
        print('\tpoweroff [t]\tinitiates UPS power off after an optionally defined timeout (default 30s)')
        print('\tcancel\t\tcancels UPS power off countdown')
        print('\tstart\t\tstarts UPS status observer process. This is to be typically called from cron at @reboot')
        print('\tstop\t\tterminates UPS status observer process')
    
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
            elif cmd == 'poweroff':
                if len(sys.argv) == 3:
                    self.doPowerOff(int(sys.argv[2]))
                else:
                    self.doPowerOff()
            elif cmd == 'cancel':
                self.cancelPowerOff()
            elif cmd == 'info' or cmd == 'status':
                self.printAllInfo()
            elif cmd == 'start':
                self.startObserverThread()
            elif cmd == 'stop':
                self.stopObserver()
            else:
                self.printHelp()
        else:
            self.printHelp()


if __name__ == "__main__":
    
    cli = UpsCli()
    cli.parseArguments()
    
