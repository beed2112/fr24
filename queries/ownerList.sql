Owners 
select DISTINCT AIRCRAFT.AIRCRAFTOWNER from AIRCRAFT order by AIRCRAFT.AIRCRAFTOWNER;


Count Interesting
select  COUNT(DISTINCT AIRCRAFT.AIRCRAFTOWNER) from AIRCRAFT order by AIRCRAFT.AIRCRAFTOWNER;


select  COUNT(AIRCRAFTNOTINTERESTING.AIRCRAFTOWNER) from AIRCRAFTNOTINTERESTING order by AIRCRAFTNOTINTERESTING.AIRCRAFTOWNER;

Count UNique Owners in Not INteresting 
select  COUNT(distinct AIRCRAFTNOTINTERESTING.AIRCRAFTOWNER) from AIRCRAFTNOTINTERESTING order by AIRCRAFTNOTINTERESTING.AIRCRAFTOWNER;



Aircraft Types

select DISTINCT AIRCRAFT.AIRCRAFTTYPE from AIRCRAFT order by AIRCRAFT.AIRCRAFTTYPE;


Private Owners to research

select DISTINCT AIRCRAFT.AIRCRAFTOWNER, AIRCRAFT.AIRCRAFTTYPE, AIRCRAFT.AIRCRAFTREGISTRATION, AIRCRAFT.AIRCRAFTID  from AIRCRAFT  where AIRCRAFT.AIRCRAFTOWNER like "Priv%" order by AIRCRAFT.AIRCRAFTTYPE;
                                      
                                      
Private|AT-6A Texan|N4802E|a5eb3c "Some Dude's old cool plane" 
Private|AT-6C Texan|N3158W|a35ce9 "Some Dude's from Mesa old cool plane" 
Private|M-62A-3 PT-26|N9165H|acb004 "GROUNDED NO MORE VETERAN FLIGHT LIFT LLC"
Private|R22 Beta II|N38GM|a45993
Private|R22 Beta II|N3086T|a34046
Private|R22 Beta II|N7098P|a9797b
Private|S.211|N211BJ|a1bd5b
Private|Stearman A75N1 PT-17 Kaydet|N450MD|a57333 "FULL BRITCHES AIR SHOWS bi plane"
Private|Stearman A75N1 PT-17 Kaydet|N68800|a92360 "Some Dude's old cool bi plane"
Private|Stearman A75N1 PT-17 Kaydet|N680PT|a9048e "WARBIRDS LLC bi plane"
Private|Stearman E75N1 PT-13D Kaydet|N1315N|a081fc "Some Dude's old cool bi plane"
Private|T-6G Texan|N153NA|a0d681 "Some Dude's old cool plane" 
Private|T-6G Texan|N260CF|a27f35 "Some Dude's old cool plane" 
                                      
                                      
