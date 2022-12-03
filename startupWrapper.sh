#


#gather values

DUMP1090IP=`grep DUMP1090IP fr24mq.confg | awk -F= '{print $2}'`
DUMP1090PORT=`grep DUMP1090PORT fr24mq.confg | awk -F= '{print $2}'`
MQTTIP=`grep MQTTIP fr24mq.confg | awk -F= '{print $2}'`
MQTTPORT=`grep MQTTPORT fr24mq.confg | awk -F= '{print $2}'`
MQTTTOPIC=`grep MQTTTOPIC fr24mq.confg | awk -F= '{print $2}'`
CALLSIGNDESCRIPTION=`grep CALLSIGNDESCRIPTION fr24mq.confg | awk -F= '{print $2}'`

# this is for testing not needed when starting container
rm callSignDescription 2> /dev/null

#grab the call sign description file -- we use it to build the list of callsigns to watch for, get plane description, and BUILD SWATCH RULES
wget "$CALLSIGNDESCRIPTION" 


awk -F@ '{print $1}' callSignDescription > /fr24/watchfor

#build swatch rules 
TICK="'"
awk -F@ '{print "watchfor /"$1"/ \n           throttle 15:00,key=$10\n           echo "  $3"\n           exec /fr24/fr24mq.sh \047$_[10]\047  "}' callSignDescription | sed "s/$$/$TICK/g"> fr24rules

/usr/bin/swatchdog -c /fr24/fr24rules -p /fr24/ncWrapper.sh
#./ncWrapper.sh