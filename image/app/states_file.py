import json

from loguru import logger

FILE_PATH = './smart-house-backend-data/states_file.json'

LOGGER_PREFIX = "STATE_FILE: "

_INITIAL_PARAMETERS: dict = {
    'Temperature_sensor':
        {
            'type': 'None',
            'location': "None",
            'parameters':
                {
                    'temperature': 0
                }
        },
    '0x00124b002214d31c':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    "battery": 0,
                    "battery_low": 'false',
                    "linkquality": 0,
                    "occupancy": 'false',
                    "tamper": 'false',
                    "voltage": 0
                }
        },
    '0x00158d000423b3f8':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    "battery": 0,
                    "device_temperature": 0,
                    "illuminance": 0,
                    "illuminance_lux": 0,
                    "linkquality": 0,
                    "occupancy": 'false',
                    "power_outage_count": 0,
                    "voltage": 0
                }
        },
    '0x00158d000423bcef':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    "battery": 0,
                    "device_temperature": 0,
                    "illuminance": 0,
                    "illuminance_lux": 0,
                    "linkquality": 0,
                    "occupancy": 'false',
                    "power_outage_count": 0,
                    "voltage": 0
                }
        },
    '0x00158d000422e20d':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    "contact": 'true',
                    "linkquality": 0
                }
        },
    '0x00124b002214d513':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    "battery": 0,
                    "battery_low": 'false',
                    "linkquality": 0,
                    "occupancy": 'false',
                    "tamper": 'false',
                    "voltage": 0
                }
        },
    '0x00158d0002321319':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    'battery': 0,
                    'humidity': 0,
                    'linkquality': 0,
                    'power_outage_count': 0,
                    'pressure': 0,
                    'temperature': 0,
                    'voltage': 0
                }
        },
    '0x00158d000271bbea':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    "battery": 0,
                    "device_temperature": 0,
                    "linkquality": 0,
                    "power_outage_count": 0,
                    "voltage": 0,
                    "water_leak": "false"
                }
        },
    '0x00158d000410de55':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    "contact": 'true',
                    "linkquality": 0
                }
        },
    '0x00158d000422e1ab':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    "battery": 0,
                    "contact": 'true',
                    "device_temperature": 0,
                    "linkquality": 0,
                    "power_outage_count": 0,
                    "voltage": 0
                }
        },
    'mini_1':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    'POWER': 'OFF'
                }
        },
    'mini_2':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    'POWER': 'OFF'
                }
        },
    '4ch_1':
        {
            'type': 'None',
            "mqtt_topic": "None",
            'location': "None",
            'parameters':
                {
                    'POWER1': 'OFF',
                    'POWER2': 'OFF',
                    'POWER3': 'OFF',
                    'POWER4': 'OFF'
                }
        }
}


def init_states() -> None:
    try:
        with open(FILE_PATH, 'r') as file:
            states = json.load(file)
            logger.info(f'{LOGGER_PREFIX}Received init states from file: {FILE_PATH}')
    except:
        with open(FILE_PATH, 'w') as file:
            json.dump(_INITIAL_PARAMETERS, file, indent=4)
            logger.info(f'{LOGGER_PREFIX}New states file was successfully created: {FILE_PATH}')


def read_states() -> dict:
    with open(FILE_PATH, 'r') as file:
        try:
            states = json.load(file)
            logger.info(f'{LOGGER_PREFIX}Successfully received states from file')
            return states
        except Exception as e:
            logger.error(f'{LOGGER_PREFIX}Received states from file was uncorrected: {e}')
        return {}


def write_states(states: dict) -> None:
    with open(FILE_PATH, 'w') as file:
        json.dump(states, file, indent=4)
        logger.info(f'{LOGGER_PREFIX}States was successfully written to file')
