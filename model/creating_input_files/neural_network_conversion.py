import csv

from betting_app.api.constants import NETWORK_REP_KEYS

def match_pairs(records):
    from collections import defaultdict
    by_date = defaultdict(list)
    for rec in records:
        date, self_id, opponent_id, *rest = rec
        by_date[date].append(rec)

    matched = []
    seen = set()

    for date, recs in by_date.items():
        for r1 in recs:
            for r2 in recs:
                if r1 is r2:
                    continue
                # Corrected indices: self_id vs opponent_id
                if r1[1] == r2[2] and r1[2] == r2[1]:
                    key = tuple(sorted([r1[1], r2[1]]) + [date])
                    if key not in seen:
                        matched.append((r1, r2))
                        seen.add(key)
    return matched

def read_network_from_csv(filename: str) -> dict[str, list[str]]:
    data = []
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        for row in reader:
            data.append(row)
        
    return data


def write_network_representation(network_data: list[dict], league_id: int, season: int):
    with open(f"betting_app/model/input_files/{season}/{league_id}/neural_network_rep.csv", "w", newline="") as f:
        writer = csv.writer(f)
        entry = network_data[1]
        
        keys = NETWORK_REP_KEYS['asian odds'] + NETWORK_REP_KEYS['odds'] + NETWORK_REP_KEYS['match_data'] + [NETWORK_REP_KEYS['label']] + [block for block in NETWORK_REP_KEYS['data']]
        row = entry['asian odds'] + entry['odds'] + entry['match_data'] + [entry['label']] + [val for block in entry['data'] for val in block]
        writer.writerow(keys)
        writer.writerow(row)

        for entry in network_data[1:]:
            row = entry['asian odds'] + entry['odds'] + entry['match_data'] + [entry['label']] + [val for block in entry['data'] for val in block]
            writer.writerow(row)
        