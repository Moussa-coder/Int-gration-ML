from django.urls import path
from .views import HistoriqueView, PredictView, index

urlpatterns = [
    path('', index, name='index'),               # Page web
    path('predict/', PredictView.as_view()),     # API JSON
    path('historique/', HistoriqueView.as_view()),
]
