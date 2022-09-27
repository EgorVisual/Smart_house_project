import asyncio
import json
import os

from typing import Dict

import paho.mqtt.client as mqtt

from asyncio_paho import AsyncioPahoClient

from loguru import logger

from .domain import ResponseMqtt

RESPONSE_MQTT_QUEUE = asyncio.Queue()

# ----------------------------------MQTT_CONNECTION_TO_BROKER_INFO---------------------------------------------
MQTT_HOST = str(os.environ.get("MQTT_HOST"))
MQTT_PORT = int(os.environ.get("MQTT_PORT"))
MQTT_USERNAME = str(os.environ.get("MQTT_USERNAME"))
MQTT_PASSWORD = str(os.environ.get("MQTT_PASSWORD"))
MQTT_SUBSCRIBING_TOPICS = [
    ("stat/tasmota/#", 0),
    ("zigbee2mqtt/#", 0)
]
# -----------------------------------CODES_OF_MQTT_RESPONSES---------------------------------------------------
MQTT_RESULTS = {
    '0': 'Successfully connected to mqtt broker',
    '1': 'incorrect protocol version',
    '2': 'invalid client identifier',
    '3': 'server unavailable',
    '4': 'bad username or password',
    '5': 'not authorised',
}
# -------------------------------------MQTT_DEVISES_INFO------------------------------------------------------
DEVICE_MAP: Dict[str, Dict[str, str]] = {
    'Temperature_sensor': {
        'type': 'arduino',
        'location': "Smart house"
    },
    '0x00124b002214d31c': {
        'type': 'motion_sensor_sonoff',
        'location': "Smart house"
    },
    '0x00158d000423b3f8': {
        'type': 'motion_sensor_aqara',
        'location': "Smart house"
    },
    '0x00158d000423bcef': {
        'type': 'motion_sensor_aqara',
        'location': "Smart house"
    },
    '0x00158d000422e20d': {
        'type': 'door_sensor',
        'location': "Smart house"
    },
    '0x00124b002214d513': {
        'type': 'motion_sensor_sonoff',
        'location': "Smart house"
    },
    '0x00158d0002321319': {
        'type': 'temperature_sensor',
        'location': "Smart house"
    },
    '0x00158d000271bbea': {
        'type': 'water_leak_sensor',
        'location': "Smart house"
    },
    '0x00158d000410de55': {
        'type': 'door_sensor',
        'location': "Smart house"
    },
    '0x00158d000422e1ab': {
        'type': 'door_sensor',
        'location': "Smart house"
    },
    'mini_1': {
        'type': 'sonoff_mini',
        'location': "Smart house"
    },
    'mini_2': {
        'type': 'sonoff_mini',
        'location': "Smart house"
    },
    '4ch_1': {
        'type': 'sonoff_4ch',
        'location': "Smart house"
    }
}

_TYPES_OF_DEVICE = (
    'sonoff_mini',
    'sonoff_4ch',
    'sonoff_d1',
    'temperature_sensor',
    'door_sensor',
    'water_leak_sensor',
    'motion_sensor_sonoff',
    'motion_sensor_aqara'
)

_LOCATION_OF_DEVICE = (
    "Smart house"
)
# ----------------------------------------------------------------------------------------------------------

LOGGER_PREFIX = "MQTT: "


async def async_on_connect(client, userdata, flags_dict, result):
    if result == 0:
        logger.info(f'{LOGGER_PREFIX} {MQTT_RESULTS[f"{result}"]}')
        await client.asyncio_subscribe(MQTT_SUBSCRIBING_TOPICS)
    else:
        logger.error(f'{LOGGER_PREFIX} Connection refused – {MQTT_RESULTS[f"{result}"]}')


async def async_on_message(client, userdata, message):
    try:
        raw_message: str = str(message.payload)
        if not ('POWER' in message.topic.split('/')[-1]):
            main_topic: str = message.topic.split('/')[0]
            device_name: str
            if main_topic == 'zigbee2mqtt':
                device_name = message.topic.split('/')[-1]
            else:
                device_name = message.topic.split('/')[-2]
            if device_name in DEVICE_MAP:
                prepared_message = raw_message[2:-1]
                device_parameters = json.loads(prepared_message)
                response = ResponseMqtt(name=device_name, mqtt_topic=message.topic, parameters=device_parameters)
                RESPONSE_MQTT_QUEUE.put_nowait(response)
                logger.info(f'{LOGGER_PREFIX} Received from "{device_name}" : {device_parameters}')
    except:
        logger.error(f'{LOGGER_PREFIX} Received message from broker was uncorrected: {message.topic} : {raw_message}')


async def mqtt_handler():
    async with AsyncioPahoClient() as client:
        client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
        client.asyncio_listeners.add_on_connect(async_on_connect)
        client.asyncio_listeners.add_on_message(async_on_message)
        while True:
            try:
                await client.asyncio_connect(MQTT_HOST, MQTT_PORT, keepalive=300)
            except (TimeoutError, ConnectionRefusedError) as e:
                logger.error(f"{LOGGER_PREFIX}Problems with connection: {e}")


def init_publisher():
    client = mqtt.Client()
    client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
    client.connect(MQTT_HOST, MQTT_PORT)
    return client


def publish_command(topic: str, command: str):
    mqtt_publisher = init_publisher()
    mqtt_publisher.publish(topic, command)
