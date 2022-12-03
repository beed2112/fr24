FROM alpine
LABEL maintainer=beed2112

RUN apk --no-cache add swatch ssmtp mosquitto mosquitto-clients

RUN mkdir -p /logs
RUN mkdir /fr24 
RUN COPY startupWrapper.sh /fr24/.
RUN COPY ncWrapper.sh /fr24/.
RUN chmod +x /fr24/*.sh

VOLUME /logs
#ENTRYPOINT [ "swatchdog", "--config-file", "/etc/swatch/swatchrc"]
ENTRYPOINT ["startupWrapper.sh"]
