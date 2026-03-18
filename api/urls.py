from django.urls import path
from .views import GetPredictionsView, GetFinalScoresView, GetNetworkInputsView, CreateBookOddsView, GetNetworkDataView, PredictView, TeamMatchesView

urlpatterns = [
    path('predict/', PredictView.as_view(), name='predict'),
    path('network_data/', GetNetworkDataView.as_view(), name='network_data'),
    path("matches/", TeamMatchesView.as_view()),
    path("book_odds/", CreateBookOddsView.as_view()),
    path("network_inputs/", GetNetworkInputsView.as_view()),
    path("final_score/", GetFinalScoresView.as_view()),
    path("predictions/", GetPredictionsView.as_view()),
]
