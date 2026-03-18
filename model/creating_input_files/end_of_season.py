import os
import numpy as np
import pandas as pd
import csv
from file_read_and_write import load_csv, get_all_teams_for_league_and_year


PLACEMENT_STATS = ['Points Earned', 'goals', 'goals against', 
                   'Expected goals (xG)', 'Expected goals (xG) against', 
                   'Ball possession', 'Total shots', 'Shots on target',
                   'Total shots against', 'Shots on target against']

def save_totals_to_csv(year, league_id, avgs: dict):
    os.makedirs(str(year), exist_ok=True)
    os.makedirs(os.path.join(str(year), str(league_id)), exist_ok=True)

    df = pd.DataFrame.from_dict(avgs, orient='index')
    df.to_csv(f"{year}/{league_id}/{year}_{league_id}_final_stats.csv", index=False)

def calculate_end_of_season_data(year, league_id):
    match_data_dict = get_all_teams_for_league_and_year(league_id, year)
    totals = {
        match['team_id'][0]: 
            {
                'wins': np.sum(np.array(match['Points Earned']).astype(int) == 3),
                'draws': np.sum(np.array(match['Points Earned']).astype(int) == 1),
                'losses': np.sum(np.array(match['Points Earned']).astype(int) == 0),
                **{stat_name: round(np.sum([float(v) if v != '' else 0.0 for v in match[stat_name]]), 3) 
                for stat_name in PLACEMENT_STATS}
            }
        for match in match_data_dict.values()
    }

    for t, v in totals.items():
        v.update({'goal diff': v['goals'] - v['goals against'], 'id': t, })

    save_totals_to_csv(year, league_id, totals)

def save_new_end_of_year_rep_to_csv(year, league_id, data):
    os.makedirs(str(year), exist_ok=True)
    os.makedirs(os.path.join(str(year), str(league_id)), exist_ok=True)

    df = pd.DataFrame(data[1:], columns=data[0])
    df.to_csv(f"{year}/{league_id}/{year}_{league_id}_final_stats.csv", index=False)

def add_promoted_teams(league_id, current_season):
    prev_season_data = np.array(load_csv(f'{current_season-1}/{league_id}/{current_season-1}_{league_id}_final_stats.csv'))
    #print(prev_season_data[1:, -1])
    current_season_data = np.array(load_csv(f'{current_season}/{league_id}/{current_season}_{league_id}_final_stats.csv'))
    #print(current_season_data[1:, -1])

    to_add_to_prev_season = []
    for team_data in current_season_data[1:]:
        team_id = team_data[-1]
        if team_id not in prev_season_data:
            print(team_id)
            to_add_to_prev_season.append(team_data)
    print('Teams above were promoted and need to be added\n')
    
    if len(to_add_to_prev_season) != 0:        
        new_prev_season_data = np.vstack([prev_season_data, np.array(to_add_to_prev_season)])
        #print(new_prev_season_data)
        save_new_end_of_year_rep_to_csv(current_season-1, league_id, new_prev_season_data)
    else:
        print('No data to be added')