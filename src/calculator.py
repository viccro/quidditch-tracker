import sqlite3
import structs
import math

# Austen City Limits: Stride & Prejudice vs. Here Comes the Run vs. Mouse Rat
# The French Connection: Electric Mayhem vs. One Race More vs. Moose & Squirrel
# The Poseidon Adventure: Nigh Uncatchable vs. That Dam Team vs. OUTABREATH
# Fresh Baked Petunias: Swan Song vs. Showstopper vs. Not Again

grudgeMatches = {
    'Showstopper': 'Fresh Baked Petunias',
    'One Race More': 'The French Connection',
    'Swan Song': 'Fresh Baked Petunias',
    'That Dam Team': 'The Poseidon Adventure',
    'HereComesTheRun': 'Austen City Limits',
    'Electric Mayhem': 'The French Connection',
    'Moose&Squirrel': 'The French Connection',
    'NighUncatchable': 'The Poseidon Adventure',
    'Mouse Rat': 'Austen City Limits',
    'OUTABREATH': 'The Poseidon Adventure',
    'Not Again': 'Fresh Baked Petunias',
    'Stride&Prjudice': 'Austen City Limits'
    }

matchTeams = {
    'The Poseidon Adventure': ['That Dam Team', 'NighUncatchable', 'OUTABREATH'],
    'Fresh Baked Petunias': ['Swan Song', 'Showstopper', 'Not Again'],
    'The French Connection': ['Electric Mayhem', 'One Race More', 'Moose&Squirrel'],
    'Austen City Limits': ['Stride&Prjudice', 'HereComesTheRun', 'Mouse Rat']
}

def currentPoints(cursor, teamName):
    grudge = grudgePoints(cursor, teamName)
    cows = cowsPoints(cursor, teamName)
    proclaimer = proclaimerPoints(cursor, teamName)
    jb = jackBauerPoints(cursor, teamName)
    return structs.Points(grudge, cows, proclaimer, jb)


def grudgePoints(cursor, teamName):
    print("Calculating Grudge")
    match_name = grudgeMatches[teamName]
    teams_in_match = matchTeams[match_name]

    teamDistances = []

    for team in teams_in_match:
        distance = get_distance_by_team_name(cursor, team)
        teamDistances.append((team, distance))
        time_crossing_finish = get_earliest_crossing(cursor, teamName, 1600)

    #figure out cap of 1600 timing

    teams_sorted_by_distance = tuple_sort(teamDistances)
    points = 1
    for name, distance in teams_sorted_by_distance:
        if name == teamName:
            return points
        else:
            points += 1

    return points


def cowsPoints(cursor, teamName):
    print("Calculating Cows")
    #Get team list
    teams = []
    cursor.execute("SELECT teamName, id FROM Teams")
    rows = cursor.fetchall()
    for row in rows:
        teams.append((row[0],row[1]))

    #Get total miles from latest datetime for ALL teams
    teamDistances = []
    for name, id in teams:
        cursor.execute("SELECT log_time as \'[timestamp]\', teamId, totalMiles FROM teamDistances WHERE teamId = " + str(id) + " ORDER BY log_time DESC")
        distance_log = cursor.fetchone()
        total_dist = distance_log[2]
        teamDistances.append((name, total_dist))

    teams_sorted_by_distance = tuple_sort(teamDistances)
    points = 1
    for name, distance in teams_sorted_by_distance:
        if name == teamName:
            return points
        else:
            points += 1
    return 0


def proclaimerPoints(cursor, teamName):
    print("Calculating Proclaimer")
    totalDist = get_distance_by_team_name(cursor, teamName)
    points = math.floor(totalDist / 1000)
    return points


def jackBauerPoints(cursor, teamName):
    print("Calculating Jack")
    return 0

def tuple_sort(list_of_tuples):
   return(sorted(list_of_tuples, key = lambda x: x[1]))

def get_distance_by_team_name(cursor, teamName):
    #Get teamId
    cursor.execute("SELECT id FROM Teams WHERE teamName = \"" + teamName + "\"")
    id, = cursor.fetchone()
    
    #Get total miles from latest datetime
    cursor.execute("SELECT log_time as \'[timestamp]\', teamId, totalMiles FROM teamDistances WHERE teamId = " + str(id) + " ORDER BY log_time DESC")
    distance_log = cursor.fetchone()
    totalDist = distance_log[2]
    return totalDist

def get_earliest_crossing(cursor, teamName, mile):
    #Get teamId
    cursor.execute("SELECT id FROM Teams WHERE teamName = \"" + teamName + "\"")
    id, = cursor.fetchone()

    cursor.execute("SELECT log_time as \'[timestamp]\', teamId, totalMiles FROM teamDistances WHERE teamId = " + str(id) + " AND totalMiles > " + str(mile) + " ORDER BY log_time LIMIT 1")
    distance_log = cursor.fetchone()
    time_of_crossing = distance_log[0] if distance_log else None
    return time_of_crossing