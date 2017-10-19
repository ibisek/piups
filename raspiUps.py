#!/usr/bin/python3
from tkinter.messagebox import CANCEL

#
# raspiUps python interface
#
# @author ibisek
# @version 2017-10-20
#

################# [ CONFIGURATION ] ###################

I2C_ADDRESS = 0x66

REGISTER_ON_BATTERY = 0x01        
REGISTER_TIME_ON_BATTERY = 0x02  
REGISTER_BATTERY_VOLTAGE = 0x04
REGISTER_BATTERY_LOW = 0x06
REGISTER_DO_POWER_OFF = 0x07
REGISTER_TIME_TO_POWER_OFF = 0x08   
REGISTER_VERSION_HW = 0xFE
REGISTER_VERSION_SW = 0xFF            

#######################################################

import sys
from time import sleep
import smbus

bus = smbus.SMBus(1)

'''
@return: (hwVersion, swVersion)
'''
def getVersions():
    hwVer = bus.read_byte_data(I2C_ADDRESS, REGISTER_VERSION_HW)
    swVer = bus.read_byte_data(I2C_ADDRESS, REGISTER_VERSION_SW)
    return (hwVer, swVer)

'''
@return: 1 if we are on battery; 0 if powered from and external power source (e.g. mains)
'''
def onBattery():
    return bus.read_byte_data(I2C_ADDRESS, REGISTER_ON_BATTERY) 

'''
@return: battery voltage [V]
'''
def getBatteryVoltage():
    voltage = bus.read_byte_data(I2C_ADDRESS, REGISTER_BATTERY_VOLTAGE) << 8
    voltage +=  bus.read_byte_data(I2C_ADDRESS, REGISTER_BATTERY_VOLTAGE + 1) 

    return voltage / 100

'''
@return: time in seconds since the external power was interrupted; 0 when on external power
'''
def getSecondsOnBattery():
    time = bus.read_byte_data(I2C_ADDRESS, REGISTER_TIME_ON_BATTERY) << 8
    time +=  bus.read_byte_data(I2C_ADDRESS, REGISTER_TIME_ON_BATTERY + 1)

    return time

'''
@param seconds: time after which to power off the UPS output when requested
''' 
def setPowerOffTime(seconds=20):
    bus.write_byte_data(I2C_ADDRESS, REGISTER_TIME_TO_POWER_OFF, seconds)

'''
@param seconds: (optional) time after which to power off the UPS output; default 20
'''
def initiatePowerOff(seconds=None):
    if seconds:
        setPowerOffTime(seconds)
        sleep(0.1)
    
    bus.write_byte_data(I2C_ADDRESS, REGISTER_DO_POWER_OFF, 0x01)
    sleep(0.1)
    time = bus.read_byte_data(I2C_ADDRESS, REGISTER_TIME_TO_POWER_OFF)
    print("Initiated UPS power off in {}s".format(time))
    
'''
Cancels UPS power off count-down.
'''
def cancelPowerOff():
    bus.write_byte_data(I2C_ADDRESS, REGISTER_DO_POWER_OFF, 0x00)
    print("UPS power off cancelled")
    

try:
    versions = getVersions()
    print("## raspiUps ## (hw ver.{}, sw ver.{})".format(versions[0], versions[1]))
except OSError:
    print("raspiUps NOT detected")
    sys.exit(1)

batteryVoltage = getBatteryVoltage()
print("Vbat:", batteryVoltage)

onBattery = onBattery()
print("onBattery:", onBattery)

if onBattery:
    secondsOnBattery = getSecondsOnBattery()
    print("secondsOnBattery:", secondsOnBattery)


initiatePowerOff(30)
#sleep(10)
#cancelPowerOff()



