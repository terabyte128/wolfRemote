import lifxlan as lifx
import logging

import asyncio
from api import LIGHTS, SCENES
from flask import Blueprint, request

lights_bp = Blueprint("lights", __name__)


async def get_light_color(name: str, light: lifx.Light):
    try:
        return (
            name,
            light.get_color(),
        )
    except lifx.WorkflowException as e:
        logging.exception("Failed to communicate with lights")
        return (
            name,
            None,
        )


async def get_lights_async():
    lights = {}
    tasks = []

    for k, v in LIGHTS.items():
        t = asyncio.create_task(get_light_color(k, v))
        tasks.append(t)

    for t in tasks:
        light, color = await t

        if color is None:
            return {
                "error": "Failed to communicate with lights",
            }, 500

        lights[light] = {
            "hue": color[0],
            "saturation": color[1],
            "brightness": color[2],
            "kelvin": color[3],
        }

    return lights


@lights_bp.route("", methods=("GET",))
def get_lights():
    return asyncio.run(get_lights_async())


async def set_light_color(name: str, light: lifx.Light, new_color: dict):
    try:
        orig_color = light.get_color()
        color = list(orig_color)

        for i, param in enumerate(["hue", "saturation", "brightness", "kelvin"]):
            if param in new_color:
                color[i] = new_color[param]

        if tuple(color) != orig_color:
            light.set_color(color, 500)

        return (
            name,
            color,
        )
    except lifx.WorkflowException as e:
        logging.exception("Failed to communicate with lights")
        return (
            name,
            None,
        )


async def set_lights_async(request_data):
    lights = {}
    tasks = []

    for k, v in LIGHTS.items():
        if k in request_data:
            t = asyncio.create_task(set_light_color(k, v, request_data[k]))
            tasks.append(t)

    for t in tasks:
        light, color = await t

        if color is None:
            return {
                "error": "Failed to communicate with lights",
            }, 500

        lights[light] = {
            "hue": color[0],
            "saturation": color[1],
            "brightness": color[2],
            "kelvin": color[3],
        }

    return lights


@lights_bp.route("", methods=("PUT",))
def set_lights():
    return asyncio.run(set_lights_async(request.json))
