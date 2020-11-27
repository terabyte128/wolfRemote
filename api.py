import json
from flask import Blueprint, request
from vizio_tv import VizioTV

api_bp = Blueprint("api", __name__)

TV_CONSTANTS = {
    "ip": "192.168.0.230",
    "auth": "Z78a6d8gz5",
    "mac": "2c:64:1f:6d:3f:15"
}

tv = VizioTV(TV_CONSTANTS['auth'], TV_CONSTANTS['ip'], TV_CONSTANTS['mac'])

@api_bp.route("tv/picture_mode", methods=["GET"])
def get_picture_mode():
    return tv.get_picture_mode()

@api_bp.route("tv/picture_mode", methods=["POST"])
def set_picture_mode():
    if not "mode" in (request.json or {}):
        return {"error": "request must contain mode"}, 400

    new_mode = request.json['mode']
    current_modes = tv.get_picture_mode()

    if new_mode not in current_modes['modes']:
        return {"error": f"{new_mode} is not a valid mode"}, 400

    tv.set_picture_mode(new_mode)
    return tv.get_picture_mode()

@api_bp.route("tv/power_state", methods=["GET"])
def get_power_state():
    return {
        "powered_on": tv.get_power_state()
    }

@api_bp.route("tv/power_state", methods=["POST"])
def set_power_state():
    if not "powered_on" in (request.json or {}):
        return {"error": "request must contain powered_on"}, 400

    new_state = request.json['powered_on']

    if new_state:
        tv.power_on()
    else:
        tv.power_off()

    return get_power_state()

@api_bp.route("tv/input", methods=["GET"])
def get_input():
    return tv.get_input()

@api_bp.route("tv/input", methods=["POST"])
def set_input():
    if not "input" in (request.json or {}):
        return {"error": "request must contain input"}, 400

    new_input = request.json['input']
    current_inputs = tv.get_input()

    if not new_input in current_inputs['inputs']:
        return {"error": f"{new_input} is not a valid input"}, 400

    tv.set_input(new_input)
    return get_input()

@api_bp.route("tv/backlight", methods=["GET"])
def get_backlight():
    return tv.get_backlight()

@api_bp.route("tv/backlight", methods=["POST"])
def set_backlight():
    if not "backlight" in (request.json or {}):
        return {"error": "request must contain backlight"}
    
    try:
        new_backlight = int(request.json['backlight'])
    except ValueError:
        return {"error": "backlight must be an int"}, 400

    current_backlight = tv.get_backlight()

    if new_backlight < current_backlight['min'] or new_backlight > current_backlight['max']:
        return {"error": f"backlight must be between {current_backlight['min']} and {current_backlight['max']}"}

    tv.set_backlight(new_backlight)
    return get_backlight()
    
