# piups
(Rapsberry|Orange|..) Pi UPS

More info will follow shortly.

@see www.ibisek.com

# Hardware installation instructions
TODO

# Software installation instructions

1. Install package dependencies:
	```
	sudo apt-get install python3-smbus
	```
	
2. Enable I2C 
	```
	sudo raspi-config
	```
	
	Go to "5 Interfacing Options" -> "I2C" -> set Yes.
	
3. Get the control script from https://github.com/ibisek/piups
	```
	git clone https://github.com/ibisek/piups.git
	cd piups
	```

	or
	
	```
	cd /opt
	mkdir piups
	cd piups
	wget https://raw.githubusercontent.com/ibisek/piups/master/autoShutdown.py
	wget https://raw.githubusercontent.com/ibisek/piups/master/autoShutdown.sh
	wget https://raw.githubusercontent.com/ibisek/piups/master/piups.py
	```

4. Test the UPS is connected and works fine:
	```
	python3 piups.py status
	```
	You should see some information like HW & SW versions, batery voltage and possibly others at this stage

5. Add a user under which this script will run to sudoers to be able to shutdown the machine:
	```
	sudo vim /etc/sudoers
	```
	and add at the end of the file
	```
	<your username> ALL=(ALL) NOPASSWD: /sbin/shutdown
	```
		
6. Configure your crontab
	```
	crontab -e
	```
	and append
	```
	@reboot /usr/bin/python3 /path/to/piups.py start & >/ dev/null
	```

Done.	
	
