# predictor/views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import joblib
import pandas as pd
import os

# Charger les modèles et l’encodeur
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_rec = joblib.load(os.path.join(BASE_DIR, "model_recettes.pkl"))
model_dep = joblib.load(os.path.join(BASE_DIR, "model_depenses.pkl"))
le = joblib.load(os.path.join(BASE_DIR, "label_encoder.pkl"))

class PredictView(APIView):
    def post(self, request):
        try:
            commune = request.data.get("commune")
            annee = int(request.data.get("annee"))

            # Encode la commune
            if commune not in le.classes_:
                return Response({"error": "Commune inconnue"}, status=status.HTTP_400_BAD_REQUEST)

            commune_enc = le.transform([commune])[0]
            X = pd.DataFrame([[annee, commune_enc]], columns=["Année", "Commune_enc"])

            # Prédictions
            recettes = model_rec.predict(X)[0]
            depenses = model_dep.predict(X)[0]

            return Response({
                "recettes": round(recettes, 2),
                "depenses": round(depenses, 2)
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def index(request):
    return render(request, "predictor/index.html")

# Charge les données historiques nettoyées
df = pd.read_csv(os.path.join(BASE_DIR, "donnees_communes_clean.csv"))

class HistoriqueView(APIView):
    def post(self, request):
        commune = request.data.get("commune")
        annee_future = int(request.data.get("annee"))

        if commune not in df["Commune"].unique():
            return Response({"error": "Commune inconnue"}, status=400)

        historique = df[df["Commune"] == commune].sort_values("Année")
        annees = historique["Année"].tolist()
        recettes = historique["Recettes"].tolist()
        depenses = historique["Dépenses"].tolist()

        # Ajoute la prédiction future
        commune_enc = le.transform([commune])[0]
        X_future = pd.DataFrame([[annee_future, commune_enc]], columns=["Année", "Commune_enc"])
        recettes.append(model_rec.predict(X_future)[0])
        depenses.append(model_dep.predict(X_future)[0])
        annees.append(annee_future)

        return Response({
            "annees": annees,
            "recettes": recettes,
            "depenses": depenses
        })

