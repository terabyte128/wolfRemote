push:
	scp -r * pi@teletubby:tv-remote
	ssh -t pi@teletubby 'sudo service tv-remote restart'