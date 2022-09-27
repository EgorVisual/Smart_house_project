from typing import Literal, Optional

from pydantic import BaseModel, Field


class GenericResponse(BaseModel):
    status: str = Literal['ok', 'error']
    detail: Optional[str] = None


class ResponseMqtt(BaseModel):
    name: str
    mqtt_topic: str
    parameters: dict


class SensorResponse(BaseModel):
    name: str
    parameters: dict


class ResponseWebsocket(BaseModel):
    name: str
    type: str
    parameters: dict

    class Config:
        allow_population_by_field_name = True
