#desc=`grep -i $1 ./callSignDescription | awk -F @ '{print $2}'`

if [$desc == ""]
 then
    desc="unknown aircraft"
fi

STR='GNU/Linux is an operating system'
SUB='Linux'
 echo $1
case $1 in

  *"N507MP"*)
    desc="a Mesa Police Helicoptor"
    ;;

  *"N505MP"*)
    desc="a Mesa Police Helicoptor"
    ;;

  *"COPPER"*)
    desc="an Air Force Tanker"
    ;;

  *"MADCAT"*)
    desc="an Air Force Training Jet"
    ;;

  *"N12718"*)
    desc="an Old Silver prop plane"
    ;;

   *"S211"*)
    desc="an Italian Fighter"
    ;;

  *"N16BP"*)
    desc="a Bi plane"
    ;;

  *"MADCAT"*)
    desc="an Air Force Training Jet"
    ;;

  *"KYOTE"*)
    desc="an Army Black Hawk"
    ;;

  *"RAIDR"*)
    desc="a Navy Tanker"
    ;;

  *"ZAPER"*)
    desc="an Air Force Tanker"
    ;;

  *"TRON"*)
    desc="an Air Force Tanker"
    ;;

  *"N55IAM"*)
    desc="an Air Force Tanker"
    ;;

  "F16"*)
    desc="an Air Force F sixteen"
    ;;

  *"TNKR"*)
    desc="a Fire fighting tanker"
    ;;

  *"SNTRY"*)
    desc="a Boeing Sentry RADAR"
    ;;

  "OXF"*)
    desc="a Flight School plane"
    ;;


  "HGT"*)
    desc="an Intel Air Shuttle"
    ;;

  "DOJ"*)
    desc="a US Marshall, Con Air flight "
    ;;
    *)
    desc="an unknown aircraft"
    ;;
esac


mosquitto_pub -h 192.168.0.253  -t planes/watchfor -u me -P me -m "$1, $desc"


