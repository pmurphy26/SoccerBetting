import pandas as pd
import os
import csv
from collections import deque
import re

from get_game_stats import get_all_stats
from betting_app.api.constants import FILE_TYPES
from file_read_and_write import load_csv

'''
Function that takes in league id and list of seasons and will write 
data for all matches that occured in that league over the season to a .csv and .xlsx file
'''
def write_league_match_data_to_files(league_id: int, seasons: list[int]):
    seasons_strs = [f'{y}/{y+1}' for y in seasons]
    print('Seasons:', seasons_strs)
    for season in seasons_strs:
        write_league_season_match_data_to_files(league_id, season)
        print(f'written data for {season}')

def write_league_season_match_data_to_files(league_id: int, season: str):
    p, tid = get_all_stats(league_id, season)
    #print(p.keys())
    #print(tid.keys())
    #print([len(v) for v in p.values()])

    szn = season[:season.find('/')]
    os.makedirs(os.path.join('betting_app', 'model', 'input_files', szn), exist_ok=True)
    os.makedirs(os.path.join('betting_app', 'model', 'input_files', szn, str(league_id)), exist_ok=True)
    for ft in FILE_TYPES:
        os.makedirs(os.path.join('betting_app', 'model', 'input_files', szn, str(league_id), ft), exist_ok=True)

    rows = []
    for team_id, matches in p.items():
        for match in matches:
            row = {"team_id": team_id, **match}
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_excel(f"betting_app/model/input_files/{szn}/{league_id}/xlsx/{tid[team_id]['name']}.xlsx", index=False)
        df.to_csv(f"betting_app/model/input_files/{szn}/{league_id}/csv/{tid[team_id]['name']}.csv", index=False)
        #print("Saved fixtures to test.xlsx and test.csv")
        rows = []   

def rolling_avg_window(data: list[int], window: int = 5):
    averages = []
    window_vals = deque(maxlen=window)

    for i, val in enumerate(data):
        parsed_num_info = parse_number_from_csv_file(val)
        #print(parsed_num_info, len(window_vals))
        if parsed_num_info['type'] == 'name': 
            parsed_val = parsed_num_info['value']
            averages.append(parsed_val)
        else:
            parsed_num = parsed_num_info['value']
            v = (averages[i-1] if i > 0 else 0) if parsed_num is None else parsed_num
            avg = round(sum(window_vals) / len(window_vals), 3) if len(window_vals) > 0 else 0
            window_vals.append(v)
            averages.append(avg)

    return averages

def parse_number_from_csv_file(s: str):
    # Pattern for "num (percentage%)"
    match = re.fullmatch(r"(\d+)\s*\((\d+)%\)", s)
    if match:
        num = int(match.group(1))
        percent = int(match.group(2))
        return {"type": "num (percentage%)", "value": num, "percent": percent}
    
    # Pattern for decimal number
    match = re.fullmatch(r"(\d+\.\d+)", s)
    if match:
        return {"type": "decimal_num", "value": float(match.group(1))}
    
    # Pattern for whole number
    match = re.fullmatch(r"(\d+)", s)
    if match:
        return {"type": "whole_num", "value": int(match.group(1))}
    
    # If the string contains any text other than (, ), or %, treat as name
    if any(ch.isalpha() for ch in s) or re.search(r"[^()\%]", s):
        return {"type": "name", "value": s}
        

    return {"type": "unknown", "value": None}


import numpy as np
import os
from datetime import datetime, timezone
import pandas as pd
import requests
from betting_app.api.constants import headers


'''
Gets a list of all the games that still haven't been played and need betting data
'''
def get_all_unplayed_games_for_league_year(league_id: int, season: str):
    url = f"https://www.fotmob.com/api/leagues?id={league_id}"
    if season is not None:
        url += f"&season={season}"
    #print(url)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    fixtures_data = data['fixtures']
    unplayed_info = fixtures_data['firstUnplayedMatch']
    unplayed_index = unplayed_info['firstUnplayedMatchIndex']
    return [[d['id'], d['home']['id'], d['away']['id']] for d in data['fixtures']['allMatches'][unplayed_index:]]
    
def get_betting_data_for_unplayed_games(match_id: int):
    url = f"https://www.fotmob.com/api/data/matchOdds?matchId={match_id}&ccode3=USA_NC&bettingProvider=Bet365_North%20Carolina"
    
    #print(url)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    try:
        odds_data = data['odds']['matchfactMarkets'][0]['selections']
        odds = []
        for o in odds_data:
            odds.append(o['oddsDecimal'])
        return odds
    except:
        return [-1, -1, -1]


'''
Use this function to add future matche's betting odds to neural_network_rep
'''
def write_betting_odds_to_future_games(league_id: int, season: str):
    neural_network_rep = np.array(load_csv(f'betting_app/model/input_files/{season}/{league_id}/neural_network_rep.csv'))
    print(len(neural_network_rep))

    current_date = datetime.now(timezone.utc)
    # Convert column 6 into Python datetimes
    timestamps = np.array([
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        for ts in neural_network_rep[1:, 6]
    ])
    mask = ((neural_network_rep[1:, :6] == '-1').all(axis=1)
            & (current_date <= timestamps))
    league_network_data = neural_network_rep[1:][mask]
    print(len(league_network_data))
    good_league_data = neural_network_rep[1:][~mask]
    print(len(good_league_data))


    ids = get_all_unplayed_games_for_league_year(league_id, season)
    for id in ids:
        o = get_betting_data_for_unplayed_games(id[0])
        if o == [-1, -1, -1]:
            break
        
        print(id, o)
        for i in range(len(league_network_data)):
            l_teams = league_network_data[i,7:9]
            
            if id[1] in l_teams and id[2] in l_teams:
                league_network_data[i] = np.concatenate([league_network_data[i, :3], o, league_network_data[i, 6:]])


    #'2026-01-14T19:30:00.000Z' '8358' '178475'
    print(len(ids))

    os.makedirs(os.path.join('betting_app','model','input_files', season), exist_ok=True)
    os.makedirs(os.path.join('betting_app','model','input_files', season, str(league_id)), exist_ok=True)

    df = pd.DataFrame(np.vstack([good_league_data, league_network_data]), columns=neural_network_rep[0])
    df.to_csv(f"betting_app/model/input_files/{season}/{league_id}/neural_network_rep.csv", index=False)
