# -*- coding: utf-8 -*-
"""
author: @lancelot
name : app.py
description : 
date : 2026/01/20
"""

# imports des modules
import sqlite3
from flask import Flask, render_template

# création de l'application Flask
app = Flask(__name__) # création du site web

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
    connection = sqlite3.connect('database_clients.db')

    # pour accéder aux colonnes par nom et non par index
    connection.row_factory = sqlite3.Row
    return connection


# création des routes pour le site web (pages)
@app.route('/')
def index():
    """
    Fonction exécutée lors de l'accès à la page d'accueil ('/').
    Args:
        None
    Returns:
        str: rendu HTML de la page d'accueil.
    """
    # connexion à la base de données
    connection = get_db_connection()

    # requête SQL pour récupérer tous les clients de la table 'clients'
    clients = connection.execute('SELECT * FROM clients').fetchall()

    # fermeture de la connexion à la base de données
    connection.close()

    # envoi des données à la page HTML index.html
    return render_template('index.html', clients=clients)

# lancement de l'application Flask
if __name__ == '__main__':
    app.run(debug=True)