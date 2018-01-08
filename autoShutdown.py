#!/usr/bin/python3
#
# piUps automatic shutdown and poweroff script
#
# @author ibisek
# @version 2017-01-08
# @see https://github.com/ibisek
#
# Crontab entry:
# crontab -e
# @reboot /opt/piups/autoShutdown.py & >/ dev/null
#


from piups import Ups, SystemTools
from time import sleep

################# [ CONFIGURATION ] ###################

# time to wait on battery for the external power to restore:
SECONDS_TO_INITIATE_SHUTDOWN = 5

# time after the UPS will cut the power (time required for pi shutdown + some reserve):
SECONDS_TO_UPS_POWER_OFF = 30

################# [ MAIN ] ###################

if __name__ == "__main__":
    
    ups = Ups()
    
    if ups.isPresent:
        while True:
            if ups.onBattery():
                secondsOnBattery = ups.getSecondsOnBattery()
                if secondsOnBattery > SECONDS_TO_INITIATE_SHUTDOWN:
                    ups.initiatePowerOff(SECONDS_TO_UPS_POWER_OFF)
                    SystemTools.halt()
            sleep(1)
