# wolfRemote

Control all your devices from a slick web UI!

(As long as your devices happen to be a Vizio TV, a Sony receiver, and LIFX lights.)

## Configure IR

1. Install `vim` so you don't have to use `vi`.

    ```sudo apt install vim```

2. Open `/boot/config.txt` and uncomment the two lines involving `gpio-ir`. Change the `gpio_pin`s as necessary.

    **NOTE TO SAM: for you, rx is 23 and tx is 22.**

3. Reboot. Yes, do it.

   (troubleshooting: [receiver](https://blog.gordonturner.com/2020/05/31/raspberry-pi-ir-receiver/), [transmitter](https://blog.gordonturner.com/2020/06/10/raspberry-pi-ir-transmitter/))

4. `ir-keytable` uses native kernel modules to send and recv IR:

    `apt install ir-keytable`

## Setup the repo

5. Oh, yeah, you need to `apt install git` first.

6. Then clone the repo.

7. Install poetry: `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -`

8. Get a nice mug of hot chocolate, `cd` to the repo's root directory, and `poetry update`.
   (this might take a while, especially on a RPi Zero).

## Configure webserver

We're gonna use `nginx` because I like it better than Apache. And it seems like it might be faster on the annoyingly underpowered RPi Zero.

7. `apt install nginx`

9. Add this stuff to `/etc/systemd/system/remote.service` to make `systemd` know about your service:

    ```
    [Unit]
    Description=wolfRemote

    [Service]
    Restart=on-failure
    RestartSec=5s

    User=pi
    Group=video

    WorkingDirectory=/home/pi/remote
    ExecStart=/usr/bin/pipenv run gunicorn -w 4 -t 60 --chdir server main:app

    [Install]
    WantedBy=multi-user.target
    ```

    Change stuff to reflect your directory if necessary. Gunicorn's default port is 8000.

10. Add this stuff to `/etc/nginx/sites-available/remote.conf` so you can serve your website via nginx:

    ```
	server {
			listen 80;
			server_name remote;

			location / {
					root /home/pi/remote/frontend/build;
			}

			location /api {
					proxy_pass http://localhost:8000;
			}

			location /static/openapi.yaml {
					# definitions for openapi are handled by the server
					proxy_pass http://localhost:8000;
			}
	}
    ```

    Note that you'll need to set up your DNS server so that it points whatever domain you want to access the remote at the pi's IP. Change `server_name` to match.

11. Make `remote.conf` active. From `/etc/nginx/sites-enabled`:

    ```ln -s ../sites-available/remote.conf .```

11. Start everything up

    ```
    sudo systemctl start remote
    sudo systemctl restart nginx
    ```

12. Run it on boot

    ```
    sudo systemctl enable remote
    sudo systemctl enable nginx
    ```

13. Congrats, you did it.

Thanks to [all-free-download.com](https://all-free-download.com/free-vector/download/wildlife-background-wolf-moon-icon-starry-sky-decor_6829751.html) for the icon :)
