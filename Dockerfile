FROM alpine
LABEL maintainer=beed2112

RUN apk --no-cache add swatch ssmtp mosquitto mosquitto-clients tzdata

ENV TZ=America/Phoenix

RUN mkdir -p /logs
RUN mkdir /fr24 
COPY startupWrapper.sh /fr24/.
COPY ncWrapper.sh /fr24/.
COPY fr24mq.sh /fr24/.
COPY fr24mq.confg /fr24/.
RUN chmod +x /fr24/*.sh

VOLUME /logs

CMD ["ash", "/fr24/startupWrapper.sh"]
