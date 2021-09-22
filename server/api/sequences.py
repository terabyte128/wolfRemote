from typing import List
import wakeonlan
from fastapi import APIRouter, HTTPException
from pydantic import validator
from pydantic.main import BaseModel

from server.api import TV, RECEIVER

sequences_router = APIRouter(tags=["sequences"])


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


class SequencesResponse(BaseModel):
    all_sequences: List[str]


@sequences_router.get("", response_model=SequencesResponse)
def get_sequences():
    return SequencesResponse(all_sequences=list(SEQUENCES.keys()))


class RunSequenceRequest(BaseModel):
    sequence: str


@sequences_router.put("", status_code=204)
def run_sequence(sequence: RunSequenceRequest):
    if sequence.sequence in SEQUENCES.keys():
        SEQUENCES[sequence.sequence]()
    else:
        raise HTTPException(
            400, f"invalid sequence, expected {list(SEQUENCES.keys())}"
        )
