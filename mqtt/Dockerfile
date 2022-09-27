FROM eclipse-mosquitto

COPY passwd /mosquitto/config
COPY mosquitto.conf /mosquitto/config
COPY entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]
CMD ["/usr/sbin/mosquitto","-c","/mosquitto/config/mosquitto.conf"]