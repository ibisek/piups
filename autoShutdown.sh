#!/bin/bash
#
# piUps automatic shutdown and poweroff script
#
# @author ibisek
# @version 2017-01-08
# @see https://github.com/ibisek
#
# Crontab entry:
# crontab -e
# @reboot /opt/piups/autoShutdown.sh & >/ dev/null
#

################# [ CONFIGURATION ] ###################

UPS_SCRIPT_DIR='/opt/piups'

# time to wait on battery for the external power to restore:
SECONDS_TO_INITIATE_SHUTDOWN=10

# time after the UPS will cut the power (time required for pi shutdown + some reserve):
SECONDS_TO_UPS_POWER_OFF=20

################# [ MAIN ] ###################

while [[ 1 ]]; do
	secondsOnBattery=`python3 $UPS_SCRIPT_DIR/piups.py time`
	
	if [[ $secondsOnBattery -gt $SECONDS_TO_INITIATE_SHUTDOWN ]]; then
		python3 $UPS_SCRIPT_DIR/piups.py poweroff $SECONDS_TO_UPS_POWER_OFF
	fi
	
	sleep 1
done

echo "KOHEU"	

