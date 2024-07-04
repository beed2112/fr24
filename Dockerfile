FROM python:3

RUN apt-get update && \
    apt-get install -y bash-completion mosquitto-clients tzdata vim iputils-ping git && \
    pip install --upgrade pip && \
    pip install python-socketio websocket-client termcolor paho-mqtt datetime requests

RUN wget "https://raw.githubusercontent.com/beed2112/fr24/masterOfAll/fr24Listner.py"
RUN wget "https://raw.githubusercontent.com/beed2112/fr24/masterOfAll/aircraft.py"
RUN wget "https://raw.githubusercontent.com/beed2112/fr24/masterOfAll/nohitAircraft.py"

ENV TZ=America/Phoenix
ENV MQTT_SERVER=mqtt
ENV MQTT_USER=me
ENV MQTT_PASS=me
ENV DATABASE=/media/freewill/beed2112/hacktop/fr24db/aircraftMon.db
ENV RECEIVER_URL=http://adsblistener

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENTRYPOINT ["python", "/fr24Listner.py"]
