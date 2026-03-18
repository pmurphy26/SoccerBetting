import os

import pandas as pd
from GetFotMobStats import rolling_avg_window
from neural_network_conversion import match_pairs, write_network_representation
import csv
from betting_app.api.constants import FILE_TYPES, FORM_STAT_NAME, GAME_STATS_TO_AVERAGE_AND_SAVE, GAME_STATS_TO_SAVE, TO_BE_COMPUTED, USED_TO_MATCH_STAT_NAMES
from read_betting_file import add_betting_data_to_network_rep
import numpy as np

from file_read_and_write import get_all_teams_for_league_and_year

'''
Function that takes single team matches and completes defensive and calcualted stats
'''
def get_full_match_data_for_year(league_id: int, year_match_data_dict, year: int):
    matches_in_year = year_match_data_dict[year]
    
    '''
    #match defensive stats
    for team_name, matches in matches_in_year.items():
        L = len(matches['opponentID'])
        defensive_stats = {}
        for i in range(L):
            defensive_stat = getMatchedGameStats(matches['team_id'][i], matches['opponentID'][i], matches_in_year)
            for key, value in defensive_stat.items():
                defensive_stats.setdefault(key, []).append(value)
        matches.update(defensive_stats)
    '''

    #calculating points earned stat
    for matches in matches_in_year.values():
        gls_home = matches['goals']
        gls_away = matches['goals against']

        points_earned = ['1' if gl_home == gl_away else '3' 
                         if gl_home > gl_away else '0'
                        for gl_home, gl_away in zip(gls_home, gls_away)]
        matches.update({FORM_STAT_NAME: points_earned})

        '''
        Computing rolling averages
        '''
        newDict = {}
        for stat_name, stat_arr in matches.items():
            if stat_name in GAME_STATS_TO_AVERAGE_AND_SAVE:
                avgs = rolling_avg_window(stat_arr)
                newDict[stat_name + ' average'] = avgs
        matches.update(newDict)

        '''
        Computing conversions/combo stats
        '''
        newDict = {}
        for stat_arr in TO_BE_COMPUTED:
            div_res = [round(float(s2) / float(s1), 3) if not (float(s1) == 0) else 0 for s1, s2 in zip(matches[stat_arr[0]], matches[stat_arr[1]])]
            newDict[f'{stat_arr[0]}/{stat_arr[1]}'] = div_res
        matches.update(newDict)

    '''
    Write data to files
    '''
    
    #print("Keys:", list[matches_in_year.values()][0].keys())
    os.makedirs(os.path.join('betting_app', 'model', 'input_files', str(year)), exist_ok=True)
    os.makedirs(os.path.join('betting_app', 'model', 'input_files', str(year), str(league_id)), exist_ok=True)
    for ft in FILE_TYPES:
        os.makedirs(os.path.join('betting_app', 'model', 'input_files', str(year), str(league_id), ft), exist_ok=True)  

    for team_name, matches in matches_in_year.items():
        df = pd.DataFrame(matches)
        df.to_excel(f"betting_app/model/input_files/{year}/{league_id}/xlsx/{team_name}.xlsx", index=False)
        df.to_csv(f"betting_app/model/input_files/{year}/{league_id}/csv/{team_name}.csv", index=False)
        #print("Saved fixtures to test.xlsx and test.csv")
    
    
    return matches_in_year

def convert_to_network_data(league_id: int, year_match_data_dict, year: int, isNotComplete: bool = True):
    matches_in_year = get_full_match_data_for_year(league_id, year_match_data_dict, year) if isNotComplete else year_match_data_dict[year]
    #getting 3 stats and matching
    matches_arr = [] #3 x (num_matches * 2) shape
    for team_name, matches in matches_in_year.items():
        L = len(matches[USED_TO_MATCH_STAT_NAMES[0]]) #num_matches
        #print(L)
        match_representation = []
        for i in range(L):
            match_rep_id = [matches[stat_name][i] for stat_name in USED_TO_MATCH_STAT_NAMES]
            game_stats = [matches[stat_name][i] for stat_name in GAME_STATS_TO_SAVE]
            team_stats_for_match = [matches[stat_name + ' average'][i] for stat_name in GAME_STATS_TO_AVERAGE_AND_SAVE]
            computed_stats = [matches[f'{stat_name[0]}/{stat_name[1]}'][i] for stat_name in TO_BE_COMPUTED]
            #print(len(match_rep_id), len(game_stats), len(team_stats_for_match), len(computed_stats))

            #representation of match for neural network
            rep = match_rep_id + game_stats + team_stats_for_match + computed_stats
            match_representation.append(rep)
        matches_arr += match_representation
            
    print("Number of match representations:", len(matches_arr), len(matches_arr[0]))

    m = match_pairs(matches_arr)
    print("Number of games:", len(m))
    #print(m[0])
    
    #converting pairs to a data point
    game_representation = []
    for pair in m:
        isHomeIndex = len(USED_TO_MATCH_STAT_NAMES)
        match_info = pair[0][:isHomeIndex + 3]

        num_team_stats_per_rep = len(GAME_STATS_TO_AVERAGE_AND_SAVE) + len(TO_BE_COMPUTED)
        #print(num_team_stats_per_rep)
        first_team_stats = pair[0][-num_team_stats_per_rep:]
        second_team_stats = pair[1][-num_team_stats_per_rep:]
        rep = [first_team_stats, second_team_stats] if pair[0][isHomeIndex] == 'False' or pair[0][isHomeIndex] == False else [second_team_stats, first_team_stats]
        #print("Game:\n", rep)
        
        #Labels: 0 -> home win, 1 -> draw, 2 -> away win
        score = pair[0][isHomeIndex + 1:isHomeIndex+3]
        #print(score)
        coeff = 1 if match_info[-1] == 'False' or match_info[-1] == False else -1
        diff = max(-1, min(1, coeff * (int(score[0]) - int(score[1]))))
        label = 1 - diff
        game_representation.append({'match_data': match_info, 'label': label, 'data': rep})
        #print("Label:", label, "coefficient:", coeff)

    return game_representation

'''
Use this function to convert .csv file data into neural network data
'''
def get_network_representation_for_league(league_id: int, seasons: list[int]):
    #mirrors directory layout: dict[year][team_name][stat_name]
    year_match_data_dict = {k: get_all_teams_for_league_and_year(league_id, k) for k in seasons}
    
    for szn in seasons:
        gr = convert_to_network_data(league_id, year_match_data_dict, szn) #list of {match_info, label, data} objects
                                                #data = 2D array with shape num_stats x 3 (home, away, diff)
        write_network_representation(gr, league_id, szn)
        print(f'uploaded data for {szn}')

def get_just_network_representation_for_league(league_id: int, seasons: list[int]):
    #mirrors directory layout: dict[year][team_name][stat_name]
    year_match_data_dict = {k: get_all_teams_for_league_and_year(league_id, k) for k in seasons}
    for szn in seasons:
        print('converting', szn, 'data to network data')
        gr = convert_to_network_data(league_id, year_match_data_dict, szn, False) #list of {match_info, label, data} objects
                                                #data = 2D array with shape num_stats x 3 (home, away, diff)
        new_network_rep = add_betting_data_to_network_rep(np.array(gr), league_id, szn)
        write_network_representation(new_network_rep, league_id, szn)
        