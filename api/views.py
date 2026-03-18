from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .constants import SEASONS
from .helper_functions.standardize_season_data import get_network_data
from .helper_functions.network_results_helpers import convert_lambdas_to_predictions_and_results
import numpy as np


from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import MatchResult, FinalScores, BookOdds, Predictions, predict, model
from .serializers import PredictionsSerializer, MatchResultSerializer, BookOddsSerializer, NetworkInputsSerializer, FinalScoresSerializer

class PredictView(APIView):
    def get(self, request):
        input_data = request.data.get('input')  # Expect JSON {"input": [...]}

        if input_data is None:
            input_data_again = request.data.get('inputs')  # Expect JSON {"input": [...]}
            if input_data_again is None:
                return Response({'error': 'No input data provided'}, status=status.HTTP_400_BAD_REQUEST)
            home_str = input_data_again[0]
            away_str = input_data_again[1]
            home_frm = input_data_again[2]
            away_frm = input_data_again[3]
        else:
            home_str = [input_data[0]]
            away_str = [input_data[1]]
            home_frm = [input_data[2]]
            away_frm = [input_data[3]]
        try:
            home_strength = np.array(home_str, dtype=np.float32)
            away_strength = np.array(away_str, dtype=np.float32)
            home_form = np.array(home_frm, dtype=np.float32)
            away_form = np.array(away_frm, dtype=np.float32)

            prediction = predict(
                home_strength,
                away_strength,
                home_form,
                away_form
            )

            return Response({'predictions': prediction.tolist()}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        input_data = request.data.get('input')  # Expect JSON {"input": [...]}

        if input_data is None:
            input_data_again = request.data.get('inputs')  # Expect JSON {"input": [...]}
            if input_data_again is None:
                return Response({'error': 'No input data provided'}, status=status.HTTP_400_BAD_REQUEST)
            home_str = input_data_again[0]
            away_str = input_data_again[1]
            home_frm = input_data_again[2]
            away_frm = input_data_again[3]
        else:
            home_str = [input_data[0]]
            away_str = [input_data[1]]
            home_frm = [input_data[2]]
            away_frm = [input_data[3]]
        try:
            home_strength = np.array(home_str, dtype=np.float32)
            away_strength = np.array(away_str, dtype=np.float32)
            home_form = np.array(home_frm, dtype=np.float32)
            away_form = np.array(away_frm, dtype=np.float32)

            prediction = predict(
                home_strength,
                away_strength,
                home_form,
                away_form
            )

            return Response({'predictions': prediction.tolist()}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetNetworkDataView(APIView):
    def get(self, request):
        try:
            
            laliga_network_data, laliga_network_inputs, laliga_network_labels = get_network_data(87, [2025])
            ligue1_network_data, ligue1_network_inputs, ligue1_network_labels = get_network_data(53, [2025])
            bundesliga_network_data, bundesliga_network_inputs, bundesliga_network_labels = get_network_data(54, [2025])
            seriea_network_data, seriea_network_inputs, seriea_network_labels = get_network_data(55, [2025])

            home_strength_data = np.vstack([
                laliga_network_inputs[:, 0, :],
                bundesliga_network_inputs[:, 0, :],
                seriea_network_inputs[:, 0, :],
                ligue1_network_inputs[:, 0, :],
            ])
            away_strength_data = np.vstack([
                laliga_network_inputs[:, 1, :],
                bundesliga_network_inputs[:, 1, :],
                seriea_network_inputs[:, 1, :],
                ligue1_network_inputs[:, 1, :],
            ])
            home_form_data = np.vstack([
                laliga_network_inputs[:, 2, :],
                bundesliga_network_inputs[:, 2, :],
                seriea_network_inputs[:, 2, :],
                ligue1_network_inputs[:, 2, :],
            ])
            away_form_data = np.vstack([
                laliga_network_inputs[:, 3, :],
                bundesliga_network_inputs[:, 3, :],
                seriea_network_inputs[:, 3, :],
                ligue1_network_inputs[:, 3, :],
            ])
            all_leagues_labels = np.vstack([
                laliga_network_labels,
                bundesliga_network_labels,
                seriea_network_labels,
                ligue1_network_labels,
            ])

            network_data = np.vstack((
                laliga_network_data,
                bundesliga_network_data,
                seriea_network_data,
                ligue1_network_data,
                #prem_network_data,
                #championship_network_data
            ))


            test_val_preds = model.predict([home_strength_data, away_strength_data, home_form_data, away_form_data])
            predicted_odds, match_predictions_from_odds, correct_guesses,actual_result_labels = convert_lambdas_to_predictions_and_results(test_val_preds, all_leagues_labels, draw_threshold=0.27)

            return Response({
                'network_data': network_data.tolist(), 
                'network_inputs': [
                    home_strength_data.tolist(), 
                    away_strength_data.tolist(), 
                    home_form_data.tolist(), 
                    away_form_data.tolist()
                ],
                'labels': all_leagues_labels.tolist(),
                'predicted_odds': predicted_odds, 
                'match_predictions_from_odds': match_predictions_from_odds,
                'correct_guesses': correct_guesses
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetNetworkInputsView(APIView):
    def post(self, request):
        data = request.data

        # Normalize input shape
        items = data["inputs"] if "inputs" in data else [data]

        normalized_items = []
        for item in items:
            item_obj = {
                "id": item["id"],
                **{
                    f"index_{c}": item[f"index_{c}"]
                    for c in range(len(item) - 1)
                }
            }
            normalized_items.append(item_obj)

        created = []
        skipped = []

        for item in normalized_items:
            serializer = NetworkInputsSerializer(data=item)

            if not serializer.is_valid():
                skipped.append({"item": item, "error": serializer.errors})
                continue

            try:
                obj = serializer.save()
                created.append(NetworkInputsSerializer(obj).data)

            except Exception:
                skipped.append({"item": item, "reason": "duplicate primary key"})
                continue

        return Response(
            {
                "created": created,
                "skipped": skipped,
            },
            status=status.HTTP_201_CREATED,
        )
    
class GetFinalScoresView(APIView):
    def post(self, request):
        data = request.data

        # Normalize input shape
        items = data["scores"] if "scores" in data else [data]

        normalized_items = []
        for item in items:
            normalized_items.append({
                "id": item["id"],
                "home_team_score": item["home_team_score"],
                "away_team_score": item["away_team_score"],
                "match_result": item["match_result"],
            })

        created = []
        updated = []
        skipped = []

        for item in normalized_items:
            match_id = item["id"]

            # Try to fetch existing row
            try:
                instance = FinalScores.objects.get(id=match_id)
                # Update mode
                serializer = FinalScoresSerializer(instance, data=item, partial=True)
                action = "updated"
            except FinalScores.DoesNotExist:
                # Create mode
                serializer = FinalScoresSerializer(data=item)
                action = "created"

            if not serializer.is_valid():
                skipped.append({"item": item, "error": serializer.errors})
                continue

            obj = serializer.save()

            if action == "created":
                created.append(FinalScoresSerializer(obj).data)
            else:
                updated.append(FinalScoresSerializer(obj).data)

        return Response(
            {
                "created": created,
                "updated": updated,
                "skipped": skipped,
            },
            status=status.HTTP_200_OK,
        )

class GetPredictionsView(APIView):
    def post(self, request):
        data = request.data

        # Normalize input shape
        items = data["predictions"] if "predictions" in data else [data]
        normalized_items = []
        for item in items:
            print(item)
            item_obj = {
                "id": item["id"],
                "home_team_odds": item["home_team_odds"],
                "draw_odds": item["draw_odds"],
                "away_team_odds": item["away_team_odds"],
                "predicted_result": item["predicted_result"]
            }
            normalized_items.append(item_obj)

        created = []
        skipped = []

        for item in normalized_items:
            serializer = PredictionsSerializer(data=item)

            if not serializer.is_valid():
                # If one row is bad, skip it but continue processing others
                skipped.append({"item": item, "error": serializer.errors})
                continue

            try:
                # Try to create the row
                obj = serializer.save()
                created.append(PredictionsSerializer(obj).data)

            except Exception:
                # Most likely IntegrityError: duplicate primary key
                skipped.append({"item": item, "reason": "duplicate primary key"})
                continue

        return Response(
            {
                "created": created,
                "skipped": skipped,
            },
            status=status.HTTP_201_CREATED,
        )
    

    #match_final_scores

class TeamMatchesView(APIView):
    def get(self, request):
        try:
            # Query match results
            results = MatchResult.objects.all()

            # Query match stats
            stats = FinalScores.objects.all()

            book_odds = BookOdds.objects.all()

            predictions = Predictions.objects.all()

            # Build lookup dictionary for stats keyed by composite PK
            stats_lookup = {
                s.id: s
                for s in stats
            }
            book_odds_lookup = {
                b.id: b
                for b in book_odds
            }
            predictions_odds_lookup = {
                p.id: p
                for p in predictions
            }
            merged = []

            for r in results:
                key = r.id
                team1ID = r.team1ID if r.team1IsHome else r.team2ID
                team2ID = r.team2ID if r.team1IsHome else r.team1ID

                # If no final score → return partial matchInfo only
                if key not in stats_lookup:
                    merged.append({
                        "id": r.id,
                        "matchInfo": {
                            "matchDate": r.matchDate,
                            "team1ID": team1ID,
                            "team2ID": team2ID,
                            "completed": r.completed if r.completed is not None else True
                        }
                    })
                    continue

                s = stats_lookup[key]
                b = book_odds_lookup.get(key)
                p = predictions_odds_lookup.get(key)

                merged_item = {
                    "id": r.id,
                    "matchInfo": {
                        "matchDate": r.matchDate,
                        "team1ID": team1ID,
                        "team2ID": team2ID,
                        "completed": r.completed if r.completed is not None else True
                    },
                    "finalScore": {
                        "home": s.home_team_score,
                        "away": s.away_team_score,
                        "matchResult": s.match_result
                    }
                }

                # Add book odds only if present
                if b:
                    merged_item["bookOdds"] = {
                        "home": b.home_win,
                        "draw": b.draw,
                        "away": b.away_win
                    }

                # Add predictions only if present
                if p:
                    merged_item["predicted"] = {
                        "home": p.home_team_odds,
                        "draw": p.draw_odds,
                        "away": p.away_team_odds,
                        "predictedResult": p.predicted_result
                    }

                merged.append(merged_item)

            return Response(merged)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        data = request.data
        items = data["matches"] if "matches" in data else [data]

        updated = []
        created = []
        skipped = []

        for item in items:
            match_id = item.get("id")
            team1 = item.get("team1ID")
            team2 = item.get("team2ID")
            date  = item.get("matchDate")

            instance = None

            # 1. Try lookup by ID
            if match_id:
                instance = MatchResult.objects.filter(id=match_id).first()

            # 2. Try lookup by composite key
            if instance is None and team1 and team2 and date:
                instance = MatchResult.objects.filter(
                    team1ID=team1,
                    team2ID=team2,
                    matchDate=date
                ).first()

            # 3. Try lookup by reversed composite key
            if instance is None and team1 and team2 and date:
                instance = MatchResult.objects.filter(
                    team1ID=team2,
                    team2ID=team1,
                    matchDate=date
                ).first()

            # 4. If found → update
            if instance:
                # Prevent primary key overwrite
                item.pop("id", None)

                serializer = MatchResultSerializer(instance, data=item, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated.append(serializer.data)
                else:
                    skipped.append({"item": item, "error": serializer.errors})
                continue

            # 5. If not found → create
            serializer = MatchResultSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
            else:
                skipped.append({"item": item, "error": serializer.errors})

        return Response(
            {
                "updated": updated,
                "created": created,
                "skipped": skipped,
            },
            status=status.HTTP_200_OK,
        )

class CreateBookOddsView(APIView):
    def post(self, request):
        data = request.data

        # Normalize input shape
        items = data["odds"] if "odds" in data else [data]

        created = []
        skipped = []

        for item in items:
            serializer = BookOddsSerializer(data=item)

            if not serializer.is_valid():
                # If one row is bad, skip it but continue processing others
                skipped.append({"item": item, "error": serializer.errors})
                continue

            try:
                # Try to create the row
                obj = serializer.save()
                created.append(BookOddsSerializer(obj).data)

            except Exception:
                # Most likely IntegrityError: duplicate primary key
                skipped.append({"item": item, "reason": "duplicate primary key"})
                continue

        return Response(
            {
                "created": created,
                "skipped": skipped,
            },
            status=status.HTTP_201_CREATED,
        )