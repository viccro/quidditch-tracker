import sqlite3
import pandas as pd
import paths
import sheetsHandler as sh
import datetime as dt
import calculator as Calc


class DatabaseHandler():
    def __init__(self, debug_mode, local_db):
        # Creates or opens the file with a SQLite3 DB
        self.dbName = local_db
        print ("Connecting to database " + self.dbName)
        self.conn = sqlite3.connect(self.dbName, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.c = self.conn.cursor()
        self.c.execute('create table if not exists Teams (id integer primary key, teamName text, teamIcon text, grudgePoints int, cowsPoints int, proclaimerPoints int, jackBauerPoints int, totalPoints int)')
        self.c.execute('create table if not exists TeamDistances (id integer primary key, log_time timestamp, teamId integer, totalMiles integer)')

        #self.c.execute('create table if not exists Racers (id integer primary key, racerName text, racerIcon text, mileGoal float, mileStretchGoal float)')
        #self.c.execute('create table if not exists RacerDistances (id integer primary key, log_time timestamp, racerId integer, totalMiles integer)')

        self.SH = sh.SheetsHandler()

    def populate_team_table(self, teamList):
        print ("Filling Teams Table")
        for teamName in teamList.keys():
            if not self.has_value("Teams", "teamName", teamName):
                team = teamList[teamName]
                self.c.execute("INSERT INTO Teams (teamName, teamIcon) " +
                    " VALUES (\"" + team.name + "\", \"" + team.image_url + "\")")
        self.conn.commit()

    def populate_racer_table(self, racerList):
        print ("Filling Racers Table")
        for racerName in racerList.keys():
            if not self.has_value("Racers", "racerName", racerName):
                racer = racerList[racerName]
                self.c.execute("INSERT INTO Racers (racerName, racerIcon) " +
                    " VALUES (\"" + racer.name + "\", \"" + racer.image_url + "\")")
        self.conn.commit()

    def close_db(self):
        print ("Closing database")
        self.conn.commit()
        self.conn.close()

    def add_team_distance(self, teamList, time):
        print ("Filling Team Distance Table")
        for teamName in teamList.keys():
            teamDistance = teamList[teamName].distance
            teamId = self.get_id_from_team_name(teamName)
            self.c.execute("INSERT INTO TeamDistances (log_time, teamId, totalMiles) " +
                           " VALUES (?, ?, ?)", (time, teamId, teamDistance))#\"(?)\", \"" + teamId + "\", \"" + teamDistance + "\")")
        self.conn.commit()

    def add_racer_distance(self, racerList, time):
        print ("Filling Racer Distance Table")
        for racerName in racerList.keys():
            racerDistance = racerList[racerName].distance
            racerId = self.get_id_from_racer_name(racerName)
            self.c.execute("INSERT INTO RacerDistances (log_time, racerId, totalMiles) " +
                           " VALUES (?, ?, ?)", (time, racerId, racerDistance))#\"(?)\", \"" + racerId + "\", \"" + racerDistance + "\")")
        self.conn.commit()

    def update_team_points(self, teamList):
        print ("Calculating Points and Updating Table")
        from calculator import currentPoints

        for teamName in teamList.keys():
            teamId = self.get_id_from_team_name(teamName)
            points = currentPoints(self.c, teamName)
            totalPoints = points.grudge + points.cows + points.proclaimer + points.jackBauer
            #Write to db
            self.c.execute("UPDATE Teams SET grudgePoints = '" + str(points.grudge) + "', cowsPoints = '" + str(points.cows) +
                "', proclaimerPoints = '" +  str(points.proclaimer) + "', jackBauerPoints = '" + str(points.jackBauer) + 
                "', totalPoints = '" + str(totalPoints) + "' WHERE id = " + str(teamId) + ";")
            
            #Write to sheets
            self.SH.write_points_to_sheets(teamName, points, totalPoints)
        self.conn.commit()

    def has_value(self, table, column, value):
        query = 'SELECT 1 from {} WHERE {} = ? LIMIT 1'.format(table, column)
        return self.c.execute(query, (value,)).fetchone() is not None

    def get_id_from_team_name(self, name):
        self.c.execute("SELECT id from Teams where teamName = \"" + name + "\"")
        rows = self.c.fetchone()
        return rows[0]

    def get_id_from_racer_name(self, name):
        self.c.execute("SELECT id from Racers where racerName = \"" + name + "\"")
        rows = self.c.fetchone()
        return rows[0]

    def get_team_name_from_id(self, id):
        self.c.execute("SELECT teamName from Teams where id = " + str(id) + "")
        rows = self.c.fetchone()
        return rows[0]

    def get_racer_name_from_id(self, id):
        self.c.execute("SELECT racerName from Racers where id = " + str(id) + "")
        rows = self.c.fetchone()
        return rows[0]

    def print_table_contents(self, tableName):
        self.c.execute("SELECT * FROM " + tableName)
        rows = self.c.fetchall()
        for row in rows:
            print(row)

    def get_team_distance_over_time_map(self, teamsToDraw=[], time_offset=None, time_of_offset=None):
        distances_by_team = dict()
        teams = set()

        #Get all team ids
        self.c.execute("SELECT id FROM Teams")
        rows = self.c.fetchall()
        for row in rows:
            teams.add(row[0])

        #for each id, get all distances sorted by datetime
        for teamId in teams:
            team = self.get_team_name_from_id(teamId)
            if (teamsToDraw == []) or (team in teamsToDraw):
                print("Adding team " + team + " to plot")
                team_times = list()
                team_dists = list()
                self.c.execute("SELECT log_time as \'[timestamp]\', teamId, totalMiles FROM teamDistances WHERE teamId = " + str(teamId) + " ORDER BY log_time")
                distance_logs = self.c.fetchall()
                if time_of_offset:
                    dist_at_offset = Calc.get_miles_at_time_by_teamId(self.c, teamId, time_of_offset + time_offset)
                else:
                    dist_at_offset = 0
                for log in distance_logs:
                    time = log[0] - time_offset
                    dist = log[2] - dist_at_offset
                    if dist >= 0:
                        team_times.append(time)
                        team_dists.append(dist)
                entry = pd.Series(team_dists, team_times)
                distances_by_team[team] = entry

        return distances_by_team

    def write_distances_to_sheets(self, hour, day):
        team_distances = self.get_team_distances()
        self.SH.write_team_distances_to_sheets(team_distances, hour, day)

        # racer_distances = self.get_racer_distances()
        # self.SH.write_racer_distances_to_sheets(racer_distances, hour, day)

    # Get most up to date total distances from teams
    def get_team_distances(self):
        distances_by_team = dict()
        teams = set()

        #Get all team ids
        self.c.execute("SELECT id, teamName FROM Teams")
        rows = self.c.fetchall()
        for row in rows:
            teams.add((row[0], row[1]))

        #for each id, get all distances sorted by datetime
        for teamId, teamName in teams:
            self.c.execute("SELECT log_time as \'[timestamp]\', totalMiles FROM TeamDistances WHERE teamId = " + str(teamId) + " ORDER BY log_time DESC")
            distance_log = self.c.fetchone()
            distances_by_team[teamName] = distance_log[1]

        return distances_by_team

    def get_racer_distances(self):
        distances_by_racer = dict()
        racers = set()

        #Get all team ids
        self.c.execute("SELECT id, racerName FROM Racers")
        rows = self.c.fetchall()
        for row in rows:
            racers.add((row[0], row[1]))

        #for each id, get all distances sorted by datetime
        for racerId, racerName in racers:
            self.c.execute("SELECT log_time as \'[timestamp]\', totalMiles FROM RacerDistances WHERE racerId = " + str(racerId) + " ORDER BY log_time DESC")
            distance_log = self.c.fetchone()
            distances_by_racer[racerName] = distance_log[1]

        return distances_by_racer