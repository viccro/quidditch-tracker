import sqlite3
import pandas as pd
import paths

class DatabaseHandler():
    def __init__(self, debug_mode, local_db):
        # Creates or opens the file with a SQLite3 DB
        self.dbName = local_db
        print ("Connecting to database " + self.dbName)
        self.conn = sqlite3.connect(self.dbName, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.c = self.conn.cursor()
        self.c.execute('create table if not exists Teams (id integer primary key, teamName text, teamIcon text)')
        self.c.execute('create table if not exists Distances (id integer primary key, log_time timestamp, teamId integer, totalMiles integer)')

    def populate_team_table(self, teamList):
        print ("Filling Teams Table")
        for teamName in teamList.keys():
            if not self.has_value("Teams", "teamName", teamName):
                team = teamList[teamName]
                self.c.execute("INSERT INTO Teams (teamName, teamIcon) " +
                    " VALUES (\"" + team.name + "\", \"" + team.image_url + "\")")

    def close_db(self):
        print ("Closing database")
        self.conn.commit()
        self.conn.close()

    def add_distance(self, teamList, time):
        print ("Filling Distance Table")
        for teamName in teamList.keys():
            teamDistance = teamList[teamName].distance
            teamId = self.get_id_from_team_name(teamName)
            self.c.execute("INSERT INTO Distances (log_time, teamId, totalMiles) " +
                           " VALUES (?, ?, ?)", (time, teamId, teamDistance))#\"(?)\", \"" + teamId + "\", \"" + teamDistance + "\")")

    def has_value(self, table, column, value):
        query = 'SELECT 1 from {} WHERE {} = ? LIMIT 1'.format(table, column)
        return self.c.execute(query, (value,)).fetchone() is not None

    def get_id_from_team_name(self, name):
        self.c.execute("SELECT id from Teams where teamName = \"" + name + "\"")
        rows = self.c.fetchone()
        return rows[0]

    def get_team_name_from_id(self, id):
        self.c.execute("SELECT teamName from Teams where id = " + str(id) + "")
        rows = self.c.fetchone()
        return rows[0]

    def print_table_contents(self, tableName):
        self.c.execute("SELECT * FROM " + tableName)
        rows = self.c.fetchall()
        for row in rows:
            print(row)

    def get_distance_over_time_map(self):
        distances_by_team = dict()
        teams = set()
        #Get all team ids
        self.c.execute("SELECT id FROM Teams")
        rows = self.c.fetchall()
        for row in rows:
            teams.add(row[0])

        #for each id, get all distances sorted by datetime
        for teamId in teams:
            team_times = list()
            team_dists = list()
            self.c.execute("SELECT log_time as \'[timestamp]\', teamId, totalMiles FROM Distances WHERE teamId = " + str(teamId) + " ORDER BY log_time")
            distance_logs = self.c.fetchall()
            for log in distance_logs:
                time = log[0]
                team = self.get_team_name_from_id(log[1])
                dist = log[2]
                team_times.append(time)
                team_dists.append(dist)
            # feed into a dict of form {team1: ([time1, time2, ...], [dist1, dist2, ...]),
            #                           team2: ... }
            entry = pd.Series(team_dists, team_times)
            distances_by_team[team] = entry

        return distances_by_team