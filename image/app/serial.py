import os
import re

import asyncio
from asyncio import Queue

from typing import Dict

from loguru import logger

from serial import Serial, SerialException

from .domain import SensorResponse

LOGGER_PREFIX = "Serial:"

ser = Serial(
    port=os.environ.get("SERIAL_PORT"),
    baudrate=int(os.environ.get('SERIAL_BAUDRATE', 9600)),
    timeout=int(os.environ.get('SERIAL_TIMEOUT', 0)),
)
# For development on windows without container.
# ser = Serial(
#     port='COM8',
#     baudrate=int(os.environ.get('SERIAL_BAUDRATE', 9600)),
#     timeout=int(os.environ.get('SERIAL_TIMEOUT', 0)),
# )

TEMPERATURE_SENSOR_NAME = 'Temperature_sensor'


async def background_receive_serial(response_queue: Queue) -> None:
    while True:
        serial_message: str = None
        message: str = None
        if ser.is_open and ser.in_waiting > 0:
            try:
                serial_message = ser.readline().decode("ascii")
                message = parse_serial(serial_message)
            except SerialException as e:
                logger.error(f"{LOGGER_PREFIX} serial error: {e}")
            except UnicodeDecodeError as e:
                logger.error(f'{LOGGER_PREFIX} unable to decode message ({repr(e.object)}); error:\"{e}\", ({ser.port}).')
            except IOError:
                logger.error(f'{LOGGER_PREFIX} unable to establish connection to serial port ({ser.port}).')
                ser.close()
        if message is not None:
            response = SensorResponse(name='Temperature_sensor', parameters=message)
            response_queue.put_nowait(response)
        await asyncio.sleep(.5)


def parse_serial(serial_message: str) -> Dict[str, str] or None:
    if re.match(r'^Temperature:(\d+\.\d*)\r\n$', serial_message):
        delimiter_position = serial_message.find(':')
        new_line_position = serial_message.find('\r\n')
        temperature = serial_message[delimiter_position + 1:new_line_position]
        return {'temperature': temperature}
    return None
