# -*- coding: utf-8 -*-
"""
author: @lancelot
name :  app_lib.py
description : bibliothèque de fonctions pour l'application Flask de gestion des clients de Pilates
date : 2026/01/21
"""


# imports des modules
import sqlite3
from datetime import datetime


# création des fonctions utilitaires
def get_db_connection():
    """
    Fonction de connexion à la base de données.
    Appelée à chaque requête pour lire ou écrire des données.
    Args:
        None
    Returns:
        sqlite3.Connection: lien de connexion à la base de données.
    """
    # connection à la base de données
    connection = sqlite3.connect('database_clients_test.db')

    # pour accéder aux colonnes par nom et non par index
    connection.row_factory = sqlite3.Row
    return connection



def get_best_clients(since_date, until_date):
    """
    Fonction pour récupérer le meilleur client depuis une date donnée. (celui qui a utilisé le plus de séances)
    Args:
        since_date (str): date au format 'YYYY-MM-DD' pour filtrer le début des actions.
        until_date (str): date au format 'YYYY-MM-DD' pour filtrer la fin des actions.
    Returns:
        list: liste des clients avec le nombre de séances utilisées.
    """
    connection = get_db_connection()

    query = """
        SELECT c.prenom, c.nom, COUNT(h.id) AS seances_utilisees
        FROM historique_seances h
        JOIN clients c ON h.client_id = c.id
        WHERE h.action = 'CHECK-IN' 
        AND DATE(h.date_heure) BETWEEN ? AND ?
        GROUP BY c.id
        ORDER BY seances_utilisees DESC
        LIMIT 1;  
    """

    result = connection.execute(query, (since_date, until_date)).fetchone()
    connection.close()
    return result




def get_client_most_remaining():
    """
    Fonction pour récupérer le client avec le plus de séances restantes.
    Args:
        None
    Returns:
        sqlite3.Row: ligne contenant les informations du client.
    """
    connection = get_db_connection()

    query = """
        SELECT prenom, nom, seances_restantes
        FROM clients
        ORDER BY seances_restantes DESC
        LIMIT 1;
    """

    result = connection.execute(query).fetchone()
    connection.close()
    return result




def get_number_seances(since_date, until_date, time_space_minutes=120):
    """
    Fonction pour récupérer le nombre total de séances donnée par le prof depuis une date donnée.
    En partant du principe qu'une séance est enregistrée par une action 'CHECK-IN' des participants.
    Et que plusieurs CHECK-IN espacé de moins de time_space_minutes minutes correspondent à la même séance.
    Args:
        since_date (str): date au format 'YYYY-MM-DD' pour filtrer le début des actions.
        until_date (str): date au format 'YYYY-MM-DD' pour filtrer la fin des actions.
        time_space_minutes (int): intervalle de temps en minutes pour regrouper les CHECK-IN dans une même séance.
    Returns:
        int: nombre total de séances.
    """
    connection = get_db_connection()

    query = """
        SELECT date_heure
        FROM historique_seances
        WHERE action = 'CHECK-IN'
        AND DATE(date_heure) BETWEEN ? AND ?
        ORDER BY date_heure ASC;
    """

    rows = connection.execute(query, (since_date, until_date)).fetchall()
    connection.close()

    if not rows:
        return 0

    # Regroupement des CHECK-IN en séances
    seances = []
    current_seance_start = datetime.strptime(rows[0]['date_heure'], '%Y-%m-%d %H:%M:%S')

    for row in rows[1:]:
        check_in_time = datetime.strptime(row['date_heure'], '%Y-%m-%d %H:%M:%S')
        delta_minutes = (check_in_time - current_seance_start).total_seconds() / 60

        if delta_minutes > time_space_minutes:
            seances.append(current_seance_start)
            current_seance_start = check_in_time

    # Ajouter la dernière séance
    seances.append(current_seance_start)
    return len(seances)