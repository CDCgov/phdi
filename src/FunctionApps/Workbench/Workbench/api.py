import os

from fastapi import FastAPI
from pydantic import BaseModel

from phdi_transforms.basic import transform_name, transform_phone
from phdi_transforms.geo import geocode, get_smartystreets_client, GeocodeResult


app = FastAPI()


class BasicResponse(BaseModel):
    value: str


@app.get("/basic/name")
async def standardize_name(name: str) -> BasicResponse:
    return BasicResponse(value=transform_name(name))


@app.get("/basic/phone")
async def standardize_phone(phone: str) -> dict:
    return BasicResponse(value=transform_phone(phone))


@app.get("/geo/address")
async def geocode_address(address: str) -> GeocodeResult:
    client = get_smartystreets_client(
        os.environ.get("SMARTYSTREETS_AUTH_ID"),
        os.environ.get("SMARTYSTREETS_AUTH_TOKEN"),
    )
    return geocode(client, address)
