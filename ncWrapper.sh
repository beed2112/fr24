#echo "$1"
#echo "$2"

DUMP1090IP=`grep DUMP1090IP fr24mq.confg | awk -F= '{print $2}'`
DUMP1090PORT=`grep DUMP1090PORT fr24mq.confg | awk -F= '{print $2}'`
MQTTIP=`grep MQTTIP fr24mq.confg | awk -F= '{print $2}'`
MQTTPORT=`grep MQTTPORT fr24mq.confg | awk -F= '{print $2}'`
MQTTTOPIC=`grep MQTTTOPIC fr24mq.confg | awk -F= '{print $2}'`
CALLSIGNDESCRIPTION=`grep CALLSIGNDESCRIPTION fr24mq.confg | awk -F= '{print $2}'`

echo "$DUMP1090IP $DUMP1090PORT"
#while  true  ; do nc  192.168.0.116 30003 | grep -f  /fr24/watchfor| sed 's/,/ /g'; done
while  true  ; do nc  $DUMP1090IP $DUMP1090PORT|  sed 's/,/ /g'; done