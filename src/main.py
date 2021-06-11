#!/usr/bin/env python3

import scraper
import json
import databasehandler as dh
import plot_handler as ph
import datetime
import dropboxHandler as DB
import paths
from dotenv import load_dotenv

load_dotenv() # get environment variables from .env
debug_mode = False
now = datetime.datetime.now()
print ("====================")
print (now.strftime("%b %d, %I:%M %p"))

local_db = paths.local_directory + "local.db"

local_plot_daily_miles = paths.local_directory + "local_daily_miles.png"
local_plot_daily_mpp = paths.local_directory + "local_daily_mpp.png"
local_plot_total_miles = paths.local_directory + "local_total_miles.png"
local_plot_total_mpp = paths.local_directory + "local_total_mpp.png"
local_plot_avg_daily_miles = paths.local_directory + "local_avg_daily_miles.png"
local_plot_daily_ranking = paths.local_directory + "local_daily_ranking.png"
local_plot_overall_ranking = paths.local_directory + "local_overall_ranking.png"

local_plot_total_points = paths.local_directory + "local_total_points.png"

local_plot_zoom_grudge = paths.local_directory + "local_zoom_grudge.png"
local_plot_full_grudge = paths.local_directory + "local_full_grudge.png"

local_plot_cows = paths.local_directory + "local_cows.png"

local_plot_proclaimer_steps = paths.local_directory + "local_proclaimer_steps.png"
local_chart_dist_to_proclaimer_pt = paths.local_directory + "local_chart_dist_to_proclaimer_pt.html"

local_plot_jack_bauer = paths.local_directory + "local_jack.png"

local_chart_team_stats = paths.local_directory + "local_chart_team.png"
local_chart_indv_stats = paths.local_directory + "local_chart_indv.png"

#Collect all data
print("Debug on? " + str(debug_mode))
teamList = scraper.extractTeamList(debug_mode)
racerList = scraper.extractRacerList(debug_mode)

if debug_mode: print (json.dumps(teamList, indent=1))
if debug_mode: print (json.dumps(racerList, indent=1))

#Write to database
DH = dh.DatabaseHandler(debug_mode, local_db)

#Write to local db
DH.populate_team_table(teamList)
DH.add_team_distance(teamList, now)

DH.populate_racer_table(racerList)
DH.add_racer_distance(racerList, now)

DH.update_team_points(teamList)

#Push db to dropbox
if not debug_mode: 
    DB.write(local_db, paths.dropbox_directory + "scrape.db")   

if debug_mode:
    DH.print_table_contents("Teams")

#Generate plots

print("Total mileage plots")
data_by_team_all = DH.get_distance_over_time_map()
if debug_mode:
   print (data_by_team_all)


print("Grudge match plots")
data_by_team_BmcBA = DH.get_distance_over_time_map(['Badger McBadass','The Dementors','SnekyMcSnekface'])


ph.plot_distance_over_time(data_by_team_BmcBA, debug_mode)

DH.close_db()

if not debug_mode:
    #Push plot to dropbox
    DB.write(local_plot, paths.dropbox_directory + "plot.png")

#ph.bin_by_hour(data_by_team) #TODO
