import csv
import os


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


def read_csv_to_dict(filename: str) -> dict[str, list[str]]:
    data = {}
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for field in reader.fieldnames:
            data[field] = []
        
        for row in reader:
            for field in reader.fieldnames:
                data[field].append(row[field])
    return data

'''
returns dict of each team and their stats for the season
'''
def get_all_teams_for_league_and_year(league_id: int, year: int) -> dict:
    path = os.path.join('betting_app', 'model', 'input_files', str(year), f"{league_id}", "csv")
    
    all_teams_stats_for_year = {}
    try:
        files = os.listdir(path)
        for file in files:
            d = read_csv_to_dict(f'betting_app/model/input_files/{year}/{league_id}/csv/{file}')
            all_teams_stats_for_year[file[:file.find('.csv')]] = d
    except FileNotFoundError:
        print(f"Directory not found: {path}")

    return all_teams_stats_for_year

