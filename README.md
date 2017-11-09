# raspiups
(Rapsberry|Orange|..) Pi UPS

More details will follow.

@see www.ibisek.com


<h1>Installation instructions</h1>:

(1) Get the control script from https://github.com/ibisek/piups
(2) Test the UPS is connected and works fine:
	python3 piups.py status

	You should see at least HW & SW versions, baatery voltage at this stage

(3) Add a user under which this script will run to sudoers to be able to shutdown the machine:
	sudo vim /etc/sudoers
	
	add
	
	<your username> ALL=(ALL) NOPASSWD: /sbin/shutdown
		
(4) Configure your crontab
	crontab -e
	
	@reboot /usr/bin/python3 /path/to/piups.py start & >/ dev/null
	

	
	