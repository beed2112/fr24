#desc=`grep -i $1 ./callSignDescription | awk -F @ '{print $2}'`

cd /fr24

DUMP1090IP=`grep DUMP1090IP fr24mq.confg | awk -F= '{print $2}'`
DUMP1090PORT=`grep DUMP1090PORT fr24mq.confg | awk -F= '{print $2}'`
MQTTIP=`grep MQTTIP fr24mq.confg | awk -F= '{print $2}'`
MQTTPORT=`grep MQTTPORT fr24mq.confg | awk -F= '{print $2}'`
MQTTTOPIC=`grep MQTTTOPIC fr24mq.confg | awk -F= '{print $2}'`
CALLSIGNDESCRIPTION=`grep CALLSIGNDESCRIPTION fr24mq.confg | awk -F= '{print $2}'`

 #echo "$1"


inplane=$1 
# echo "$DUMP1090IP"
# echo "$DUMP1090PORT"
# echo "$MQTTIP"
# echo "$MQTTPORT"
# echo "$MQTTTOPIC"
# echo "$CALLSIGNDESCRIPTION"

descout="unknown aircraft"

for foo in `sed 's/ /-/g' /fr24/callSignDescription | awk -F@ '{print $1"@"$2}'  ` 
do 
 
 res=`echo $foo | sed 's/ /-/g'`
 call=`echo $foo | awk -F@ '{print $1}'`
 desc=`echo $foo | awk -F@ '{print $2}' | sed 's/-/ /g'`
#echo "$inplane    $call"
 #echo " $desc      $call"
 #echo "$inplane from file --> $call - $desc"
 
 if [[ "$inplane"  =~ .*"$call"*. ]]; then 
    descout="$desc"
 fi 

done

mydate=`date`
echo "$mydate -  $inplane    $descout"
mosquitto_pub -h 192.168.0.253  -t planes/watchfor -u me -P me -m "$inplane, $descout"





