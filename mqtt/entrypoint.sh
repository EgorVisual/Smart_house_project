#!/bin/sh

PASSWDFILE=/mosquitto/config/passwd
FLAG=/mosquitto/config/flag

if [ -f $PASSWDFILE ] && [ ! -f $FLAG ]; then
    echo "converting password file"
    mosquitto_passwd -U $PASSWDFILE
    touch $FLAG
fi

exec "$@"