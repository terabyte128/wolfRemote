from typing import List
import requests
import time
import warnings
import urllib3
from wakeonlan import send_magic_packet
from pydantic import BaseModel

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VizioTV:
    def __init__(self, auth, ip, mac, port=7345):
        self.auth = auth
        self.ip = ip
        self.mac = mac
        self.port = port
        self.address = "https://{}:{}".format(ip, port)
        self._request_args = {"verify": False, "headers": {"AUTH": self.auth}}

    def _put_payload(self, uri, payload, timeout=0.5):
        r = requests.put(
            "{}/{}".format(self.address, uri),
            json=payload,
            timeout=timeout,
            **self._request_args
        )
        r.raise_for_status()

    def _get_items(self, uri):
        r = requests.get(
            "{}/{}".format(self.address, uri), **self._request_args
        )
        r.raise_for_status()
        return r.json()["ITEMS"]

    def _get_and_set_hashval(self, uri, value):
        # get hashval
        r = requests.get(
            "{}/{}".format(self.address, uri), **self._request_args
        )
        r.raise_for_status()

        hashval = r.json()["ITEMS"][0]["HASHVAL"]

        payload = {"REQUEST": "MODIFY", "VALUE": value, "HASHVAL": hashval}

        # set new value
        r = requests.put(
            "{}/{}".format(self.address, uri),
            json=payload,
            **self._request_args
        )
        r.raise_for_status()

    def force_reboot(self):
        # toggle the power switch
        requests.get(r"http://192.168.0.225/cm?cmnd=Power%20Off")
        time.sleep(0.5)
        requests.get(r"http://192.168.0.225/cm?cmnd=Power%20On")
        time.sleep(15)  # wait for TV to initialize

    def _power_on_normal(self):
        # send a magic packet to wake up if asleep
        for i in range(2):
            send_magic_packet(self.mac)
            time.sleep(0.1)  # ew

        # also send power on signal via virtual remote
        payload = {
            "KEYLIST": [{"CODESET": 11, "CODE": 1, "ACTION": "KEYPRESS"}]
        }

        self._put_payload("key_command/", payload)

    def get_power_state(self):
        return self._get_items("state/device/power_mode")[0]["VALUE"] == 1

    def power_on(self):
        try:
            self._power_on_normal()
        except requests.exceptions.Timeout as e:
            warnings.warn("TV did not respond to magic packet, restarting it.")
            self.force_reboot()
            self._power_on_normal()

    def power_off(self):
        payload = {
            "KEYLIST": [{"CODESET": 11, "CODE": 0, "ACTION": "KEYPRESS"}]
        }

        self._put_payload("key_command/", payload)

    class Input(BaseModel):
        active_input: str
        inputs: List[str]

    def get_input(self) -> Input:
        all_inputs = self._get_items(
            "menu_native/dynamic/tv_settings/devices/name_input"
        )
        all_inputs = [i["NAME"] for i in all_inputs]

        current_input = self._get_items(
            "menu_native/dynamic/tv_settings/devices/current_input"
        )[0]["VALUE"]

        return self.Input(active_input=current_input, inputs=all_inputs)

    def set_input(self, new_input):
        self._get_and_set_hashval(
            "menu_native/dynamic/tv_settings/devices/current_input", new_input
        )

    class Backlight(BaseModel):
        current: int
        min: int
        max: int

    def get_backlight(self) -> Backlight:
        backlight = self._get_items(
            "menu_native/dynamic/tv_settings/picture/backlight"
        )
        return self.Backlight(current=backlight[0]["VALUE"], min=0, max=100)

    def set_backlight(self, backlight):
        assert backlight > 0 and backlight <= 100
        self._get_and_set_hashval(
            "menu_native/dynamic/tv_settings/picture/backlight", backlight
        )

    class PictureMode(BaseModel):
        active_mode: str
        modes: List[str]

    def get_picture_mode(self) -> PictureMode:
        modes = self._get_items(
            "menu_native/dynamic/tv_settings/picture/picture_mode"
        )
        current_mode = modes[0]["VALUE"]
        other_modes = modes[0]["ELEMENTS"]

        if current_mode[-1] == "*":
            current_mode = current_mode[:-1]

        other_modes = [
            mode[:-1] if mode[-1] == "*" else mode for mode in other_modes
        ]

        return self.PictureMode(active_mode=current_mode, modes=other_modes)

    def set_picture_mode(self, mode, also_send_star=True):
        self._get_and_set_hashval(
            "menu_native/dynamic/tv_settings/picture/picture_mode", mode
        )

        if also_send_star:
            self._get_and_set_hashval(
                "menu_native/dynamic/tv_settings/picture/picture_mode",
                mode + "*",
            )

    def volume_up(self, amount=1):
        payload = {"KEYLIST": [{"CODESET": 5, "CODE": 1, "ACTION": "KEYPRESS"}]}

        for _ in range(amount):
            self._put_payload("key_command/", payload)
            time.sleep(0.1)

    def volume_down(self, amount=1):
        payload = {"KEYLIST": [{"CODESET": 5, "CODE": 0, "ACTION": "KEYPRESS"}]}

        for _ in range(amount):
            self._put_payload("key_command/", payload)
            time.sleep(0.1)


# tv = VizioTV("Zr9iux8krt", "192.168.0.230", "2c:64:1f:6d:3f:15")
