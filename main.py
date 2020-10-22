import subprocess
import vizio_tv
import cec
import os
from remotes import ir_remote

from flask import Flask, render_template
app = Flask(__name__)

TV_CONSTANTS = {
    "ip": "192.168.0.230",
    "auth": "Zr9iux8krt",
    "mac": "2c:64:1f:6d:3f:15"
}

tv = vizio_tv.VizioTV(TV_CONSTANTS['auth'], TV_CONSTANTS['ip'], TV_CONSTANTS['mac'])
receiver = ir_remote.IRRemote(os.path.join(os.path.dirname(__file__), "remotes/sony_strdh590.json"), 10)
cec.init()
cec_devices = cec.list_devices()

def chromecast():
    tv.power_on()
    tv.set_input("HDMI-1")
    receiver.send_command("MEDIA")

def switch():
    tv.power_on()
    tv.set_input("HDMI-1")
    receiver.send_command("GAME")

def cubert():
    tv.power_on()
    tv.set_input("HDMI-2")
    receiver.send_command("TV")

def airplay():
    tv.power_on()
    tv.set_input("AirPlay")
    receiver.send_command("TV")

def vinyl():
    receiver.send_command("CD")

def all_off():
    tv.power_off()
    receiver.send_command("POWER")

SEQUENCES = {
    "chromecast": chromecast,
    "switch": switch,
    "cubert": cubert,
    "all_off": all_off,
    "airplay": airplay,
    "vinyl": vinyl
}

VENDOR_SEQUENCES = {
    "Chromecast": chromecast
}

# callback for HDMI-CEC
def cec_cb(*args):
    if len(args) != 2:
        return # only respond to the right command

    source = args[0]
    params = args[1]

    if params['opcode'] != 0x82:
        return # only respond to 0x82, which is "active source"

    device = cec_devices[source]
    print("device", device.osd_string, "became active")

    # activate seq if exists
    if device.osd_string in VENDOR_SEQUENCES:
        VENDOR_SEQUENCES[device.osd_string]()

cec.add_callback(cec_cb, cec.EVENT_ALL)

@app.route("/seq/<sequence>")
def seq(sequence):
    if sequence in SEQUENCES:
        SEQUENCES[sequence]()
        return ("OK", 200)
    else:
        return ("sequence not found", 404)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/picture_mode/<mode>")
def picture_mode(mode):
    tv.set_picture_mode(mode)
    return ("OK", 200)

@app.route("/backlight/<int:backlight>")
def backlight(backlight):
    tv.set_backlight(backlight)
    return ("OK", 200)

@app.route("/force_reboot")
def force_reboot():
    tv.force_reboot()
    return ("OK", 200)

@app.route("/volup/<int:amount>")
def volup(amount):
    receiver.send_command("VOLUP")
    return ("OK", 200)

@app.route("/voldown/<int:amount>")
def voldown(amount):
    receiver.send_command("VOLDOWN")
    return ("OK", 200)

@app.route("/off")
def off():
    tv.power_off()
    return ("OK", 200)
