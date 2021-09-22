import json
import os
import lifxlan
import server

from server.devices.ir_remote import IRRemote
from server.devices.vizio_tv import VizioTV

config_path = os.path.join(os.path.dirname(server.__file__), "config")

with open(os.path.join(config_path, "tv.json")) as f:
    _tv_constants = json.load(f)

RECEIVER = IRRemote(os.path.join(config_path, "sony_strdh590.json"), 10)
TV = VizioTV(_tv_constants["auth"], _tv_constants["ip"], _tv_constants["mac"])

with open(os.path.join(config_path, "lights.json")) as f:
    things = json.load(f)

LIGHTS = {}
GROUPS = SCENES = things["groups"]

for nickname, addr in things["lights"].items():
    LIGHTS[nickname] = lifxlan.Light(*addr)
