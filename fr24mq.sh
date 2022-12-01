desc=`grep -i $1 callSignDescription | awk -F @ '{print $2}'`

if [$desc == ""]
 then
    desc="unknown aircraft"
fi
    
mosquitto_pub -h 192.168.0.253  -t planes/watchfor -u me -P me -m "$1, $desc"

