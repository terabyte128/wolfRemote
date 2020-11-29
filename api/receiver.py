import json
import os
import time

from flask import Blueprint, request
from api import TV, RECEIVER

receiver_bp = Blueprint("api.receiver", __name__)

@receiver_bp.route("volume", methods=["GET", "POST"])
def volume():
    if request.method != "POST":
        return {"error": "only POST requests are supported"}, 400
    
    if not all(k in (request.json or {}) for k in ["amount", "direction"]):
        return {"error": "request must contain amount and direction"}, 400

    if request.json['direction'] not in ['up', 'down']:
        return {"error": "direction must be up or down"}, 400

    try:
        volume_amount = int(request.json['amount'])
    except ValueError:
        return {"error": "amount must be an int"}, 400

    if volume_amount < 0 or volume_amount > 5:
        return {"error": "amount must be between 0 and 5"}, 400
    
    for i in range(volume_amount):
        if request.json['direction'] == "up":
            RECEIVER.send_command("VOLUP")
        else:
            RECEIVER.send_command("VOLDOWN")

        time.sleep(0.1)

    return "", 204