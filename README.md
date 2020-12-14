# wolfRemote

Control all your devices from a slick web UI!

(As long as your devices happen to be a Vizio TV, a Sony receiver, and LIFX lights.)

## Configure IR

1. Install `vim` so you don't have to use `vi`.

    ```sudo apt install vim```

2. Open `/boot/config.txt` and uncomment the two lines involving `gpio-ir`. Change the `gpio_pin`s as necessary. 
    
    **NOTE TO SAM: for you, rx is 23 and tx is 22.** 

3. Reboot. Yes, do it.

    (Troubleshooting: https://blog.gordonturner.com/2020/05/31/raspberry-pi-ir-receiver/)

4. `ir-keytable` uses native kernel modules to send and recv IR:

    `apt install ir-keytable` 

## Install cec dependencies

Needed for CEC routines. `pipenv` will fail if you don't do this.

`apt install libcec-dev build-essential python3-dev`

## Setup the repo

5. Oh, yeah, you need to `apt install git` first.

6. Then clone the repo.

7. Install pipenv: `apt install pipenv`

8. Get a nice mug of hot chocolate, `cd` to the repo's root directory, and `pipenv sync`.
   (this might take a while, especially on a RPi Zero).

   (You will probably want to set `PIPENV_TIMEOUT=500` otherwise it will probably time out)

## Configure webserver

We're gonna use `nginx` because I like it better than Apache. And it seems like it might be faster on the annoyingly underpowered RPi Zero.

7. `apt install nginx`

    Now we need to do a magic dance to make WSGI serve the site through nginx.

    Install uwsgi, which provides a bridge between nginx and the app:

8.  `apt install uwsgi uwsgi-plugin-python3`

9. Add this stuff to `/etc/systemd/system/remote.service` to make `systemd` know about your service:
    
    ```
    [Unit]
    Description=control all the things
    
    [Service]
    WorkingDirectory=/home/pi/remote
    ExecStartPre=/usr/bin/bash -c 'mkdir -p /run/remote; chown pi:www-data /run/remote'
    ExecStart=uwsgi --ini remote.ini
    
    [Install]
    WantedBy=multi-user.target
    ```

    Change stuff to reflect your directory if necessary.

10. Add this stuff to `/etc/nginx/sites-available/remote.conf` so you can serve your website via nginx:

    ```
    server {
            listen 80;
            server_name remote;
    
            location / {
                    include uwsgi_params;
                    uwsgi_pass unix:/run/remote/remote.sock;
            }
    }
    ```

    Note that you'll need to set up your DNS server so that it points whatever domain you want to access the remote at the pi's IP. Change `server_name` to match.

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