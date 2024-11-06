FROM eclipse-mosquitto:2.0.20

WORKDIR /

COPY ./mosquitto/ ./mosquitto/

CMD ["mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]