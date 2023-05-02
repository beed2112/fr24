cp  /home/beed2112/Downloads/ReleasableAircraft.zip . 
unzip -o ReleasableAircraft.zip 

echo "NNUMBER,OWNER,AIRCRAFTID" > master.txt
tail -n+2 MASTER.txt | awk -F, '{print $1 "," $7 "," substr(tolower($34),1,6)}' >> master.txt 

sqlite3 aircraftMon.db <<EOF
.mode csv
drop table MASTER;
.import "/home/beed2112/fr24/master.txt" MASTER
EOF
