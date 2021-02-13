import json
import os
import time

from flask import Blueprint, request
from api import TV, RECEIVER
from fire_and_forget import run

receiver_bp = Blueprint("api.receiver", __name__)


@receiver_bp.route("volume", methods=["GET", "PUT"])
def volume():
    if request.method != "PUT":
        return {"error": "only PUT requests are supported"}, 400

    if not all(k in (request.json or {}) for k in ["amount", "direction"]):
        return {"error": "request must contain amount and direction"}, 400

    if request.json["direction"] not in ["up", "down"]:
        return {"error": "direction must be up or down"}, 400

    try:
        volume_amount = int(request.json["amount"])
    except ValueError:
        return {"error": "amount must be an int"}, 400

    if volume_amount < 0 or volume_amount > 5:
        return {"error": "amount must be between 1 and 5"}, 400

    def f():
        if request.json["direction"] == "up":
            RECEIVER.send_command("VOLUP", amount)
        else:
            RECEIVER.send_command("VOLDOWN", amount)

    run(f, [])

    return "", 204


@receiver_bp.route("input", methods=["GET"])
def get_inputs():
    return {"inputs": RECEIVER.get_inputs()}


@receiver_bp.route("input", methods=["PUT"])
def set_input():
    if not "input" in (request.json or {}):
        return {"error": "input is requred"}, 400
    elif request.json["input"] not in RECEIVER.get_inputs():
        return {"error": "input is invalid"}, 400

    RECEIVER.set_input(request.json["input"])

    return "", 204
