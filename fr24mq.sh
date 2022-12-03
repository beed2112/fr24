#desc=`grep -i $1 ./callSignDescription | awk -F @ '{print $2}'`

DUMP1090IP=`grep DUMP1090IP fr24mq.confg | awk -F= '{print $2}'`
DUMP1090PORT=`grep DUMP1090PORT fr24mq.confg | awk -F= '{print $2}'`
MQTTIP=`grep MQTTIP fr24mq.confg | awk -F= '{print $2}'`
MQTTPORT=`grep MQTTPORT fr24mq.confg | awk -F= '{print $2}'`
MQTTTOPIC=`grep MQTTTOPIC fr24mq.confg | awk -F= '{print $2}'`
CALLSIGNDESCRIPTION=`grep CALLSIGNDESCRIPTION fr24mq.confg | awk -F= '{print $2}'`

 echo "$1"


inplane=$1 
echo "$DUMP1090IP"
echo "$DUMP1090PORT"
echo "$MQTTIP"
echo "$MQTTPORT"
echo "$MQTTTOPIC"
echo "$CALLSIGNDESCRIPTION"

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


echo "output $inplane    $descout"
#mosquitto_pub -h 192.168.0.253  -t planes/watchfor -u me -P me -m "$inplane, $descout"


# case $1 inS

#   *"N507MP"*)
#     desc="a Mesa Police Helicoptor"
#     ;;

#   *"N505MP"*)
#     desc="a Mesa Police Helicoptor"
#     ;;

#   *"COPPER"*)
#     desc="an Air Force Tanker"
#     ;;

#   *"MADCAT"*)
#     desc="an Air Force Training Jet"
#     ;;

#   *"N12718"*)
#     desc="an Old Silver prop plane"
#     ;;

#    *"S211"*)
#     desc="an Italian Fighter"
#     ;;

#   *"N16BP"*)
#     desc="a Bi plane"
#     ;;

#   *"MADCAT"*)
#     desc="an Air Force Training Jet"
#     ;;

#   *"KYOTE"*)
#     desc="an Army Black Hawk"
#     ;;

#   *"RAIDR"*)
#     desc="a Navy Tanker"
#     ;;

#   *"ZAPER"*)
#     desc="an Air Force Tanker"
#     ;;

#   *"TRON"*)
#     desc="an Air Force Tanker"
#     ;;

#   *"N55IAM"*)
#     desc="an Air Force Tanker"
#     ;;

#   "F16"*)
#     desc="an Air Force F sixteen"
#     ;;

#   *"TNKR"*)
#     desc="a Fire fighting tanker"
#     ;;

#   *"SNTRY"*)
#     desc="a Boeing Sentry RADAR"
#     ;;

#   "OXF"*)
#     desc="a Flight School plane"
#     ;;


#   "HGT"*)
#     desc="an Intel Air Shuttle"
#     ;;

#   "DOJ"*)
#     desc="a US Marshall, Con Air flight "
#     ;;
#     *)
#     desc="an unknown aircraft"
#     ;;
# esac




