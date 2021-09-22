from typing import Dict, Optional
import lifxlan as lifx
import logging
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic.main import BaseModel

from server.api import LIGHTS

light_router = APIRouter(tags=["lights"])


async def get_light_color(name: str, light: lifx.Light):
    try:
        return (
            name,
            light.get_color(),
        )
    except lifx.WorkflowException:
        logging.exception("Failed to communicate with lights")
        return (
            name,
            None,
        )


class LightColor(BaseModel):
    hue: int
    saturation: int
    brightness: int
    kelvin: int


class Lights(BaseModel):
    lights: Dict[str, LightColor]


@light_router.get("", response_model=Lights)
async def get_lights() -> Lights:
    lights = {}
    tasks = []

    for k, v in LIGHTS.items():
        t = asyncio.create_task(get_light_color(k, v))
        tasks.append(t)

    for t in tasks:
        light, color = await t

        if color is None:
            raise HTTPException(502, "Failed to communicate with lights")

        lights[light] = LightColor(
            hue=color[0],
            saturation=color[1],
            brightness=color[2],
            kelvin=color[3],
        )

    return Lights(lights=lights)


class OptionalLightColor(BaseModel):
    hue: Optional[int]
    saturation: Optional[int]
    brightness: Optional[int]
    kelvin: Optional[int]


class OptionalLights(BaseModel):
    lights: Dict[str, OptionalLightColor]


async def set_light_color(
    name: str, light: lifx.Light, new_color: OptionalLightColor
):
    try:
        orig_color = light.get_color()
        color = list(orig_color)

        for i, param in enumerate(
            [
                new_color.hue,
                new_color.saturation,
                new_color.brightness,
                new_color.kelvin,
            ]
        ):
            if param is not None:
                color[i] = param

        if tuple(color) != orig_color:
            light.set_color(color, 500)

        return (
            name,
            color,
        )
    except lifx.WorkflowException:
        logging.exception("Failed to communicate with lights")
        return (
            name,
            None,
        )


@light_router.put(
    "",
    response_model=OptionalLights,
    description="A dictionary of each light you wish to update, mapping to each "
    "property you wish to change. Properties not given will remain the same.",
)
async def set_lights(lights: OptionalLights):
    tasks = []

    invalid_names = [k for k in lights.lights.keys() if k not in LIGHTS.keys()]

    if len(invalid_names) > 0:
        raise HTTPException(
            400, f"Invalid light names in request: {invalid_names}"
        )

    for k, v in LIGHTS.items():
        if k in lights.lights:
            t = asyncio.create_task(set_light_color(k, v, lights.lights[k]))
            tasks.append(t)

    for t in tasks:
        light, color = await t

        if color is None:
            return {
                "error": "Failed to communicate with lights",
            }, 500

        lights.lights[light] = OptionalLightColor(
            hue=color[0],
            saturation=color[1],
            brightness=color[2],
            kelvin=color[3],
        )

    return lights
