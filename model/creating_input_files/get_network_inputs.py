import os
import numpy as np
import pandas as pd

from convert import get_full_match_data_for_year, get_just_network_representation_for_league
from file_read_and_write import get_all_teams_for_league_and_year
from GetFotMobStats import write_betting_odds_to_future_games, write_league_match_data_to_files
from betting_app.api.constants import LEAGUE_IDS, SEASONS
from end_of_season import calculate_end_of_season_data
from read_betting_file import write_league_season_betting_data_to_files

#league_id = LEAGUE_IDS['LALIGA']
years = [2020, 2021, 2022, 2023, 2024, 2025]
season = 2025

for league_id in [87, 54, 55]:
    print('Getting most recent data for league id:', league_id)
    '''
    Convert file from betting site to betting.csv
    '''
    write_league_season_betting_data_to_files(league_id, season)

    '''
    Use this to create csv and xlsx files for league and seasons
    '''
    #write_league_match_data_to_files(league_id, SEASONS)
    write_league_match_data_to_files(league_id, [2025])


    '''
    Use this to complete all the csv and xlsx files extra/defensive stats
    '''
    get_full_match_data_for_year(league_id, {season: get_all_teams_for_league_and_year(league_id, season)}, season)

    '''
    Use this after generating all of the csv and xlsx files for a league to generate the end of season stats
    '''
    calculate_end_of_season_data(season, league_id)

    '''
    Use this to generate neural network rep
    '''
    #get_just_network_representation_for_league(league_id, SEASONS)
    get_just_network_representation_for_league(league_id, [2025])

    '''
    Use this once the full neural network rep has been generated to add future betting odds 
    '''
    write_betting_odds_to_future_games(league_id, '2025')