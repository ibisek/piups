#!/usr/bin/python3

#
# raspiUps python interface
#
# @author ibisek
# @version 2017-11-08
#

################# [ CONFIGURATION ] ###################

#######################################################

import sys
from time import sleep
import smbus
import syslog
import subprocess


class SystemTools(object):
    @staticmethod
    def log(message):
        syslog.syslog(syslog.LOG_INFO, message)

    @staticmethod
    def wall(message):
        subprocess.run(['/usr/bin/wall', message])


'''
An object to communicate with the UPS through I2C bus.
'''
class RaspiUps(object):
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
    def getBatteryLow(self):
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
An object to parse command line arguments and perform appropriate actions. 
'''
class RaspiUpsCli(object):
    
    def __init__(self):
        self.ups = RaspiUps()

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
        print(self.ups.getBatteryLow())
    
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
        batteryLow = self.ups.getBatteryLow()
        remainingTimeToPowerOff = self.ups.getRemainingPowerOffTime()
    
        message = "UPS status:\n battery voltage: {:.2f}V \n on battery: {}".format(batteryVoltage, onBattery)
        if onBattery:
            message = "{}\n time on battery: {:}s\n battery low: {}".format(message, secsOnBattery, batteryLow)
            
        if remainingTimeToPowerOff > 0:
            message = "{}\n POWER OFF in {}s".format(message, remainingTimeToPowerOff)
    
        print(message)
        
    def logStatus(self):
        #TODO
        pass
        #SystemTools.log(message)

    def printHelp(self):
        print('## raspiUps ## control script\nusage: piUps.py [ver] [batt] [onbatt] [time] [halt [t]] [cancel]')
        print('\tinfo\t\tprints all available information from the UPS')
        print('\tver\t\tprints UPS version in form of hw.fw')
        print('\tbatt\t\tprints battery voltage [V]')
        print('\tonbatt\t\tprints whether we run on battery (1) or on external power (0)')
        print('\ttime\t\tprints run time on battery in seconds or 0 if powered from external source')
        print('\tbattlow\t\tprints (1) if battery voltage is too low, (0) otherwise')
        print('\tpoweroff [t]\tinitiates UPS power off after an optionally defined timeout (default 30s)')
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
            elif cmd == 'poweroff':
                if len(sys.argv) == 3:
                    self.doPowerOff(int(sys.argv[2]))
                else:
                    self.doPowerOff()
            elif cmd == 'cancel':
                self.cancelPowerOff()
            elif cmd == 'info':
                self.printAllInfo()
            else:
                self.printHelp()
        else:
            self.printHelp()


if __name__ == "__main__":
    
    cli = RaspiUpsCli()
    cli.parseArguments()
    
