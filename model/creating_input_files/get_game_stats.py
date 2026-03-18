import pandas as pd
import requests
from betting_app.api.constants import headers

'''
Helper functions for get_all_stats
'''
def get_competition_match_ids(league_id: int, season: str | None = None) -> list[int]:
    url = f"https://www.fotmob.com/api/leagues?id={league_id}"
    if season is not None:
        url += f"&season={season}"
    #print(url)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    return [d['id'] for d in data['fixtures']['allMatches']]

def get_match_stats(match_id):
    url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    try:
        game_stats = (
            data.get('content', {})
                .get('stats', {})
                .get('Periods', {})
                .get('All', {})
                .get('stats', {})
        )
    except AttributeError:
        game_stats = {}

    game_info = data['general']
    date = game_info['matchTimeUTCDate']
    home_team = game_info['homeTeam']
    away_team = game_info['awayTeam']
    home_team_score = 0
    away_team_score = 0
    
    try:
        game_scores = (
            data.get('header', {})
                .get('teams', [])
        )
    except AttributeError:
        game_scores = []

    if not len(game_scores) == 0:
        firstScoreHome = game_scores[0]['id'] == home_team['id']
        home_team_score = game_scores[0]['score'] if firstScoreHome else game_scores[1]['score']
        away_team_score = game_scores[1]['score'] if firstScoreHome else game_scores[0]['score']


    #dicts to return
    home_dict = {
        'date': date,
        'opponentID': away_team['id'],
        'opponentName': away_team['name'],
        'goals': home_team_score,
        'goals against': away_team_score,
        'isHome': True
    }
    away_dict = {
        'date': date,
        'opponentID': home_team['id'],
        'opponentName': home_team['name'],
        'goals': away_team_score,
        'goals against': home_team_score,
        'isHome': False
    }

    for top_stats in game_stats:
        home_stats = [{d['title']: d["stats"][0]} for d in top_stats['stats']] + [{f'{d['title']} against': d["stats"][1]} for d in top_stats['stats']]
        away_stats = [{d['title']: d["stats"][1]}  for d in top_stats['stats']] + [{f'{d['title']} against': d["stats"][0]} for d in top_stats['stats']]
        
        home_dict = {
            **home_dict,
            **{k: v for d in home_stats for k, v in d.items()}
        }
        away_dict = {
            **away_dict,
            **{k: v for d in away_stats for k, v in d.items()}
        }
    
    return  ({
            away_team['id']: away_dict, 
            home_team['id']: home_dict
        }, 
        {
            'home': home_team, 
            'away': away_team
        })

'''
Gets all of the statistics for each match in a league in a single year
'''    
def get_all_stats(league_id: int, season: str | None = None): 
    teams_stats_dict = {}
    team_info_dict = {}

    ids = get_competition_match_ids(league_id, season)
    for id in ids:
        match_dict, team_info = get_match_stats(id)
        for key, value in match_dict.items():
            if key in teams_stats_dict:
                teams_stats_dict[key] += [value]
            else:
                teams_stats_dict[key] = [value]

            key_team_info = team_info['home'] if team_info['home']['id'] == key else team_info['away']
            if key not in team_info_dict:
                team_info_dict[key] = key_team_info

    return teams_stats_dict, team_info_dict
