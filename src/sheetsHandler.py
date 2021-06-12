from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
import time

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly','https://www.googleapis.com/auth/spreadsheets']
spreadsheet_id = '1sM0ErmEhI44Ni_za6VEocUtao-AQNMchWtcZmVvk1GE' 

"""Shows basic usage of the Drive v3 API.
Prints the names and ids of the first 10 files the user has access to.
"""
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('../token.pickle'):
    with open('../token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('../token.pickle', 'wb') as token:
        pickle.dump(creds, token)

sheets_service = build('sheets', 'v4', credentials=creds)
sheets_api = sheets_service.spreadsheets()

class SheetsHandler():
    def __init__(self):
        self.points_teams_ordered = get_name_column('Ranking and Points')
        self.distance_teams_ordered = get_name_column('Team Miles - 8pm')
        #self.distance_racers_ordered = get_name_column('Racer Miles - 8pm')

        self.points_headers_ordered = get_column_headers('Ranking and Points')
        self.distance_teams_headers_ordered = get_column_headers('Team Miles - 8pm')
        #self.distance_racers_headers_ordered = get_column_headers('Racer Miles - 8pm')

    def write_points_to_sheets(self, teamName, pointsStruct, totalPoints):
        points_column_to_value = {
            "Grudge Match (Projected)": pointsStruct.grudge,
            "We've Got Cows (Projected)": pointsStruct.cows,
            "Proclaimer Challenge (Actual)": pointsStruct.proclaimer,
            "Jack Bauer (Projected)": pointsStruct.jackBauer,
            "Total Points (Projected)": totalPoints
        }
        
        #Get Row Number
        row_number = self.points_teams_ordered.index(teamName) + 1

        column = 'A'
        for column_header in self.points_headers_ordered:
            try:
                value_to_write = points_column_to_value[column_header]
                write_cells("'Ranking and Points'!"+column+str(row_number), value_to_write)
            except:
                pass
            column = inc_letter(column)

    def write_team_distances_to_sheets(self, team_distances_dict, hour, day):
        print("Write team distances to google sheets")
        sheet_name = "Team Miles - " + hour

        ordered_distances = []
        for team in self.distance_teams_ordered:
            try:
                dist = team_distances_dict[team]
                ordered_distances.append([dist])
            except KeyError as e:
                print(e)

        #Get row numbers
        max_row = len(ordered_distances) + 1
        
        #Get column letter
        column_num = self.distance_teams_headers_ordered.index("Day " + str(day) + " Total") + 1
        column_letter = num_to_letter(column_num)

        write_cells(sheet_name + "!" + column_letter + "2:" + column_letter + str(max_row), ordered_distances)


    # def write_racer_distances_to_sheets(self, racer_distances_dict, hour, day):   
    #     print("Write racer distances to google sheets")
    #     sheet_name = "Racer Miles - " + hour

    #     ordered_distances = []
    #     for racer in self.distance_racers_ordered:
    #         try:
    #           dist = racer_distances_dict[racer]
    #           ordered_distances.append([dist])
    #           print(racer, dist)
    #         except KeyError as e:
    #             print(e)

    #     #Get row numbers
    #     max_row = len(ordered_distances) + 1
        
    #     #Get column letter
    #     column_num = self.distance_racers_headers_ordered.index("Day " + str(day) + " Total") + 1
    #     column_letter = num_to_letter(column_num)

    #     write_cells(sheet_name + "!" + column_letter + "2:" + column_letter + str(max_row), ordered_distances)


def get_name_column(sheetName):
    cellRange = "A1:A100"
    column = [val[0] for val in getRange(sheetName, cellRange)]
    return column

def get_column_headers(sheetName):
    cellRange = "A1:AZ1"
    headers = getRange(sheetName, cellRange)
    return headers[0]

def getRange(sheet, cells):
    time.sleep(.5)
    cellRange = "'" + sheet + "'!" + cells
    results =  sheets_api.values().get(spreadsheetId=spreadsheet_id, range=cellRange).execute()
    return results.get('values', [])

def write_cells(cells, value):
    time.sleep(.5)
    if isinstance(value, list):
        body = {'values': value}
    else:
        body = {'values': [[value]]}
    result = sheets_api.values().update(
        spreadsheetId=spreadsheet_id, range=cells, body=body, valueInputOption='RAW').execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

def inc_letter(letter):
    return chr(ord(letter) + 1)

def num_to_letter(num):
    return chr(64+num)