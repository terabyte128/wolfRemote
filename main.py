import subprocess
from devices import vizio_tv
import os
import lifxlan as lifx
import json
from devices import ir_remote
from flask import Flask, render_template, request

app = Flask(__name__)

with app.app_context():
    from api.tv import tv_bp
    from api.receiver import receiver_bp
    from api.sequences import seq_bp, SEQUENCES

app.register_blueprint(tv_bp, url_prefix="/api/tv") 
app.register_blueprint(receiver_bp, url_prefix="/api/receiver")
app.register_blueprint(seq_bp, url_prefix="/api/sequence")

use_cec = True

try:
    import cec
except ModuleNotFoundError:
    use_cec = False

lan = lifx.LifxLAN()

with open(os.path.join(app.root_path, "config", "lights.json")) as f:
    things = json.load(f)

lights = {}
scenes = things['groups']

for nickname, addr in things['lights'].items():
    lights[nickname] = lifx.Light(*addr)

TV_CONSTANTS = {
    "ip": "192.168.0.230",
    "auth": "Z78a6d8gz5",
    "mac": "2c:64:1f:6d:3f:15"
}

tv = vizio_tv.VizioTV(TV_CONSTANTS['auth'], TV_CONSTANTS['ip'], TV_CONSTANTS['mac'])
receiver = ir_remote.IRRemote(os.path.join(app.root_path, "config", "sony_strdh590.json"), 10)

if use_cec:
    cec.init()
    cec_devices = cec.list_devices()

CEC_SEQUENCES = {
    "Chromecast": SEQUENCES['chromecast'],
    "NintendoSwitch": SEQUENCES['switch']
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
    if device.osd_string in CEC_SEQUENCES:
        CEC_SEQUENCES[device.osd_string]()

if use_cec:
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
    return render_template("index.html", scenes=scenes)

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

@app.route("/set_scene")
def set_scene():
    color = [
        int(request.args['hue']),
        int(request.args['saturation']), 
        int(request.args['brightness']), 
        int(request.args['kelvin']) if request.args['kelvin'] else int(request.args['custom_kelvin'])
    ]

    did_fail = False

    for name, on in scenes[request.args['scene']].items():
        try:
            if on:
                lights[name].set_power(True)
                lights[name].set_color(color)
            else:
                lights[name].set_power(False)
        except lifx.errors.WorkflowException:
            did_fail = True
            print("failed to set %s" % name)

    if did_fail:
        return ("Failed", 500)
    else:
        return ("OK", 200)
