from GetFotMobStats import rolling_avg_window
from file_read_and_write import get_all_teams_for_league_and_year, load_csv
from end_of_season import PLACEMENT_STATS, add_promoted_teams, save_totals_to_csv
from betting_app.api.constants import TEAM_ID_TO_NAME, headers, SEASONS
import numpy as np

'''
f1 = [3,2,1,0,2,0,1,3,5,3,5,1,2,1,
2,7,1,0,0,3,3,0,0,0,6,0,1,1,1,0,1,5,1,1]

l = rolling_avg_window([str(f) for f in f1])
print(len(f1))
print(len(l))
print(l[:5])
'''


league_id = 48
year = 2025
expected_num_games = 46

'''
match_data_dict = get_all_teams_for_league_and_year(league_id, year)

totals = {}
for match in match_data_dict.values():
    index = match['Ball possession'].index('')
    m = {
        match['team_id'][0]: 
            {
                'wins': round(np.sum(np.array(match['Points Earned'][:index]).astype(int) == 3) * expected_num_games / index,3),
                'draws': round(np.sum(np.array(match['Points Earned'][:index]).astype(int) == 1) * expected_num_games / index,3),
                'losses': round(np.sum(np.array(match['Points Earned'][:index]).astype(int) == 0) * expected_num_games / index,3),
                **{stat_name: round(np.sum([float(v) if v != '' else 0.0 for v in match[stat_name][:index]]) * expected_num_games / index, 3) 
                for stat_name in PLACEMENT_STATS}
            }
    }

    totals.update(m)
#print(totals)

for t, v in totals.items():
    v.update({'goal diff': round(v['goals'] - v['goals against'], 3), 'id': t, })

save_totals_to_csv(year, league_id, totals)



for year in [2021, 2022, 2023, 2024, 2025]:
    add_promoted_teams(league_id, year)
'''
team_names = [v for v in TEAM_ID_TO_NAME.values()]
teams_to_change = []
for season in SEASONS:
    data = load_csv(f'{season}/{league_id}/betting.csv')
    data = np.array(data[1:])
    for d in data[:, 2]:
        if d not in team_names and d not in teams_to_change:
            print(d)
            teams_to_change.append(d)

import requests
def get_all_teams_for_dict(seasons: list[int]):
    all_teams = []
    for season in seasons:
        url = f"https://www.fotmob.com/api/leagues?id={league_id}&season={season}/{season+1}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        try:
            league_teams = (
                data.get('table', {})[0]
                    .get('data', {})
                    .get('table', {})
                    .get('all', {})
            )
        except AttributeError:
            league_teams = []

        team_names = [t['name'] for t in league_teams]
        team_ids = [t['id'] for t in league_teams]
        for i in range(len(team_names)):
            if str(f'\'{team_ids[i]}\' : \'{team_names[i]}\',') not in all_teams and str(team_ids[i]) not in TEAM_ID_TO_NAME:
                all_teams.append(f'\'{team_ids[i]}\' : \'{team_names[i]}\',')

    return all_teams

#at = get_all_teams_for_dict([2020, 2021, 2022, 2023, 2024, 2025])
#print(at)