import requests
from bs4 import BeautifulSoup as bs
import requestsAdapter
import sys
import structs
import paths

total_miles_in_race = 1600
baseUrl = paths.baseUrl

teamsFile = "../quidditch-tracker/webpages/s21-botf-finals-teams.html"

def extractTeamList(debug_mode_on):
    if not debug_mode_on:
        print ("Requesting ingredients [team]")
        data = get_live_data(baseUrl + "#teams")
    else:
        print ("Setting out ingredients [team]")
        data = get_static_data(teamsFile)

    print ("Formulating team soup")
    soup = bs(data, "html.parser")

    for section in soup.find_all("section"):
        if section.get("data-panel-hash") == "teams":
            team_section = section

    teams = extract_members(team_section)
    teamList = dict()

    for team in teams:
        if team.span != None:
            teamName = str(team.find('span',{"class":"name"}).find('a').find('span').string)
            teamDistanceVerbose = team.find('span',{"class":"distance"}).string
            teamDistance = teamDistanceVerbose.split()[0]
            teamLogoUrl = team.find('div',{"class":"icon"}).find('img').get("src")
            teamPlaceNumberVerbose = team.find('div',{"class":"place_number"}).string
            teamPlaceNumber = teamPlaceNumberVerbose.replace('.','')

        if teamDistance == 'Finished':
            teamDistance = total_miles_in_race
        teamDistance = float(teamDistance)

        teamList[teamName] = structs.Team(teamName, teamDistance, teamLogoUrl, teamPlaceNumber)

    return teamList

def extractRacerList(debug_mode_on):
    if not debug_mode_on:
        print ("Requesting ingredients [racer]")
        data = get_live_data(baseUrl + "#teams-t@muppets_48370")
    else:
        print ("Setting out ingredients [racer]")
        data = get_static_data(teamsFile)

    print ("Formulating racer soup")
    soup = bs(data, "html.parser")

    for section in soup.find_all("section"):
        if section.get("data-panel-hash") == "racers":
            racer_section = section

    racers = extract_members(racer_section)
    racerList = dict()

    for racer in racers:
        if racer.span != None:
            racerName = str(racer.find('span',{"class":"name"}).string)
            racerDistanceVerbose = racer.find('span',{"class":"distance"}).string
            racerDistance = racerDistanceVerbose.split()[0]
            racerLogoUrl = racer.find('div',{"class":"icon"}).find('img').get("src")
            racerPlaceNumberVerbose = racer.find('div',{"class":"place_number"}).string
            racerPlaceNumber = racerPlaceNumberVerbose.replace('.','')

        if racerDistance == 'Finished':
            racerDistance = total_miles_in_race
        racerDistance = float(racerDistance)

        racerList[racerName] = structs.Racer(racerName, racerDistance, racerLogoUrl, racerPlaceNumber)
    return racerList    

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

def extract_members(section):
    return section.find_all('li')