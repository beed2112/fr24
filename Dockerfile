FROM alpine
LABEL maintainer=heywoodlh

RUN apk --no-cache add swatch ssmtp mosquitto mosquitto-clients

RUN mkdir -p /logs
VOLUME /logs
ENTRYPOINT [ "swatchdog", "--config-file", "/etc/swatch/swatchrc"]

