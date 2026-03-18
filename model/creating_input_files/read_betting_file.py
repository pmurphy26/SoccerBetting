import csv
import os
import pandas as pd
import numpy as np
from datetime import datetime

from betting_app.api.constants import FILE_TYPES, LEAGUE_ID_TO_BETTING_FILE_NAME, SEASONS, TEAM_ID_TO_NAME
from neural_network_conversion import read_network_from_csv

RETURNED_KEYS = [
    'Date', 'HomeTeam', 'AwayTeam', #team info
    'FTHG', 'FTAG', #full time scores
    'B365H', 'B365D', 'B365A', #bet 365 3 way ML odds
    'AHCh', 'B365CAHH', 'B365CAHA' #asian spread, odds
]
def read_bet_csv_to_dict(filename: str) -> dict[str, list[str]]:
    data = {}
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for field in reader.fieldnames:
            data[field] = []
        
        for row in reader:
            for field in reader.fieldnames:
                data[field].append(row[field])
    return data

def get_league_betting_data_for_year(league_id: int, year: int, returnedKeys: list[str]):
    path = os.path.join('betting_app', 'model', 'input_files', str(year), f"{league_id}", f'{LEAGUE_ID_TO_BETTING_FILE_NAME[league_id]}.csv')
    
    all_teams_stats_for_year = {}
    try:
        d = read_bet_csv_to_dict(path)
        
        # Filter dictionary to only include requested keys
        filtered = {k: v for k, v in d.items() if k in returnedKeys}
        return filtered

    except FileNotFoundError:
        print(f"Directory not found: {path}")

    print(year)
    return all_teams_stats_for_year

'''
Use this function to convert I/D/SP/etc.csv to betting.csv
'''
def write_league_season_betting_data_to_files(league_id: int, season: int):
    betting_data_dict = get_league_betting_data_for_year(league_id, season, RETURNED_KEYS)
    
    os.makedirs(os.path.join('betting_app', 'model', 'input_files', str(season)), exist_ok=True)
    os.makedirs(os.path.join('betting_app', 'model', 'input_files', str(season), str(league_id)), exist_ok=True)

    df = pd.DataFrame.from_dict(betting_data_dict, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={"index": "game_id"}, inplace=True)
    df_flipped = df.set_index("game_id").T.reset_index()
    df_flipped.to_csv(f"betting_app/model/input_files/{season}/{league_id}/betting.csv", index=False)

    return df

def parse_date(date_str):
    try:
        # Try DD/MM/YYYY
        return datetime.strptime(date_str, "%d/%m/%Y").date().isoformat()
    except ValueError:
        # Try ISO format
        #print(date_str)
        return datetime.fromisoformat(date_str.replace("Z", "")).date().isoformat()

def normalize_match(date, home, away):
    """
    Create a canonical representation of a match so that
    ['Augsburg', 'Werder Bremen'] and ['Werder Bremen', 'Augsburg']
    are treated as the same key.
    """
    d = parse_date(date)
    return (d, tuple(sorted([home, away])))

def build_match_dict(list1, list2, tag1 = 'list1', tag2 = 'list2'):
    match_dict = {}
    
    for fixture in list1:
        date, home, away, *rest = fixture
        key = normalize_match(date, home, away)
        match_dict[key] = {
            "odds": rest[-6:-3], 
            "asian odds": rest[-3:], 
            tag1: [date, home, away]
        }
    
    for fixture in list2:
        date, home, away, *rest = fixture
        key = normalize_match(date, home, away)
        if key in match_dict:
            match_dict[key][tag2] = [date, home, away]
        else:
            match_dict[key] = {tag2: [date, home, away]}
    
    #print(match_dict.keys())
    return match_dict

def save_neural_network_arr_to_csv(data_arr, league_id: int, szn: int):
    os.makedirs(str(szn), exist_ok=True)
    os.makedirs(os.path.join(str(szn), str(league_id)), exist_ok=True)
    for ft in FILE_TYPES:
        os.makedirs(os.path.join(str(szn), str(league_id), ft), exist_ok=True)

    df = pd.DataFrame(data_arr)
    df.to_csv(f"{szn}/{league_id}/neural_network_rep.csv", index=False)

def write_relevant_betting_data_to_files(league_id: int, seasons: list[int]):
    for season in seasons:
        bd = write_league_season_betting_data_to_files(league_id, season)
        #print(len(bd))

def add_betting_data_to_network_rep(network_arr: list[dict], league_id: int, season: int):
    path = os.path.join('betting_app','model','input_files', str(season), f"{league_id}", "betting.csv")
    betting_arr = np.array(read_network_from_csv(path))[1:, 1:]
    #print(betting_arr)
    
    dates = [n['match_data'][0] for n in network_arr]
    home_teams = []
    away_teams = []

    for n in network_arr:
        isAway = int(n['match_data'][3] == 'False')

        home_teams.append(TEAM_ID_TO_NAME[n['match_data'][1 + isAway]])
        away_teams.append(TEAM_ID_TO_NAME[n['match_data'][2 - isAway]])

    stack = np.column_stack((dates, home_teams, away_teams))
    match_dict = build_match_dict(betting_arr, stack)
    
    for match in network_arr:
        m = [
            match['match_data'][0], 
            TEAM_ID_TO_NAME[match['match_data'][1]], 
            TEAM_ID_TO_NAME[match['match_data'][2]]
        ]

        md = match_dict[normalize_match(m[0], m[1], m[2])]
        #print(f'md: {md}')
        if 'odds' in md:
            o = md['odds']
            asian_o = md['asian odds']
            match.update({'odds': o, 'asian odds': asian_o})
        else:
            match.update({'odds': [-1, -1, -1], 'asian odds': [-1, -1, -1]})
            print(f'Error: {md} is missing key')

    #print("Shape after adding betting data:", network_arr.shape)
    return network_arr
    