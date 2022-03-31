#!/usr/bin/env -P/Users/andrew/.asdf/shims/:/opt/local/bin/:/Users/andrew/opt/anaconda3/bin:/Users/andrew/anaconda3/bin:/Users/180341c/opt/anaconda3/bin/    python3

# <bitbar.title>Current cricket score</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>Andrew Rohl</bitbar.author>
# <bitbar.author.github>arohl</bitbar.author.github>
# <bitbar.desc>Provides current score from cricinfo</bitbar.desc>
# <bitbar.dependencies>python3 requests prettytable</bitbar.dependencies>

import requests
import datetime
from dateutil.parser import parse
import errno
from json import load
from os import environ
from urllib.request import pathname2url
from prettytable import PrettyTable

config_file_name = ".cricket.config"
innings_file_prefix = "innings"
html_table_header = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <style>
    table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        width: 650px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
    }
    table thead tr {
        background-color: #3a7ef7;
        color: #ffffff;
        text-align: left;
    }
    table th,
    table td {
        padding: 12px 15px;
    }
    table tbody tr {
        border-bottom: 1px solid #dddddd;
    }

    table tbody tr:nth-of-type(even) {
        background-color: #f3f3f3;
    }

    table tbody tr:last-of-type {
        border-bottom: 2px solid #3a7ef7;
    }
    </style>
    <title>title</title>
  </head>
  <body>
"""
html_table_footer = """</body>
</html>"""

def convert_date(date):
    return (parse(date).astimezone())

def days_hours_minutes(td):
    return td.days, td.seconds//3600, (td.seconds//60)%60

def prepare_for_emojize(s):
    return s.replace(" ", "_").lower()

def replace_none(field):
    if field == None:
        return ''
    else:
        return field

class BattingScore:
    def __init__(self, name, dismissal, runs, balls, sixes, fours, strike_rate, type, is_out):
        self.name = name
        self.dismissal = dismissal
        self.runs = runs
        self.balls = balls
        self.sixes = sixes
        self.fours = fours
        self.strike_rate = strike_rate
        self.type = type
        self.is_out = is_out

        def __str__(self):
            return f'{self.name}'

class BowlingScore:
    def __init__(self, name, overs, runs, wickets, economy):
        self.name = name
        self.overs = overs
        self.runs = runs
        self.wickets = wickets
        self.economy = economy

    def __str__(self):
        return f'{self.name}'

class Innings:
    def __init__(self, team, runs, wickets):
        self.team = team
        self.runs = runs
        self.wickets = wickets
        self.batting_scorecard = []
        self.bowling_scorecard = []
        self.n_bowlers = 0

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

    def print_batting(self, out_file):
        scorecard = PrettyTable()
        scorecard.field_names = (['batter', 'dismissal', 'runs', 'balls', '6s', '4s', 'S/R'])
        scorecard.align = 'r'
        scorecard.align['batter'] = 'l'
        for batter in self.batting_scorecard:
            scorecard.add_row([batter.name, batter.dismissal, batter.runs, batter.balls, batter.sixes, batter.fours, batter.strike_rate])
        scorecard.format = False
        html = scorecard.get_html_string()
        print(html, file = out_file)

    def print_bowling(self, out_file):
        bowling = PrettyTable()
        bowling.field_names = (['bowler', 'overs', 'runs', 'wickets', 'economy'])
        bowling.align = 'r'
        bowling.align['bowler'] = 'l'
        for bowler in self.bowling_scorecard:
            bowling.add_row([bowler.name, bowler.overs, bowler.runs, bowler.wickets, bowler.economy])
        bowling.format = False
        html = bowling.get_html_string()
        print(html, file = out_file)


# open config file and simply exit with success if doesn't exist as means no games on
try:
    config_with_path = f"{environ['SWIFTBAR_PLUGINS_PATH']}/{config_file_name}"
    config_file = open(config_with_path, "r")
except OSError as err:
    if err.errno == errno.ENOENT:
        exit()

# read config as json and check if the date is in the future and if so display time
# until match starts

config = load(config_file)

start_time = convert_date(config['startTime'])
wait_for_start = start_time - datetime.datetime.now().astimezone()
if wait_for_start.total_seconds() > 0:
    days, hours, mins = days_hours_minutes(wait_for_start)
    _home_team = prepare_for_emojize(config['homeTeam'])
    _away_team = prepare_for_emojize(config['awayTeam'])
    if days > 0:
        print(f":{_home_team}: v :{_away_team}: {days}:{hours:02}:{mins:02} | symbolize=false")
    else:
        print(f":{_home_team}: v :{_away_team}: {hours}:{mins:02} | symbolize=false")
    print("---")
    date_time = start_time.strftime("%a %b %d at %-I:%M %p")
    print(f"{config['homeTeam']} vs {config['awayTeam']} starts on {date_time} | color = royalblue")
    exit()

# match is live (or finished - need to decide what to do (if anything) with finished matches)
match_url = f"https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?lang=en&seriesId={config['seriesId']}&matchId={config['matchId']}&latest=true"

# get JSON page detailing match
page = requests.get(match_url)
match_json = page.json()

# read through JSON and put relevent entries into data structure
innings_json = match_json['scorecard']['innings']
n_innings = len(innings_json)
innings = []

for i in range(n_innings):
    # store team score
    inning = Innings(innings_json[i]['team']['name'], innings_json[i]['runs'], innings_json[i]['wickets'])
    # store individual batsmen stats
    for batter in innings_json[i]['inningBatsmen']:
        if batter['dismissalText'] == None:
            dismissal = ""
        else:
            dismissal = batter['dismissalText']['short']
        if batter['strikerate'] == None:
            strike_rate = ""
        else:
            strike_rate = f"{batter['strikerate']:.2f}"
        inning.batting_scorecard.append(BattingScore(batter['player']['name'], dismissal, replace_none(batter['runs']), replace_none(batter['balls']), replace_none(batter['sixes']), replace_none(batter['fours']), strike_rate, batter['battedType'], batter['isOut']))
    #store individual bowler stats
    n_bowler = 0
    for bowler in innings_json[i]['inningBowlers']:
        economy =  f"{bowler['economy']:.2f}"
        inning.bowling_scorecard.append(BowlingScore(bowler['player']['name'], bowler['overs'], bowler['conceded'], bowler['wickets'], economy))
        n_bowler = n_bowler + 1
    inning.n_bowler = n_bowler
    # add team and individual stats to list of innings
    innings.append(inning)


print(innings[-1].emojize_score())
print("---")

print(f"{match_json['match']['series']['alternateName']}: {match_json['match']['title']}, {match_json['match']['ground']['smallName']} | color = royalblue")
print(f"{match_json['match']['statusText']} | color = black")
for batter in innings[-1].batting_scorecard:
    if (not batter.type == 'DNB'):
        if (not batter.is_out):
            print(f"{batter.name} {batter.runs}({batter.balls}) | color = black")

print("---")

i = 0
# loop through the innings
for score in innings:
    innings_with_path = f"{environ['SWIFTBAR_PLUGIN_DATA_PATH']}/{innings_file_prefix}_{i+1}.html"
    try:
        innings_file = open(innings_with_path, "w")
    except OSError as err:
        print(f"Can't open file {innings_with_path} with error {err.errno}")
        exit()
    print(html_table_header, file = innings_file)
    height = 550 + 44*(score.n_bowler + 1)
    print(f"{score} | href=\"file://{pathname2url(innings_with_path)}\" webview=true webvieww=680 webviewh={height}")
    score.print_batting(innings_file)
    score.print_bowling(innings_file)
    print(html_table_footer, file = innings_file)
    i = i + 1

print("---")
print("Web sites | color=royalblue")
print("Cricinfo | color=black href=https://www.espncricinfo.com")
print("Cricket.com.au | color=black href=https://www.cricket.com.au")
