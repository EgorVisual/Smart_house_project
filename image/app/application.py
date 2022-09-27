import asyncio

from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from loguru import logger

from .mqtt import mqtt_handler, RESPONSE_MQTT_QUEUE
from .serial import background_receive_serial
from .states_file import init_states
from .websockethandler import WebSocketHandler

app = FastAPI()

logger.add("./smart-house-backend-data/logs.log", rotation="500 MB")

LOGGER_PREFIX = "CLIENT: "

WS_CLIENTS: Set[WebSocket] = set()
RESPONSE_QUEUE = asyncio.Queue()
REQUEST_QUEUE = asyncio.Queue()

# var ws = new WebSocket("ws://localhost:8000/ws"); -- For development on local machine with windows and docker

# < ul
# id = 'messages' >
# < / ul >
# < script >
# var
# ws = new
# WebSocket("ws://192.168.0.63:8081/ws");
# ws.onmessage = function(event)
# {
#     var
# messages = document.getElementById('messages')
# var
# message = document.createElement('li')
# var
# content = document.createTextNode(event.data)
# message.appendChild(content)
# messages.appendChild(message)
# const
# device_states = JSON.parse(event.data);

CONTROL_PANEL_HTML = """
<!DOCTYPE html>
<html>
    <style>
    #line_block { 
        width:30%; 
        height:10%; 
        background:#ffffff; 
        float:left; 
        margin: 0 15px 15px 0; 
        text-align:center;
        padding: 10px;
        }
    </style>
    <head>
        <title>Control panel</title>
    </head>
    <body>
        <h1>Control panel</h1>
        <div id="line_block"> 
        Sonoff_mini_1: 
        <button onclick="sendCommand(event, 'toggle', 'mini_1', 'POWER')" id="toggle_state_mini_1">Toggle</button>
        <output id = "state_mini_1" value = "OFF"/>
        </div>
        <div id="line_block"> 
        Sonoff_mini_2: 
        <button onclick="sendCommand(event, 'toggle', 'mini_2', 'POWER')" id="toggle_state_mini_2">Toggle</button>
        <output id = "state_mini_2" value = "OFF"/>
        </div>
        <div id="line_block"> 
        Sonoff_4ch_1_1: 
        <button onclick="sendCommand(event, 'toggle', '4ch_1', 'POWER1')" id="toggle_state_4ch_1_1">Toggle</button>
        <output id = "state_4ch_1_1" value = "OFF"/>
        </div>
        <div id="line_block"> 
        Sonoff_4ch_1_2: 
        <button onclick="sendCommand(event, 'toggle', '4ch_1', 'POWER2')" id="toggle_state_4ch_1_2">Toggle</button>
        <output id = "state_4ch_1_2" value = "OFF"/>
        </div>
                <div id="line_block"> 
        Sonoff_4ch_1_3: 
        <button onclick="sendCommand(event, 'toggle', '4ch_1', 'POWER3')" id="toggle_state_4ch_1_3">Toggle</button>
        <output id = "state_4ch_1_3" value = "OFF"/>
        </div>
        <div id="line_block"> 
        Sonoff_4ch_1_4: 
        <button onclick="sendCommand(event, 'toggle', '4ch_1', 'POWER4')" id="toggle_state_4ch_1_4">Toggle</button>
        <output id = "state_4ch_1_4" value = "OFF"/>
        </div>
        <div>---------------------------------------------------</div>
        <div>MQTT Temperature sensor xxx319:</div>
        <div>battery:   <output id = "battery_319" value = "0"/></div>
        <div>humidity:  <output id = "humidity_319" value = "0"/></div>
        <div>pressure:  <output id = "pressure_319" value = "0"/></div>
        <div>temperature:   <output id = "temperature_319" value = "0"/></div>
        <div>---------------------------------------------------</div>
        <div>MQTT Motion sensor sonoff xxx31c:</div>
        <div>battery:   <output id = "battery_31c" value = "0"/></div>
        <div>occupancy:   <output id = "occupancy_31c" value = "False"/></div>
        <div>---------------------------------------------------</div>
        <div>MQTT Motion sensor sonoff xxx513:</div>
        <div>battery:   <output id = "battery_513" value = "0"/></div>
        <div>occupancy:   <output id = "occupancy_513" value = "False"/></div>
        <div>---------------------------------------------------</div>
        <div>MQTT Motion sensor aqara xxx3f8:</div>
        <div>battery:   <output id = "battery_3f8" value = "0"/></div>
        <div>occupancy:   <output id = "occupancy_3f8" value = "False"/></div>
        <div>---------------------------------------------------</div>
        <div>MQTT Motion sensor aqara xxxcef:</div>
        <div>battery:   <output id = "battery_cef" value = "0"/></div>
        <div>occupancy:   <output id = "occupancy_cef" value = "False"/></div>
        <div>---------------------------------------------------</div>
        <div>MQTT Water leak sensor xxxbea:</div>
        <div>battery:   <output id = "battery_bea" value = "0"/></div>
        <div>water_leak:   <output id = "water_leak_bea" value = "false"/></div>
        <div>---------------------------------------------------</div>
        <div>MQTT Open sensor xxx20d:</div>
        <div>contact:   <output id = "contact_20d" value = "true"/></div>
        <div>---------------------------------------------------</div>
        <div>MQTT Open sensor xxxe55:</div>
        <div>contact:   <output id = "contact_e55" value = "true"/></div>
        <div>---------------------------------------------------</div>
        <div>MQTT Open sensor xxx1ab:</div>
        <div>contact:   <output id = "contact_1ab" value = "true"/></div>
        <div>---------------------------------------------------</div>
        <div>MQTT Temperature sensor:</div>
        <div>temperature:   <output id = "temperature_serial" value = "0"/></div>
        <script>
            var ws = new WebSocket("ws://192.168.0.63:8081/ws");
            ws.onmessage = function(event) {
                const device_states = JSON.parse(event.data);
                console.log(device_states)
                if (device_states["name"] == "mini_1"){
                    document.getElementById("state_mini_1").value = device_states["parameters"]["POWER"]
                }
                if (device_states["name"] == "mini_2"){
                    document.getElementById("state_mini_2").value = device_states["parameters"]["POWER"]
                }
                if (device_states["name"] == "4ch_1"){
                    for (key in Object.keys(device_states["parameters"])){
                        if (Object.keys(device_states["parameters"])[key] == "POWER1"){
                            document.getElementById("state_4ch_1_1").value = device_states["parameters"]["POWER1"]
                        }
                        if (Object.keys(device_states["parameters"])[key] == "POWER2"){
                            document.getElementById("state_4ch_1_2").value = device_states["parameters"]["POWER2"]
                        }
                        if (Object.keys(device_states["parameters"])[key] == "POWER3"){
                            document.getElementById("state_4ch_1_3").value = device_states["parameters"]["POWER3"]
                        }
                        if (Object.keys(device_states["parameters"])[key] == "POWER4"){
                            document.getElementById("state_4ch_1_4").value = device_states["parameters"]["POWER4"]
                        }
                    }
                }
                if (device_states["name"]== "0x00124b002214d31c"){
                    document.getElementById("battery_31c").value = device_states["parameters"]["battery"]
                    document.getElementById("occupancy_31c").value = device_states["parameters"]["occupancy"]
                }
                if (device_states["name"]== "0x00158d000423b3f8"){
                    document.getElementById("battery_3f8").value = device_states["parameters"]["battery"]
                    document.getElementById("occupancy_3f8").value = device_states["parameters"]["occupancy"]
                }
                if (device_states["name"]== "0x00158d000423bcef"){
                    document.getElementById("battery_cef").value = device_states["parameters"]["battery"]
                    document.getElementById("occupancy_cef").value = device_states["parameters"]["occupancy"]
                }
                if (device_states["name"]== "0x00158d000422e20d"){
                    document.getElementById("contact_20d").value = device_states["parameters"]["contact"]
                }
                if (device_states["name"]== "0x00124b002214d513"){
                    document.getElementById("battery_513").value = device_states["parameters"]["battery"]
                    document.getElementById("occupancy_513").value = device_states["parameters"]["occupancy"]
                }
                if (device_states["name"]== "0x00158d0002321319"){
                    document.getElementById("battery_319").value = device_states["parameters"]["battery"]
                    document.getElementById("humidity_319").value = device_states["parameters"]["humidity"]
                    document.getElementById("pressure_319").value = device_states["parameters"]["pressure"]
                    document.getElementById("temperature_319").value = device_states["parameters"]["temperature"]
                }
                if (device_states["name"]== "0x00158d000271bbea"){
                    document.getElementById("battery_bea").value = device_states["parameters"]["battery"]
                    document.getElementById("water_leak_bea").value = device_states["parameters"]["water_leak"]
                }
                if (device_states["name"]== "0x00158d000410de55"){
                  document.getElementById("contact_e55").value = device_states["parameters"]["contact"]
                }
                if (device_states["name"]== "0x00158d000422e1ab"){
                    document.getElementById("contact_1ab").value = device_states["parameters"]["contact"]
                }
                if (device_states["name"]== "Temperature_sensor"){
                    document.getElementById("temperature_serial").value = device_states["parameters"]["temperature"]
                }
                }
            function sendCommand(event, button_command, relay_name, relay_info) {
                const request = JSON.stringify({name: relay_name, info: relay_info, state: button_command});
                ws.send(request)
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(CONTROL_PANEL_HTML)


@app.on_event("startup")
async def start_background_tasks():
    init_states()
    asyncio.create_task(mqtt_handler())
    asyncio.create_task(background_receive_serial(RESPONSE_QUEUE))


@app.websocket("/ws")
async def websocket(websocket: WebSocket):
    websocket_client = WebSocketHandler(websocket, WS_CLIENTS, RESPONSE_MQTT_QUEUE, RESPONSE_QUEUE, REQUEST_QUEUE)
    await websocket_client.greet_new_client()
    WS_CLIENTS.add(websocket)
    try:
        await asyncio.gather(
            websocket_client.handle_messages_from_mqtt(),
            websocket_client.receive_request(),
            websocket_client.process_response()
        )
    except WebSocketDisconnect:
        WS_CLIENTS.remove(websocket)
        logger.info(f'{LOGGER_PREFIX}client ({websocket}) disconnected.')
