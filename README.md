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
	
2. Get the control script from https://github.com/ibisek/piups
	```
	cd /opt
	mkdir piups
	cd piups
	wget https://raw.githubusercontent.com/ibisek/piups/master/autoShutdown.py
	wget https://raw.githubusercontent.com/ibisek/piups/master/autoShutdown.sh
	wget https://raw.githubusercontent.com/ibisek/piups/master/piups.py
	```
	
	or just
	
	```
	git clone https://github.com/ibisek/piups.git
	cd piups
	```

3. Test the UPS is connected and works fine:
	```
	python3 piups.py status
	```
	You should see some information like HW & SW versions, batery voltage and possibly others at this stage

4. Add a user under which this script will run to sudoers to be able to shutdown the machine:
	```
	sudo vim /etc/sudoers
	```
	and add at the end of the file
	```
	<your username> ALL=(ALL) NOPASSWD: /sbin/shutdown
	```
		
5. Configure your crontab
	```
	crontab -e
	```
	and append
	```
	@reboot /usr/bin/python3 /path/to/piups.py start & >/ dev/null
	```

	
	
