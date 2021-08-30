import wakeonlan

from flask import Blueprint, request
from server.api import TV, RECEIVER

seq_bp = Blueprint("sequences", __name__)


def chromecast():
    TV.power_on()
    TV.set_input("HDMI-1")
    RECEIVER.send_command("MEDIA")


def switch():
    TV.power_on()
    TV.set_input("HDMI-1")
    RECEIVER.send_command("GAME")


def cubert():
    TV.power_on()
    # wake up cubert
    wakeonlan.send_magic_packet("70:85:c2:db:fd:90")
    TV.set_input("HDMI-2")
    RECEIVER.send_command("TV")


def airplay():
    TV.power_on()
    TV.set_input("AirPlay")
    RECEIVER.send_command("TV")


def vinyl():
    RECEIVER.send_command("CD")


def all_off():
    TV.power_off()
    RECEIVER.send_command("POWER")


SEQUENCES = {
    "chromecast": chromecast,
    "switch": switch,
    "cubert": cubert,
    "all_off": all_off,
    "airplay": airplay,
    "vinyl": vinyl,
}


@seq_bp.route("", methods=["GET", "PUT"])
def sequence():
    if request.method == "GET":
        return {"all_sequences": list(SEQUENCES.keys())}

    if "sequence" not in request.json or {}:
        return {"error": "sequence is required"}, 400

    sequence = request.json["sequence"]

    if sequence in SEQUENCES.keys():
        SEQUENCES[sequence]()
        return "", 204
    else:
        return {"error": "sequence not found"}, 404
