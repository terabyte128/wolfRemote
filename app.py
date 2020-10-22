import lifxlan as lifx
import os
import json

from flask import Flask, escape, request, render_template, redirect

lan = lifx.LifxLAN()

app = Flask(__name__)

with open(os.path.join(app.root_path, "lights.json")) as f:
    things = json.load(f)

lights = {}
scenes = things['scenes']

for nickname, addr in things['lights'].items():
    lights[nickname] = lifx.Light(*addr)

@app.route('/')
def index():
    return render_template('index.html', scenes=scenes)

@app.route("/set_scene")
def set_scene():
    color = [
        int(request.args['hue']),
        int(request.args['saturation']), 
        int(request.args['brightness']), 
        int(request.args['kelvin']) if request.args['kelvin'] else int(request.args['custom_kelvin'])
    ]

    for name, on in scenes[request.args['scene']].items():
        try:
            if on:
                lights[name].set_power(True)
                lights[name].set_color(color)
            else:
                lights[name].set_power(False)
        except lifx.errors.WorkflowException:
            print("failed to set %s" % name)

    return "done"
