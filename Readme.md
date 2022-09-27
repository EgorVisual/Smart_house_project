# Smart house

# Project description:

This project is a base for "Smart house" backend. 

And it will be updated later. 

The main idea:
User can control the relays(Sonoff mini, Sonoff 4ch) and monitor sensors(Aqara motion sensor, Aqara Temperature and Humidity Sensor,
Aqara Door and Window Sensor and so on) by using a web-interface.

The project was built by using FastAPI. Commands to the backend are sent using a websocket. 

To communicate with sensors and relays, it is used Mqtt. To receive data from zigbee sensor you should use a zigbee-stick.
This project create container with zigbee2mqtt service to get data by zigbee. To manage data used container with Mqtt broker. 
Relays send data to Mqtt broker by Wi-Fi. 

Also in this project, I implemented receiving data on the serial port from the temperature sensor, which is installed on the arduino.

Before lunching the docker-compose file you should to create .env file. 

Example:

ZIGBEE_STICK=(serial port of the zigbee-stick)

SERIAL_PORT=(serial port of the arduino)

SERIAL_BAUDRATE=9600

SERIAL_TIMEOUT=0

MQTT_HOST=(ip of your mqtt broker)

MQTT_PORT=1883

MQTT_USERNAME=(mqtt username)

MQTT_PASSWORD=(mqtt password)


