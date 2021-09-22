import logging
from fastapi import FastAPI
from pydantic import BaseModel

from .api.tv import tv_router
from .api.lights import light_router
from .api.receiver import receiver_router
from .api.sequences import sequences_router

logging.getLogger().setLevel(logging.INFO)

app = FastAPI(title="wolfRemote", description="beep boop control things")
app.include_router(tv_router, prefix="/api/v1/tv")
app.include_router(light_router, prefix="/api/v1/lights")
app.include_router(receiver_router, prefix="/api/v1/receiver")
app.include_router(sequences_router, prefix="/api/v1/sequences")


class RootResponse(BaseModel):
    hello: str


@app.get("/", response_model=RootResponse)
def root():
    return RootResponse(hello="world")
