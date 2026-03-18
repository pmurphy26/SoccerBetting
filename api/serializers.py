from rest_framework import serializers
from .models import MatchResult, BookOdds, FinalScores, Predictions, NetworkInputs

class MatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchResult
        fields = "__all__"

class BookOddsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookOdds
        fields = "__all__"

class NetworkInputsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkInputs
        fields = "__all__"

class FinalScoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalScores
        fields = "__all__"

class PredictionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Predictions
        fields = "__all__"
