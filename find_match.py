#!/usr/bin/env -P/Users/andrew/.asdf/shims/:/Users/180341c/.asdf/shims/ python

# <bitbar.title>Companion program for Cricket</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>Andrew Rohl</bitbar.author>
# <bitbar.author.github>arohl</bitbar.author.github>
# <bitbar.desc>Finds a cricket team's matches</bitbar.desc>
# <bitbar.dependencies>python3 requests</bitbar.dependencies>

import requests
import json
import errno
import os
from fake_useragent import UserAgent

my_team = "AUS"
matches_url = "https://hs-consumer-api.espncricinfo.com/v1/pages/matches/current?lang=en&latest=true"
config_file = ".cricket.config"
config_with_path = f"{os.environ['SWIFTBAR_PLUGINS_PATH']}/{config_file}"

try:
    os.remove(config_with_path)
except:
    pass

ua = UserAgent()
headers = {'User-Agent': ua.safari}
page = requests.get(matches_url, headers=headers)
matches_json = page.json()

found = False
for match in matches_json["matches"]:
    for team in match["teams"]:
        if team["team"]["abbreviation"] == my_team:
            found = True
            start_time = match["startTime"]
            home_team = match["teams"][0]["team"]["name"]
            away_team = match["teams"][1]["team"]["name"]
            match_id = match["objectId"]
            series_id = match["series"]["objectId"]
    if found:
        break

if found:
    config = {
        "seriesId": series_id,
        "matchId": match_id,
        "homeTeam": home_team,
        "awayTeam": away_team,
        "startTime": start_time,
    }
else:
    exit()

with open(config_with_path, "w") as f:
    json.dump(config, f)
