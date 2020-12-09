import networkx as nx
import math
import json
import os
from pathlib import Path




def mins_maxs(edges_data: list) -> list:
    """
    Calcul les attributs minimums et maximums des edges (on ne s'intéresse pas à l'attribut "transport")
    """
    maxs, mins = {}, {}
    for attrib in edges_data:
        for key, value in attrib[2].items():
            if value != str(value):
                if maxs.get(key, 0) < value:
                    maxs[key] = value
                if mins.get(key, 1e12) > value:
                    mins[key] = value
    return [maxs, mins]


def put_weight(G: object, duree: int, distance: int, empreinte_carbone: int, prix: int) -> object:
    """
    Définit les poids des arrêtes du graph G par rapport aux 4 attributs qui nous intéressent
    """
    maxs, mins = mins_maxs(list(G.edges.data()))
    for edge in G.edges():
        attribs = list(G.get_edge_data(*edge).values())
        
        # on fait coef_duree*(t - t_min)/(t_max - t_min) et de même pour les autres attributs .. à changer ?
        weight = duree*(attribs[0]-mins["duree"])/(maxs["duree"]-mins["duree"]) + \
                 distance*(attribs[1]-mins["distance"])/(maxs["distance"]-mins["distance"]) + \
                 empreinte_carbone*(attribs[2]-mins["empreinte_carbone"])/(maxs["empreinte_carbone"]-
                                                                           mins["empreinte_carbone"]) + \
                 prix*(attribs[3]-mins["prix"])/(maxs["prix"]-mins["prix"])
        
        # on divise le poids par la somme des coef
        G[edge[0]][edge[1]]['weight'] = weight/(duree + distance + empreinte_carbone + prix)
    return G


def ecart(lat_i: float, lat_f: float, long_i: float, long_f: float):
    """
    Calcul de la distance entre deux points gps par la formule de Haversine
    """
    r = 6378
    lat_i, long_i = math.radians(lat_i), math.radians(long_i)
    lat_f, long_f = math.radians(lat_f), math.radians(long_f)
    return 2*r*math.asin(math.sqrt(math.sin((lat_i - lat_f)/2)**2 + math.cos(lat_i)*
                                   math.cos(lat_f)*math.sin((long_i-long_f)/2)**2))

def shortest_path(G_i: object, pt1: tuple, pt2: tuple, rel: dict, n1: int=10, n2: int=10, \
                  funct: object=nx.dijkstra_path, duree: int=10, distance: int=1, empreinte_carbone: int=1, \
                  prix: int=1)-> dict:
    """
    FONCTION A UTILISER !
    G_i -> Graph à utiliser
    pt1, pt2 -> point gps (lat, long) du point de départ et d'arrivée
    rel -> relations entre les numéros des noeuds et les noms des points
    n1, n2 (défaut 10, 10) -> nombre de noeuds de transport les plus proches de pt1, pt2
    funct (défaut nx.dijkstra_path) -> fonction pour le plus court chemin. Il y a également nx.shortest_path, etc ?
    duree (défaut 10) -> coef de poids pour la durée entre 1 et 10
    distance (défaut 1) -> coef de poids pour la distance entre 1 et 10
    empreinte_carbone (défaut 1) -> coef de poids pour la empreinte_carbone entre 1 et 10
    prix (défaut 1) -> coef de poids pour la prix entre 1 et 10
    """
    
    def f_1(dict_sorted: dict, n: int):
        """
        Regarde si il n'y a pas le n-ème noeud qui a la même position que le n+i_ème, etc.. si oui on prend n+i
        """
        count, condition = 0, 0
        while count < n or condition == 0:
            try:
                if list(dict_sorted.values())[count + 1] != list(dict_sorted.values())[count]:
                    condition = 1
                else:
                    condition = 0
            except Exception:
                pass
            count += 1
        return count
    
    def f_2(G: object, count: int, dict_sorted: dict, pt: tuple, name_pt: str):
        """
        Ajoute count edge pour départ/arrivée
        """
        for i in range(count): 
            pt_proche = list(dict_sorted.keys())[i]
            dist = ecart(pt[0], dict_sorted[pt_proche]["latitude"], pt[1], dict_sorted[pt_proche]["longitude"])
            t = 60*dist/3.0 # on par du principe qu'une personne marche à 3km/h (vol d'oiseau)
            weight = duree*(t-mins["duree"])/(maxs["duree"]-mins["duree"]) + \
                     distance*(dist-mins["distance"])/(maxs["distance"]-mins["distance"])
            if weight < 0:
                weight = 0
            G.add_edge(name_pt, pt_proche, duree=round(t, 2), distance=round(dist, 3), empreinte_carbone=0.0, 
                       prix=0.0, transport="marche", weight=weight/(duree + distance + empreinte_carbone + prix))
        return G
    
    G = G_i.copy()
    
    # on met les poids
    G = put_weight(G, duree, distance, empreinte_carbone, prix)
    
    # on ajoute les noeuds départ et arrivée (qui seront donc fait à la marche)
    G.add_node("point depart", latitude=pt1[0], longitude=pt1[1])
    G.add_node("point arrivee", latitude=pt2[0], longitude=pt2[1])
    
    # on va prendre les dep, fin (n1, n2 ou plus si même position) plus proches noeuds de respectivement pt1, pt2
    dic_nodes = dict(G.nodes.data())
    dep_sorted = {k: v for k, v in sorted(dic_nodes.items(), key=lambda x: ecart(list(x[1].values())[0], pt1[0], 
                                                                                 list(x[1].values())[1], pt1[1]))}
    fin_sorted = {k: v for k, v in sorted(dic_nodes.items(), key=lambda x: ecart(list(x[1].values())[0], pt2[0], 
                                                                                 list(x[1].values())[1], pt2[1]))}
    if n1 < 2: # on fixe au minimum n1 ou n2 a 2 (car le premier edge c'est du noeud vers lui même ..)
        n1 = 2
    if n2 < 2:
        n2 = 2
    dep = f_1(dep_sorted, n1)
    fin = f_1(fin_sorted, n2)

    # ajoute edges liés au n1 et n2 plus proches noeuds par rapport à départ et arrivée
    maxs, mins = mins_maxs(list(G.edges.data()))
    G = f_2(G, dep, dep_sorted, pt1, "point depart")
    G = f_2(G, fin, fin_sorted, pt2, "point arrivee")

    # plus cours chemin (liste des noeuds)
    path = {}
    path_value =  funct(G, "point depart", "point arrivee", weight="weight")
    caract_value = []
    for i in range(1, len(path_value)):
        caract_value.append(G[path_value[i-1]][path_value[i]])
    path[tuple(path_value)] = caract_value
    
    # caractéristiques totales du trajet (juste pour le print des caracts)
    caract_tot = {}
    for value in list(path.values())[0]:
        for key, value_bis in value.items():
            if value_bis != str(value_bis):
                caract_tot[key] = caract_tot.get(key, 0) + value_bis
    print(f"Noeuds définissant le chemin : {list(path.keys())[0]}\n\nCaractéristiques du trajet :")
    for key, value, item, arrondi in zip(caract_tot.keys(), caract_tot.values(), 
                                                          ["minutes", "km", "gCO2", "euros", ""], [2, 3, 1, 2, 3]):
        print(f"\n--> {key} : {round(value, arrondi)} {item}")
    
    # dictionnaire à retourner pour le site web !
    result = {}
    for key in list(path.keys())[0]:
        if key == "point depart":
            result["points"] = result.get("points", []) + [list(pt1)]
            result["nom points"] = result.get("nom points", []) + ["point depart"]
        elif key == "point arrivee":
            result["points"] = result.get("points", []) + [list(pt2)]
            result["nom points"] = result.get("nom points", []) + ["point arrivee"]
        else:
            result["points"] = result.get("points", []) + [list(G.nodes[key].values())]
            result["nom points"] = result.get("nom points", []) + [rel[str(key)]]
    for value in list(path.values())[0]:
        for attrib in ["duree", "distance", "empreinte_carbone", "prix", "transport"]:
            result[attrib] = result.get(attrib, []) + [value[attrib]]
    return result


def compute_path(depart: tuple, arrivee: tuple, duree: int=10, distance: int=1, empreinte_carbone: int=1, \
                  prix: int=1):
    """ Méthode permettant de lancer le calcul du trajet """
    os.chdir(Path(__file__).parent)
    G = nx.read_gpickle("data/graph") # chemin vers fichier "graph" (créé dans le graph.ipynb)

    with open('data/rel', 'r') as in_f: # chemin vers fichier "rel" (créé dans le graph.ipynb)
        rel = json.load(in_f)

    result = shortest_path(G, depart, arrivee, rel)
    return result