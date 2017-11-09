# raspiups
(Rapsberry|Orange|..) Pi UPS

More info will follow shortly.

@see www.ibisek.com


# Software installation instructions

1. Get the control script from https://github.com/ibisek/piups

2. Test the UPS is connected and works fine:
	```
	python3 piups.py status
	```
	You should see some information like HW & SW versions, batery voltage and possibly others at this stage

3. Add a user under which this script will run to sudoers to be able to shutdown the machine:
	```
	sudo vim /etc/sudoers
	```
	and add
	```
	<your username> ALL=(ALL) NOPASSWD: /sbin/shutdown
	```
		
4. Configure your crontab
	```
	crontab -e
	```
	and add at the end
	```
	@reboot /usr/bin/python3 /path/to/piups.py start & >/ dev/null
	```

	
	
