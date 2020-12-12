# Itineraires intelligents
Auteurs: **Morgan Fassier** & **Fabrice Pont**
## Introduction
Ce programme a été réalisé pour illustrer un travail réalisé sur les réseaux de transports français (avion, bus, TER, TGV, intercités). Nous avons essayé de récupérer différentes bases de données nous indiquant les trajets entre différentes villes (les données ne sont pas récupéré en temps réel) ainsi que diverses caractéristiques :
- Prix
- Empreinte carbone
- Temps
- Distance

Nous voulons permettre à l'utilisateur de trouver le trajet le plus optimal pour lui en fonction de ses préférences sur les 4 points ci-dessus.

## Prérequis
- Python 3.8+
- Les packages suivants : **flask**, **numpy**, **networkx**, **requests**
- Une connexion internet

## Utilisation

Afin de pouvoir utiliser l'application veuillez lancer le programme **run** de l'archive *webapp* :
```
python3 webapp/run.py
```
Enfin, connectez-vous à l'adresse suivante: **http://127.0.0.1:8000/**.

Vous remarquerez alors **4 curseurs** sur l'application qui vous permettront de gérer vos préférences entre 1 (peu d'importance si élevé) et 10 (contraignant si élevé) :
- Distance : nombre de km parcourus
- Ecologie : émissions de CO2 engendrées
- Temps : temps consacré
- Prix : argent dépensé

Ces indicateurs représentent des préférences et nous permettent de mettre à jour les poids de notre carte afin de trouver le trajet optimal dans ce cas.

Vous pouvez ensuite rentrer 2 adresses (ville, adresse précise) et calculer le trajet. Celui-ci s'affichera sur la carte et vous verrez votre le calcul total de votre empreinte carbone, votre temps, votre prix et enfin votre distance parcourue.


## Limites
Notre programme présente certaines limites:
- Toutes les jonctions entre les différents transports se font à pieds ce qui donne parfois des résultats très bizarres
- Nous ne prenons pas en compte les transports en commun des villes ou les voitures
- Les trajets entre deux gares, arrêts de bus, ou autre, se font en ligne droite donc les tracés ne correspondents pas parfaitement au trajet emprunté
- On ne considère pas les temps d'attentes entre deux transports

## Contenu de l'archive
Cette archive contient 2 dossiers:
- *webapp* : contient l'application Web qui permet d'illustrer notre projet
- *data* : contient tous les codes de nettoyage et traitement des données, les données nettoyées et traitées ainsi que les liens vers les données brutes utilisées
