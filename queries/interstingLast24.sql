select   date(AIRCRAFTSIGHTINGS.AIRCRAFTSIGHTINGEPOCH, 'unixepoch', 'localtime') as Seendate, 
 AIRCRAFT.AIRCRAFTOWNER, AIRCRAFT.AIRCRAFTREGISTRATION, AIRCRAFT.AIRCRAFTTYPE, AIRCRAFTSIGHTINGS.AIRCRAFTSIGHTINGID from AIRCRAFTSIGHTINGS LEFT OUTER JOIN AIRCRAFT on
 AIRCRAFTSIGHTINGS.AIRCRAFTSIGHTINGID = AIRCRAFT.AIRCRAFTID where datetime(AIRCRAFTSIGHTINGS.AIRCRAFTSIGHTINGEPOCH, 'unixepoch', 'localtime') >= datetime('now' ,  'localtime', '-24 hours')  group by AIRCRAFT.AIRCRAFTID, Seendate order by AIRCRAFT.AIRCRAFTOWNER;
