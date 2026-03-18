from django.db import models

# Create your models here.
import numpy as np

import keras
import os

from .helper_functions.standardize_season_data import LALIGA_SEASON_DATES_DICT, get_form_data, get_league_data, get_network_data, get_network_inputs_and_labels, process_league_data, process_end_of_season_data
from .constants import SEASONS
keras.config.enable_unsafe_deserialization()

def load_model():
    model_path = os.path.join(os.getcwd(), 'model/decent_lambda_model_prev_year_const_2.keras')
    model = keras.models.load_model(
        model_path,
        safe_mode=False
    )

    return model

model = load_model()

def predict(home_strength_data, away_strength_data, home_form_data, away_form_data):
    val_preds = model.predict([
        home_strength_data, 
        away_strength_data,
        home_form_data, 
        away_form_data
    ])
    return val_preds


from django.db import models

class MatchResult(models.Model):
    matchDate = models.DateField()
    team1ID = models.IntegerField()
    team2ID = models.IntegerField()
    id = models.IntegerField(primary_key=True)
    team1IsHome = models.BooleanField()
    completed = models.BooleanField()

    class Meta:
        db_table = "match_results"
        managed = False

class BookOdds(models.Model):
    id = models.IntegerField(primary_key=True)
    home_win = models.FloatField()
    draw = models.FloatField()
    away_win = models.FloatField()

    class Meta:
        db_table = "book_odds"
        managed = False


class NetworkInputs(models.Model):
    id = models.IntegerField(primary_key=True)
    index_0 = models.FloatField()
    index_1 = models.FloatField()
    index_2 = models.FloatField()
    index_3 = models.FloatField()
    index_4 = models.FloatField()
    index_5 = models.FloatField()
    index_6 = models.FloatField()
    index_7 = models.FloatField()
    index_8 = models.FloatField()
    index_9 = models.FloatField()
    index_10 = models.FloatField()
    index_11 = models.FloatField()
    index_12 = models.FloatField()
    index_13 = models.FloatField()
    index_14 = models.FloatField()
    index_15 = models.FloatField()
    index_16 = models.FloatField()
    index_17 = models.FloatField()
    index_18 = models.FloatField()
    index_19 = models.FloatField()
    index_20 = models.FloatField()
    index_21 = models.FloatField()
    index_22 = models.FloatField()
    index_23 = models.FloatField()
    index_24 = models.FloatField()
    index_25 = models.FloatField()
    index_26 = models.FloatField()
    index_27 = models.FloatField()
    index_28 = models.FloatField()
    index_29 = models.FloatField()
    index_30 = models.FloatField()
    index_31 = models.FloatField()
    index_32 = models.FloatField()
    index_33 = models.FloatField()
    index_34 = models.FloatField()
    index_35 = models.FloatField()
    index_36 = models.FloatField()
    index_37 = models.FloatField()
    index_38 = models.FloatField()
    index_39 = models.FloatField()
    index_40 = models.FloatField()
    index_41 = models.FloatField()
    index_42 = models.FloatField()
    index_43 = models.FloatField()
    index_44 = models.FloatField()
    index_45 = models.FloatField()
    index_46 = models.FloatField()
    index_47 = models.FloatField()
    index_48 = models.FloatField()
    index_49 = models.FloatField()
    index_50 = models.FloatField()
    index_51 = models.FloatField()

    class Meta:
        db_table = "network_indices"
        managed = False


class FinalScores(models.Model):
    id = models.IntegerField(primary_key=True)
    home_team_score = models.IntegerField()
    away_team_score = models.IntegerField()
    match_result = models.IntegerField()
    
    class Meta:
        db_table = "match_final_scores"
        managed = False


class Predictions(models.Model):
    id = models.IntegerField(primary_key=True)
    home_team_odds = models.FloatField()
    draw_odds = models.FloatField()
    away_team_odds = models.FloatField()
    predicted_result = models.IntegerField()
    
    class Meta:
        db_table = "prediction_odds"
        managed = False
