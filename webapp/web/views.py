from flask import Flask, render_template, request, redirect
import numpy as np
from itertools import groupby
from .backend import compute_path
import requests
from urllib.parse import quote
import json as j

app = Flask(__name__)

@app.route('/')
def index():
    json = {}
    return render_template('index.html', **locals())


@app.route('/', methods=['POST'])
def compute_trajet():
    # Récupération des coordonnées des adresses
    from_url = "https://api-adresse.data.gouv.fr/search/?q=" + quote(request.form["adress-from"]) + "&type=&autocomplete=1"
    to_url = "https://api-adresse.data.gouv.fr/search/?q=" + quote(request.form["adress-to"]) + "&type=&autocomplete=1"
    fr = j.loads(requests.get(from_url).content.decode())["features"][0]["geometry"]["coordinates"]
    to = j.loads(requests.get(to_url).content.decode())["features"][0]["geometry"]["coordinates"]

    # Données du formulaire
    s_distance = int(request.form["score-distance"])
    s_temps = int(request.form["score-temps"])
    s_ecologie = int(request.form["score-ecologie"])
    s_prix = int(request.form["score-prix"])
    depart = (float(fr[1]), float(fr[0]))
    arrivee = (float(to[1]), float(to[0]))
    print(fr, to)
    # Calcul du plus court chemin
    data = compute_path(depart, arrivee, duree=s_temps, distance=s_distance, empreinte_carbone=s_ecologie, prix=s_prix)
    
    # Création des données pour l'affichage du trajet
    colors = {"ter": "green", "marche": "black", "tgv": "red", "bus": "yellow", "avion": "white", "intercites": "blue"}
    types = [(e[0], len(list(e[1]))) for e in groupby(data["transport"])]
    index = [0] + list(np.cumsum([e[1] for e in types]))
    index[-1] += 1
    json = {}
    for idx, elem in enumerate(types):
        color = colors[elem[0]]
        d = round(sum(data["duree"][index[idx]: index[idx + 1]]), 2)
        p = data["points"][index[idx]: index[idx + 1]]
        c = round(sum(data["empreinte_carbone"][index[idx]: index[idx + 1]]))
        # On doit rajouter le premier point du nouveau trajet au dernier trajet pour les relier
        if idx != 0:
            json[idx-1]["points"] += [p[0]]
        json[idx] = {"points": p, "duree": d, "co2": c, "color": color, "type": elem[0]}
    

    # Formatage du trajet
    trajets = [{"co2": json[e]["co2"], "temps": json[e]["duree"], "type": json[e]["type"]} for e in json]

    # Calcul des valeurs totales
    temps_total = round(sum(data["duree"]), 2)
    distance_totale = round(sum(data["distance"]), 2)
    co2_total = round(sum(data["empreinte_carbone"]))
    prix_total = round(sum(data["prix"]), 2)

    return render_template('index.html', **locals())
