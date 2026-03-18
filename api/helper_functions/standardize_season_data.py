import os
import csv
import numpy as np

FORM_DIM = 13
HOME_FORM_STAT_INDICES = [41, 13, 27, 15, 29, 21, 17, 19, 31, 33, 25, 23, 37] #[38, 10, 24, 12, 26, 18, 14, 16, 28, 30, 22, 20, 34]
AWAY_FORM_STAT_INDICES = [42, 14, 28, 16, 30, 22, 18, 20, 32, 34, 26, 24, 38] #[39, 11, 25, 13, 27, 19, 15, 17, 29, 31, 23, 21, 35]
STATS_INDEX = 13

BUNDESLIGA_SEASON_DATES_DICT = { #yy, mm, dd
    2020: [[2020, 7, 18], [2021, 6, 22]],
    2021: [[2021, 7, 13], [2022, 6, 14]],
    2024: [[2024, 7, 23], [2025, 6, 17]],
    2023: [[2023, 7, 18], [2024, 6, 18]],
    2022: [[2022, 7, 5], [2023, 6, 27]],
    2025: [[2025, 7, 22], [2026, 6, 16]]
}

LALIGA_SEASON_DATES_DICT = {
    2020: [[2020, 9, 12],[2021, 5, 23]],
    2021: [[2021, 8, 13], [2022, 5, 22]],
    2022: [[2022,8,12],[2023, 6, 4]],
    2023: [[2023, 8, 11], [2024, 5, 26]],
    2024: [[2024, 8, 15], [2025, 5, 25]]
}

SERIEA_DATES_DICT = {
    2020: [[2020, 9, 19],[2021, 5, 23]],
    2021: [[2021, 8, 13], [2022, 5, 22]],
    2022: [[2022,8,12],[2023, 6, 4]],
    2023: [[2023, 8, 11], [2024, 5, 26]],
    2024: [[2024, 8, 15], [2025, 5, 25]],
    2025: [[2025, 8, 20], [2026, 5, 30]]
}

SEASON_DATES_DICT = BUNDESLIGA_SEASON_DATES_DICT


def convert_date_str_to_season(date_str: str, season_dates_dict: dict = SEASON_DATES_DICT) -> int:
  date_year = int(date_str[:4])
  date_month = int(date_str[5:7])
  date_day = int(date_str[8:10])
  for key, value in season_dates_dict.items():
    if date_year < value[0][0]:
      continue
    elif date_year == value[0][0]:
      if date_month > value[0][1]:
        return key
      elif date_month == value[0][1] and date_day >= value[0][2]:
          return key
    elif date_year > value[1][0]:
      continue
    else:
      if date_month < value[1][1]:
        return key
      elif date_month == value[1][1] and date_day <= value[1][2]:
          return key

  print(f'Error: {date_year}/{date_month}/{date_day} not in SEASON_DATES_DICT')
  return date_year

def load_csv(filename):
    rows = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            numeric_row = []
            for val in row:
                if val.strip() == '':
                    continue
                try:
                    numeric_row.append(int(val))
                except ValueError:
                    try:
                        numeric_row.append(float(val))
                    except ValueError:
                        numeric_row.append(val)
            rows.append(numeric_row)
    return rows

def get_league_data(league_id, seasons):
  sys_path = os.path.join(os.getcwd(), 'model', 'input_files')
  data = []
  end_of_season_data = {}

  for season in seasons:
    stats_data = os.path.join(sys_path, f'{season}', f'{league_id}', 'neural_network_rep.csv')
    end_of_season = os.path.join(sys_path, f'{season-1}', f'{league_id}', f'{season-1}_{league_id}_final_stats.csv')
    data_to_add = load_csv(stats_data)[1:]
    #data += data_to_add

    clean_rows = []
    bad_rows = []
    for i, row in enumerate(data_to_add):
        if not isinstance(row[6], str) or "T" not in str(row[6]):
            bad_rows.append((i, row[6]))
        else:
          clean_rows.append(row)

    data += clean_rows

    print(season, bad_rows[:10])

    end_of_season_data.update({season: load_csv(end_of_season)})
    print(stats_data)
    print('Path to data: {}'.format(stats_data))
    print('Path to end os season stats: {}\n'.format(end_of_season))

  return data, end_of_season_data

def process_league_data(data):
  league_network_data = np.array([row[:51] for row in data])
  #Removes all entrys of 0's from network dataset

  print("Before filtering:")
  print(league_network_data.shape)

  mask = ~((league_network_data[:, STATS_INDEX:] == '0.0').all(axis=1) | (league_network_data[:, :6] == '-1').all(axis=1))
  league_network_data = league_network_data[mask]

  print("After filtering:")
  print(league_network_data.shape)

  return league_network_data

def process_end_of_season_data(end_of_season_data):
  all_season_data_dict = {}
  for season_year, season_data in end_of_season_data.items():
    #data_labels = season_data[0]
    data_to_standardize = np.array(season_data[1:])
    standardized_seasonal_data = []
    for i in range(data_to_standardize.shape[1] - 1):
      dts = data_to_standardize[:, i].astype(float)
      mean = dts.mean()
      std = dts.std()
      zscore = (dts - mean) / std
      #print(len(zscore))
      if i == 0:
        standardized_seasonal_data = zscore
      else:
        standardized_seasonal_data = np.column_stack((standardized_seasonal_data, zscore))

    standardized_seasonal_data = np.column_stack((standardized_seasonal_data, data_to_standardize[:,-1].astype(int)))
    season_data_dict = {s[-1]: s[:-2] for s in standardized_seasonal_data}
    all_season_data_dict.update({season_year: season_data_dict})

  return all_season_data_dict

def get_form_data(network_data):
  print(network_data.shape)

  home_form_network_inputs = []
  for i in HOME_FORM_STAT_INDICES:
    form_data_to_standardize = network_data[:, i].astype(float)
    #print(form_data_to_standardize.shape)

    mean = form_data_to_standardize.mean()
    std = form_data_to_standardize.std()
    zscore = (form_data_to_standardize - mean) / std
    #print(len(zscore))
    if len(home_form_network_inputs) == 0:
      home_form_network_inputs = zscore
    else:
      home_form_network_inputs = np.column_stack((home_form_network_inputs, zscore))
  print(home_form_network_inputs.shape)

  away_form_network_inputs = []
  for i in AWAY_FORM_STAT_INDICES:
    form_data_to_standardize = network_data[:, i].astype(float)
    #print(form_data_to_standardize.shape)

    mean = form_data_to_standardize.mean()
    std = form_data_to_standardize.std()
    zscore = (form_data_to_standardize - mean) / std
    #print(len(zscore))
    if len(away_form_network_inputs) == 0:
      away_form_network_inputs = zscore
    else:
      away_form_network_inputs = np.column_stack((away_form_network_inputs, zscore))
  print(away_form_network_inputs.shape)
  print(network_data.shape)

  #flipping bad stats
  print(home_form_network_inputs.shape)
  form_indexes_to_flip = [2, 4, 8, 9, 12]
  for i in form_indexes_to_flip:
    home_form_network_inputs[:, i] = -1 * home_form_network_inputs[:, i]
    away_form_network_inputs[:, i] = -1 * away_form_network_inputs[:, i]

  return home_form_network_inputs, away_form_network_inputs

def get_network_inputs_and_labels(network_data, all_season_data_dict, season_dates_dict=SEASON_DATES_DICT):
  #print(network_data[0])
  network_inputs = []
  labels = []
  for n in network_data:
    date_str = n[6]
    n_year = convert_date_str_to_season(date_str, season_dates_dict)
    first_team_is_away = int(n[9] == 'False')
    ni = [all_season_data_dict[n_year][int(n[7 + first_team_is_away])], all_season_data_dict[n_year][int(n[8 - first_team_is_away])]]
    network_inputs.append(ni)
    label = [int(n[10 + first_team_is_away]), int(n[11 - first_team_is_away])]
    labels.append(label)

  labels = np.array(labels).astype(float)
  network_inputs = np.array(network_inputs)
  print("Network input's shape:", network_inputs.shape)
  print("Network data's shape:", network_data.shape)
  print("Network label's shape:", labels.shape)
  print("First label:", labels[0])

  #print('Before:', network_inputs[0])
  #flipping bad stats
  indexes_to_flip = [2, 5, 7, 11, 12]
  for i in indexes_to_flip:
    network_inputs[:, :, i] = -1 * network_inputs[:, :, i]

  #print('After', network_inputs[0])
  print(network_inputs.shape)

  return network_inputs, labels

def get_network_data(league_id, seasons):
  data, end_of_season_data = get_league_data(league_id, seasons)
  network_data = process_league_data(data)
  all_season_data_dict = process_end_of_season_data(end_of_season_data)
  home_form_network_inputs, away_form_network_inputs = get_form_data(network_data)
  network_inputs, network_labels = get_network_inputs_and_labels(network_data, all_season_data_dict)
  print(network_inputs.shape)
  print(home_form_network_inputs.shape)
  print(away_form_network_inputs.shape)

  network_inputs = np.concatenate((
      network_inputs,
      np.expand_dims(home_form_network_inputs, axis=1),
      np.expand_dims(away_form_network_inputs, axis=1)),
                                        axis=1 )
  print(network_inputs.shape)

  return network_data, network_inputs, network_labels
