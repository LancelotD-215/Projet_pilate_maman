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



def get_best_clients(since_date):
    """
    Fonction pour récupérer le meilleur client depuis une date donnée. (celui qui a utilisé le plus de séances)
    Args:
        since_date (str): date au format 'YYYY-MM-DD' pour filtrer les actions.
    Returns:
        list: liste des clients avec le nombre de séances utilisées.
    """
    connection = get_db_connection()

    actual_date = datetime.now().strftime('%Y-%m-%d') # date actuelle au format 'YYYY-MM-DD'
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

    result = connection.execute(query, (since_date, actual_date)).fetchone()
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