#!/usr/bin/env python3

import scraper
import json
import databasehandler as dh
import plot_handler as ph
import datetime

debug_mode = False
now = datetime.datetime.now()
print ("====================")
print (now.strftime("%b %d, %I:%M %p"))

#Collect all data
print("Debug on? " + str(debug_mode))
teamList = scraper.extractTeamList(debug_mode)
if debug_mode: print (json.dumps(teamList, indent=1))

#Write to database
DH = dh.DatabaseHandler(debug_mode)

if not debug_mode:
    DH.populate_team_table(teamList)
    DH.add_distance(teamList, now)

if debug_mode:
    DH.print_table_contents("Teams")
    DH.print_table_contents("Distances")

#Generate plots
data_by_team = DH.get_distance_over_time_map()
DH.close_db()

if debug_mode: print (data_by_team)

ph.plot_distance_over_time(data_by_team, debug_mode)
#ph.bin_by_hour(data_by_team)
