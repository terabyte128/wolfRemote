from typing import List
from typing_extensions import Literal
from fastapi import APIRouter, HTTPException
from pydantic import validator
from pydantic.main import BaseModel

from server.api import RECEIVER

receiver_router = APIRouter(tags=["receiver"])


class VolumeRequest(BaseModel):
    amount: int
    direction: Literal["up", "down"]

    @validator("amount")
    def validate_amount(cls, value: int):
        if value < 1 or value > 5:
            raise ValueError("amount must be between 1 and 5")

        return value


@receiver_router.put("/volume", status_code=204)
def change_volume(volume: VolumeRequest):
    if volume.direction == "up":
        RECEIVER.send_command("VOLUP", volume.amount)
    else:
        RECEIVER.send_command("VOLDOWN", volume.amount)

    return "", 204


class InputResponse(BaseModel):
    inputs: List[str]


@receiver_router.get("/input", response_model=InputResponse)
def get_inputs() -> InputResponse:
    return InputResponse(inputs=RECEIVER.get_inputs())


class InputRequest(BaseModel):
    input: str


@receiver_router.put("/input", status_code=204)
def set_input(input: InputRequest):
    if input.input not in RECEIVER.get_inputs():
        raise HTTPException(
            400, f"input is invalid, expected {RECEIVER.get_inputs()}"
        )

    RECEIVER.set_input(input.input)
