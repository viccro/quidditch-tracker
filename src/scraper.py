import requests
from bs4 import BeautifulSoup as bs
import requestsAdapter
import sys
import structs
import paths

total_miles_in_race = 3625.8
baseUrl = paths.baseUrl

teamsFile = "/Users/206790/Documents/OtherStuff/racery-scrape/quidditch-tracker/webpages/current-quidditch.html"

def extractTeamList(debug_mode_on):
    if not debug_mode_on:
        print ("Requesting ingredients")
        data = get_live_data(baseUrl + "#teams")
    else:
        print ("Setting out ingredients")
        data = get_static_data(teamsFile)

    print ("Formulating soup")
    soup = bs(data, "html.parser")

    for section in soup.find_all('section'):
        if section.get("data-panel-hash") == "teams":
            teams = section
            break

    teamList = dict()

    for team in teams.find_all('li'):
        if team.span != None:
            teamName = str(team.span.string)

        tD = team.find_all('span', class_='distance')
        if len(tD) > 0:
            teamDistance = tD[0].get_text().split()[0]
            if teamDistance == 'Finished':
                teamDistance = total_miles_in_race
            teamDistance = float(teamDistance)
                #    tI = team.find_all('div', class_='icon')
    #    if len(tI) > 0:
    #        teamImage = tI[0]
    #        print(teamImage)

        teamList[teamName] = structs.Team(teamName, teamDistance, "")

    return teamList

def get_live_data(url_location):
    session = requests.Session()
    session.mount('https://', requestsAdapter.SSLAdapter())
    response = session.get(url_location)

    if response.status_code != requests.codes.ok:
        sys.exit(response.status_code)
    return response.text

def get_static_data(file_location):
    with open(file_location, "r") as myfile:
        return myfile.read()
