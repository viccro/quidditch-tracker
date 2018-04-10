#!/usr/bin/env python3

import scraper
import json
import databasehandler as dh
import plot_handler as ph
import datetime
import dropboxHandler as DB
import paths

debug_mode = False
now = datetime.datetime.now()
print ("====================")
print (now.strftime("%b %d, %I:%M %p"))

local_db = paths.local_directory + "local.db"
local_plot = paths.local_directory + "local.png"

#Collect all data
print("Debug on? " + str(debug_mode))
teamList = scraper.extractTeamList(debug_mode)
if debug_mode: print (json.dumps(teamList, indent=1))

#Write to database
DH = dh.DatabaseHandler(debug_mode, local_db)

if not debug_mode:
    #Write to local db
    DH.populate_team_table(teamList)
    DH.add_distance(teamList, now)

    #Push db to dropbox
    #DB.write(local_db, "/S18/scrape.db")

if debug_mode:
    DH.print_table_contents("Teams")
    DH.print_table_contents("Distances")

#Generate plots

#print("grab all")
#data_by_team_all = DH.get_distance_over_time_map()
#if debug_mode:
#    print (data_by_team_all)

print("grab relevant plots")
data_by_team_BmcBA = DH.get_distance_over_time_map(['Badger McBadass','The Dementors','SnekyMcSnekface'])
DH.close_db()

ph.plot_distance_over_time(data_by_team_BmcBA, debug_mode)

if not debug_mode:
    #Push plot to dropbox
    DB.write(local_plot, "/S18/plot.png")

#ph.bin_by_hour(data_by_team) #TODO
