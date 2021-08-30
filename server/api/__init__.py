import json
import os
import lifxlan

from flask import current_app
from server.devices.ir_remote import IRRemote
from server.devices.vizio_tv import VizioTV

with open(os.path.join(current_app.root_path, "config", "tv.json")) as f:
    _tv_constants = json.load(f)

RECEIVER = IRRemote(
    os.path.join(current_app.root_path, "config", "sony_strdh590.json"), 10
)
TV = VizioTV(_tv_constants["auth"], _tv_constants["ip"], _tv_constants["mac"])

with open(os.path.join(current_app.root_path, "config", "lights.json")) as f:
    things = json.load(f)

LIGHTS = {}
GROUPS = SCENES = things["groups"]

for nickname, addr in things["lights"].items():
    LIGHTS[nickname] = lifxlan.Light(*addr)
