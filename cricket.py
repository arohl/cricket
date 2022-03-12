#!/usr/bin/env -P/Users/andrew/.asdf/shims/python3:/opt/local/bin/:/Users/andrew/opt/anaconda3/bin:/Users/andrew/anaconda3/bin:/Users/180341c/opt/anaconda3/bin/    python3

# <bitbar.title>Current cricket score</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>Andrew Rohl</bitbar.author>
# <bitbar.author.github>arohl</bitbar.author.github>
# <bitbar.desc>Provides current score from cricinfo</bitbar.desc>
# <bitbar.dependencies>python3 requests</bitbar.dependencies>

import requests
import datetime
from dateutil.parser import parse
import errno
import json
import os

config_file = "cricket.config"

def convert_date(date):
    return (parse(date).astimezone())

def days_hours_minutes(td):
    return td.days, td.seconds//3600, (td.seconds//60)%60

def prepare_for_emojize(s):
    return s.replace(" ", "_").lower()

class Innings:
    def __init__(self, team, runs, wickets):
        self.team = team
        self.runs = runs
        self.wickets = wickets

    def __str__(self):
        if self.wickets < 10:
            return f'{self.team} {self.runs}/{self.wickets}'
        else:
            return f'{self.team} {self.runs}'

    def emojize_score(self):
        _team = prepare_for_emojize(self.team)
        if self.wickets < 10:
            return f':{_team}: {self.runs}/{self.wickets} | symbolize=false'
        else:
            return f':{_team}: {self.team} {self.runs} | symbolize=false'


# open config file and simply exit with success if doesn't exist as means no games on
try:
    config_with_path = f"{os.environ['SWIFTBAR_PLUGINS_PATH']}/{config_file}"
    f = open(config_with_path)
except OSError as err:
    if err.errno == errno.ENOENT:
        exit()

# read config as json and check if the date is in the future and if so display time
# until match starts

config = json.load(f)

start_time = convert_date(config['startTime'])
wait_for_start = start_time - datetime.datetime.now().astimezone()
if wait_for_start.total_seconds() > 0:
    days, hours, mins = days_hours_minutes(waitForStart)
    _home_team = prepare_for_emojize(config['homeTeam'])
    _away_team = prepare_for_emojize(config['awayTeam'])
    if days > 0:
        print(f":{_home_team}: v :{_away_team}: {days}:{hours:02}:{mins:02} | symbolize=false")
    else:
        print(f":{_home_team}: v :{_away_team}: {hours}:{mins:02} | symbolize=false")
    print("---")
    date_time = startTime.strftime("%a %b %d at %-I:%M %p")
    print(f"{config['homeTeam']} vs {config['awayTeam']} starts on {date_time} | color = royalblue")
    exit()

# match is live (or finished - need to decide what to do (if anything) with finished matches)
match_url = f"https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?lang=en&seriesId={config['seriesId']}&matchId={config['matchId']}&latest=true"

page = requests.get(match_url)
match_json = page.json()
n_innings = len(match_json['scorecard']['innings'])

innings = []
for i in range(n_innings):
    innings.append(Innings(match_json['scorecard']['innings'][i]['team']['name'], match_json['scorecard']['innings'][i]['runs'], match_json['scorecard']['innings'][i]['wickets']))

print(innings[-1].emojize_score())
print("---")
print(f"{match_json['match']['series']['alternateName']}: {match_json['match']['title']}, {match_json['match']['ground']['smallName']} | color = royalblue")
print(f"{match_json['match']['statusText']} | color = black")
for batter in match_json['scorecard']['innings'][n_innings-1]['inningBatsmen']:
    if (not batter['battedType'] == 'DNB'):
        if (not batter['isOut']):
            print(f"{batter['player']['name']} {batter['runs']}({batter['balls']}) | color = black")
print("---")
for score in innings:
    print(f"{score} | color = black")
