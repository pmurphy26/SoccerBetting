import numpy as np

from scipy.stats import poisson

# Regular score matrix
def score_matrix(lambda_home, lambda_away, max_goals=7):
    P = np.zeros((max_goals+1, max_goals+1))
    for i in range(max_goals+1):
        for j in range(max_goals+1):
            P[i, j] = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)
    return P

# Dixon–Coles draw inflation
def score_matrix_dc(lambda_home, lambda_away, rho=1.15, max_goals=7):
    P = np.zeros((max_goals+1, max_goals+1))

    for i in range(max_goals+1):
        for j in range(max_goals+1):
            P[i,j] = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)

            if (i,j) in [(0,0),(1,1),(0,1),(1,0)]:
                P[i,j] *= rho

    return P / P.sum()

def wdl_from_score_matrix(P):
    home_win = np.tril(P, -1).sum()
    draw     = np.trace(P)
    away_win = np.triu(P,  1).sum()
    return home_win, draw, away_win


def make_prediction_from_odds(odds, draw_threshold = 0.27):
  home, draw, away = odds
  if draw > draw_threshold:
    return 1
  elif home > away:
    return 0
  else:
    return 2

def get_result_from_label(label: list[int]) -> int:
  if label[0] > label[1]:
    return 0
  elif label[0] < label[1]:
    return 2
  else:
    return 1

def get_book_odds(network_data):
  book_odds = []
  for i in range(len(network_data)):
    book_multiplier_odds = [1/float(o) for o in network_data[i, :3]]
    s = sum(book_multiplier_odds)
    book_odds_for_game = [round(o / s, 2) for o in book_multiplier_odds]
    book_odds.append(book_odds_for_game)

  book_odds = np.array(book_odds)

  return book_odds


def convert_lambdas_to_predictions_and_results(model_lambda_predictions, all_leagues_labels, draw_threshold=0.27):
  #print(model_lambda_predictions[:10])
  #print(model_lambda_predictions.shape)
  predicted_odds = [wdl_from_score_matrix(score_matrix(pred[0], pred[1])) for pred in model_lambda_predictions]
  #print(draw_threshold)
  match_predictions_from_odds = []
  for p in predicted_odds:
    am = make_prediction_from_odds(p, draw_threshold)
    match_predictions_from_odds.append(am)


  correct_guesses = []
  actual_results = []
  for i in range(len(match_predictions_from_odds)):
    res = get_result_from_label(all_leagues_labels[i])
    guessed_correctly = match_predictions_from_odds[i] == res
    correct_guesses.append(guessed_correctly)
    actual_results.append(res)


  print("Total guesses:", len(correct_guesses))
  print("Accuracy:", np.sum(correct_guesses) / len(correct_guesses))

  draw_rates = [odds[1] for odds in predicted_odds]
  print("Average draw odds:", np.mean(draw_rates), "\n")

  return predicted_odds, match_predictions_from_odds, correct_guesses, actual_results

def select_good_bets(network_data, predicted_odds, book_odds, correct_guesses, all_leagues_labels,
                     bad_mult_threshold = 1.85,
                     bad_gap_threshold = 0.1,
                     bad_draw_threshold = 0.325,
                     bad_draw_mult_threshold = 3.5
):
  bad_multiplier = (network_data[:, :3].astype(float) <= bad_mult_threshold).any(axis=1)
  #print(f'Bad multiplier: {bad_multiplier}')


  idx = predicted_odds.argmax(axis=1)
  bad_gap = (book_odds[np.arange(len(book_odds)), idx] - predicted_odds[np.arange(len(predicted_odds)), idx]) >= bad_gap_threshold
  #print('Bad gap:', bad_gap)

  predicted_draw = (predicted_odds[:, 1] > bad_draw_threshold) | (network_data[:, 1].astype(float) < bad_draw_mult_threshold)

  #print(network_data[:3, :3])
  #print(book_odds[:3])
  #print(predicted_odds[:3])


  correct_guesses_taken = np.array(correct_guesses)[~(bad_multiplier | predicted_draw | bad_gap)]
  #taken_total_true = sum(correct_guesses_taken)
  #taken_total_false = len(correct_guesses_taken) - sum(correct_guesses_taken)

  #print("Correct bets placed:", taken_total_true)
  #print("incorrect bets placed:", taken_total_false)
  #print('Total count:', len(correct_guesses_taken))

  all_leagues_labels_taken = all_leagues_labels[~(bad_multiplier | predicted_draw | bad_gap)]
  network_data_taken = network_data[~(bad_multiplier | predicted_draw | bad_gap)]
  #print(network_data.shape, network_data_taken.shape)
  #print(all_leagues_labels.shape, all_leagues_labels_taken.shape)

  #asian_odds_taken = asian_odds_data[~(bad_multiplier | predicted_draw | bad_gap)]
  #print(asian_odds_data.shape, asian_odds_taken.shape)
  return network_data_taken, correct_guesses_taken, all_leagues_labels_taken

def get_select_good_bets_mask(network_data, predicted_odds, book_odds, correct_guesses, all_leagues_labels,
                     bad_mult_threshold = 1.9,
                     bad_gap_threshold = 0.1,
                     bad_draw_threshold = 0.3,
                     bad_draw_mult_threshold = 3.5
):
  bad_multiplier = (network_data[:, :3].astype(float) <= bad_mult_threshold).any(axis=1)
  idx = predicted_odds.argmax(axis=1)
  bad_gap = (book_odds[np.arange(len(book_odds)), idx] - predicted_odds[np.arange(len(predicted_odds)), idx]) >= bad_gap_threshold

  predicted_draw = (predicted_odds[:, 1] > bad_draw_threshold) | (network_data[:, 1].astype(float) < bad_draw_mult_threshold)
  mask = ~(bad_multiplier | predicted_draw | bad_gap)

  return mask