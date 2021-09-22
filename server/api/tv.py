from fastapi import APIRouter, HTTPException
from pydantic.main import BaseModel

from server.api import TV

tv_router = APIRouter(tags=["tv"])


@tv_router.get("/picture_mode", response_model=TV.PictureMode)
def get_picture_mode():
    return TV.get_picture_mode()


class SetPictureMode(BaseModel):
    mode: str


@tv_router.put("/picture_mode", response_model=TV.PictureMode)
def set_picture_mode(mode: SetPictureMode):
    current_modes = TV.get_picture_mode()

    if mode.mode not in current_modes.modes:
        raise HTTPException(400, detail=f"{mode.mode} is not a valid mode")

    TV.set_picture_mode(mode.mode)
    return TV.get_picture_mode()


class SetPowerState(BaseModel):
    power_state: bool


@tv_router.get("/power_state", response_model=SetPowerState)
def get_power_state():
    return SetPowerState(power_state=TV.get_power_state())


@tv_router.put("/power_state", response_model=SetPowerState)
def set_power_state(power_state: SetPowerState):
    if power_state.power_state:
        TV.power_on()
    else:
        TV.power_off()

    return get_power_state()


@tv_router.get("/input", response_model=TV.Input)
def get_input():
    return TV.get_input()


class SetInput(BaseModel):
    input: str


@tv_router.put("/input", response_model=TV.Input)
def set_input(input: SetInput):
    current_inputs = TV.get_input()

    if not input.input in current_inputs.inputs:
        raise HTTPException(400, detail=f"{input.input} is not a valid input")

    TV.set_input(input.input)
    return get_input()


@tv_router.get("/backlight", response_model=TV.Backlight)
def get_backlight():
    return TV.get_backlight()


class SetBacklight(BaseModel):
    backlight: int


@tv_router.put("/backlight", response_model=TV.Backlight)
def set_backlight(backlight: SetBacklight):
    current_backlight = TV.get_backlight()
    new_backlight = backlight.backlight

    if (
        new_backlight < current_backlight.min
        or new_backlight > current_backlight.max
    ):
        return {
            "error": f"backlight must be between {current_backlight.min} and {current_backlight.max}"
        }

    TV.set_backlight(new_backlight)
    return get_backlight()


@tv_router.put("/force_reboot", status_code=204)
def force_reboot():
    TV.force_reboot()
