import requests
import os
import requests
import time
import pandas as pd
from datetime import datetime
import pprint

# Assuming 1091 = Fall SKAHL season and 332 = Division D
URL = 'https://snokinghockeyleague.com/api/game/list/1091/332/0'
GAMES_FILE = 'data/games.json'
# If we downloaded the file in the last 5m (300s), use it vs re-requesting it from API
FILE_REFRESH_SECONDS = 300
START_DATE = datetime(2024, 1, 9)
END_DATE = datetime(2024, 1, 16)


# Check if the file exists
if os.path.exists(GAMES_FILE):
    # Get the modification time of the file
    last_modified_time = os.path.getmtime(GAMES_FILE)
    # Get the current time
    current_time = time.time()
    
    # Check if the file hasn't been updated in the last 5 minutes
    if current_time - last_modified_time > 300:  # 300 seconds = 5 minutes
        # Download the file
        response = requests.get(URL)
        with open(GAMES_FILE, 'wb') as file:
            file.write(response.content)
        print(f'File downloaded at {time.ctime(current_time)}')
    else:
        print(f'File is up to date.')
else:
    # Download the file if it doesn't exist
    response = requests.get(URL)
    with open(GAMES_FILE, 'wb') as file:
        file.write(response.content)
    print(f'File downloaded at {time.ctime(time.time())}')


df = pd.read_json(GAMES_FILE)
home_teams = df.teamHomeName.unique()
away_teams = df.teamAwayName.unique()
teams = set(home_teams.tolist() + away_teams.tolist())
bye_teams = set(home_teams.tolist() + away_teams.tolist())
rinks = df.rinkName.unique()
time_freq = {}
week_count = 0

for rink in rinks:
    for d in df[df.rinkName == rink].day.unique():
        day_df = df[(df.rinkName == rink) & (df.day == d)]
        day_times = day_df.time.unique()
        for t in day_times:
            tf_key = f'{rink}-{d}-{t}'
            # number of total for this time slot over the history of all games in this season
            count = len(day_df[day_df.time == t].index)
            time_freq[tf_key] = count
            
            week_df = day_df[(day_df.time == t) & (day_df.dateTime > START_DATE) & (day_df.dateTime < END_DATE)]
            week_count += len(week_df.index)
            week_teams = week_df.teamHomeName.tolist() + week_df.teamAwayName.tolist()
            for team in week_teams:
                bye_teams.remove(team)
            # print(f'tf_key: {tf_key}\ncount: {count}')

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(time_freq)
print(len(time_freq))
print(f'Games this week: {week_count}')
for team in bye_teams:
    teams.remove(team)
print(f'Teams playing:')
pp.pprint(teams)
print(f'Teams not playing:')
pp.pprint(bye_teams)

# {
#   "id": 14853,
#   "seasonId": 1091,
#   "dateTime": "2023-09-06T21:40:00",
#   "date": "9/6/2023",
#   "day": "Wed",
#   "time": "9:40 PM",
#   "rinkName": "Kirkland",
#   "teamHomeName": "Deception Pass",
#   "teamAwayName": "Goal Diggers",
#   "scoreHome": 3,
#   "scoreAway": 7,
#   "isScoresheetSet": true,
#   "isRostersSet": true,
#   "teamHomeSeasonId": 2929,
#   "teamAwaySeasonId": 2928
# }

# for game_day in df['Day'].unique():
#     day_df = df.loc[df['Day'] == game_day]
#     day_df = day_df.loc[day_df['dateTime'] > '2023-11-01']
#     print(day_df)