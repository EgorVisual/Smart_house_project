import asyncio
import json
from asyncio import Queue
from json import JSONDecodeError
from typing import Set, Dict, Literal

from fastapi import WebSocket

from loguru import logger
from pydantic import ValidationError

from .domain import ResponseWebsocket, GenericResponse
from .mqtt import publish_command, DEVICE_MAP, _LOCATION_OF_DEVICE, _TYPES_OF_DEVICE
from .states_file import read_states, write_states

LOGGER_PREFIX = 'WS handler: '


class WebSocketHandler:
    def __init__(self, websocket: WebSocket, ws_clients: Set[WebSocket], response_mqtt_queue: Queue,
                 response_queue: Queue, request_queue: Queue) -> None:
        self.client = websocket
        self.ws_clients = ws_clients
        self.response_mqtt_queue = response_mqtt_queue
        self.response_queue = response_queue
        self.request_queue = request_queue

    async def greet_new_client(self) -> None:
        await self.client.accept()
        logger.info(f'{LOGGER_PREFIX} New client "{self.client}" successfully connected!')
        for device_name in DEVICE_MAP.keys():
            states = self._restore_parameters(device_name)
            response = ResponseWebsocket(name=device_name, type=states['type'], parameters=states['parameters'])
            await self.client.send_text(response.json())

    async def handle_messages_from_mqtt(self) -> None:
        while True:
            if not self.response_mqtt_queue.empty():
                message_from_mqtt = self.response_mqtt_queue.get_nowait()
                if message_from_mqtt is not None:
                    device_info = DEVICE_MAP[message_from_mqtt.name]
                    self._update_states(message_from_mqtt.name, message_from_mqtt.parameters,
                                        message_from_mqtt.mqtt_topic, device_info['type'], device_info['location'])
                    await self._update_pages(ResponseWebsocket(name=message_from_mqtt.name, type=device_info['type'],
                                                               parameters=message_from_mqtt.parameters),
                                             self.ws_clients)
            await asyncio.sleep(.2)

    async def receive_request(self) -> None:
        while True:
            request = await self.client.receive_text()
            logger.info(f'{LOGGER_PREFIX}we have message from client: {request}')
            try:
                parsed_json = json.loads(request)
                if parsed_json['state'] == "toggle":
                    states = read_states()
                    device_states = states[parsed_json['name']]
                    command: str
                    if device_states['parameters'][f"{parsed_json['info']}"] == 'ON':
                        command = 'OFF'
                    elif device_states['parameters'][f"{parsed_json['info']}"] == 'OFF':
                        command = 'ON'
                    else:
                        command = 'None'
                    self._send_command_mqtt(parsed_json['name'], parsed_json['info'], command)
            except (JSONDecodeError, ValidationError) as e:
                await self.client.send_text((GenericResponse(status="error", detail=str(e)).json(by_alias=True)))
            await asyncio.sleep(.2)

    async def process_response(self):
        while True:
            if not (self.response_queue.empty()):
                response = self.response_queue.get_nowait()
                if response.name in DEVICE_MAP:
                    device_info = DEVICE_MAP[response.name]
                    self._update_states(device_name=response.name, device_parameters=response.parameters,
                                        device_mqtt_topic=None, device_type=device_info['type'],
                                        device_location=device_info['location'])
                    self.response_queue.task_done()
                    updated_parameters = self._restore_parameters(response.name)
                    response_to_client = ResponseWebsocket(name=response.name,
                                                           type=updated_parameters['type'],
                                                           parameters=updated_parameters['parameters'])
                    await self._update_pages(response_to_client, self.ws_clients)
            await asyncio.sleep(.5)

    @staticmethod
    def _update_states(device_name: str, device_parameters: Dict[str, str], device_mqtt_topic: str or None,
                       device_type: str = Literal[_TYPES_OF_DEVICE],
                       device_location: str = Literal[_LOCATION_OF_DEVICE]) -> None:
        states_from_file = read_states()
        if device_name in states_from_file:
            if device_type in ['sonoff_mini', 'sonoff_4ch', 'sonoff_d1']:
                for key in device_parameters.keys():
                    logger.info(f'{LOGGER_PREFIX}State: {key} - {device_parameters[f"{key}"]}')
                    states_from_file[device_name]['parameters'][f'{key}'] = device_parameters[f'{key}']
                    states_from_file[device_name]['type'] = device_type
            else:
                states_from_file[device_name]['parameters'] = device_parameters
                states_from_file[device_name]['type'] = device_type
            if device_mqtt_topic is not None:
                states_from_file[device_name]['mqtt_topic'] = device_mqtt_topic
            states_from_file[device_name]['location'] = device_location
        write_states(states_from_file)

    @staticmethod
    def _restore_parameters(device_name: str) -> Dict:
        all_states = read_states()
        device_states = all_states[device_name]
        return device_states

    @staticmethod
    async def _update_pages(response: ResponseWebsocket, clients: Set[WebSocket]) -> None:
        logger.info(f'{LOGGER_PREFIX}Send updated data to clients: {response.json()}')
        for client in clients:
            await client.send_text(response.json())

    @staticmethod
    def _send_command_mqtt(device_name: str, device_info: str, command: str):
        states = read_states()
        device_states = states[device_name]
        topic = device_states['mqtt_topic']
        topic_words = topic.split('/')[1:-1]
        raw_topic: str = ''
        for word in topic_words:
            raw_topic += word + '/'
        command_topic = 'cmnd/' + raw_topic + device_info
        publish_command(command_topic, command)
