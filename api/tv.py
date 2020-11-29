import json
import os

from flask import Blueprint, request
from api import TV

tv_bp = Blueprint("api.tv", __name__)

@tv_bp.route("picture_mode", methods=["GET"])
def get_picture_mode():
    return TV.get_picture_mode()

@tv_bp.route("picture_mode", methods=["POST"])
def set_picture_mode():
    if not "mode" in (request.json or {}):
        return {"error": "request must contain mode"}, 400

    new_mode = request.json['mode']
    current_modes = TV.get_picture_mode()

    if new_mode not in current_modes['modes']:
        return {"error": f"{new_mode} is not a valid mode"}, 400

    TV.set_picture_mode(new_mode)
    return TV.get_picture_mode()

@tv_bp.route("power_state", methods=["GET"])
def get_power_state():
    return {
        "power_state": TV.get_power_state()
    }

@tv_bp.route("power_state", methods=["POST"])
def set_power_state():
    if not "powered_on" in (request.json or {}):
        return {"error": "request must contain power_state"}, 400

    new_state = request.json['power_state']

    if new_state:
        TV.power_on()
    else:
        TV.power_off()

    return get_power_state()

@tv_bp.route("input", methods=["GET"])
def get_input():
    return TV.get_input()

@tv_bp.route("input", methods=["POST"])
def set_input():
    if not "input" in (request.json or {}):
        return {"error": "request must contain input"}, 400

    new_input = request.json['input']
    current_inputs = TV.get_input()

    if not new_input in current_inputs['inputs']:
        return {"error": f"{new_input} is not a valid input"}, 400

    TV.set_input(new_input)
    return get_input()

@tv_bp.route("backlight", methods=["GET"])
def get_backlight():
    return TV.get_backlight()

@tv_bp.route("backlight", methods=["POST"])
def set_backlight():
    if not "backlight" in (request.json or {}):
        return {"error": "request must contain backlight"}
    
    try:
        new_backlight = int(request.json['backlight'])
    except ValueError:
        return {"error": "backlight must be an int"}, 400

    current_backlight = TV.get_backlight()

    if new_backlight < current_backlight['min'] or new_backlight > current_backlight['max']:
        return {"error": f"backlight must be between {current_backlight['min']} and {current_backlight['max']}"}

    TV.set_backlight(new_backlight)
    return get_backlight()


    