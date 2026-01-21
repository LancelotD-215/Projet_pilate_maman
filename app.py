# -*- coding: utf-8 -*-
"""
author: @lancelot
name : app.py
description : 
date : 2026/01/20
"""

# imports des modules
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

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


@app.route('/presence', methods=['GET', 'POST']) # pour accepter les requêtes GET et POST
def presence():
    """
    Fonction exécutée lors de l'accès à la page '/presence'.
    Args:
        None
    Returns:
        str: rendu HTML de la page de présence.
    """
    # connexion à la base de données
    connection = get_db_connection()

    if request.method == "POST": # si l'utilisateur a soumis le formulaire (POST)
        # récupération de l'ID du client depuis le formulaire
        prenom = request.form['prenom']
        nom = request.form['nom']

        # nettoyage des entrées
        prenom = prenom.strip().title()
        nom = nom.strip().title() 

        # recherche du client dans la base de données
        client = connection.execute('SELECT * FROM clients WHERE prenom = ? AND nom = ?', (prenom, nom)).fetchone()
        
        if client:
            # récupération de l'ID du client
            client_id = client['id']

            # mise à jour de la présence du client dans la base de données
            connection.execute('UPDATE clients SET seances_restantes = seances_restantes - 1 WHERE id = ?', (client_id,))

            # ajout dans historique seances
            connection.execute('INSERT INTO historique_seances (client_id, action, nombre) VALUES (?, ?, ?)', (client_id, "utilisation", -1))

            # commit des changements
            connection.commit() 
            connection.close()

            # renvoie l'utilisateur vers l'accueil
            return redirect(url_for('index'))
        
        else:
            # client non trouvé
            connection.close()
            return (f"<h1>Erreur : Le client '{prenom} {nom}' est introuvable.</h1><p>Vérifiez l'orthographe et réessayez.</p><a href='/presence'>Réessayer</a>")

    if request.method == "GET" :
        # affichage de la liste des clients
        clients = connection.execute('SELECT * FROM clients').fetchall()
        connection.close()
        return render_template('presence.html', clients=clients)


@app.route('/ajout_client', methods=['GET', 'POST'])
def ajout_client():
    """
    Fonction exécutée lors de l'accès à la page '/ajout_client'.
    Args:
        None
    Returns:
        str: rendu HTML de la page d'ajout de client.
    """
    # connexion à la base de données
    connection = get_db_connection()
    
    if request.method == "POST": # si l'utilisateur a soumis le formulaire (POST)
        # récupération des données du formulaire
        prenom = request.form['prenom'].strip().title()
        nom = request.form['nom'].strip().title() 
        seances_initiales = int(request.form['seances_initiales'])

        # vérification si le client existe déjà
        existing_client = connection.execute('SELECT * FROM clients WHERE prenom = ? AND nom = ?', (prenom, nom)).fetchone()

        if existing_client:
            connection.close()
            return (f"<h1>Erreur : Le client '{prenom} {nom}' existe déjà.</h1><p>Veuillez vérifier les informations et réessayer.</p><a href='/ajout_client'>Réessayer</a>")
        
        else:
            # curseur pour récupérer l'ID du nouveau client
            curseur = connection.execute('INSERT INTO clients (prenom, nom, seances_restantes) VALUES (?, ?, ?)',(prenom, nom, seances_initiales))
            
            # récupération de l'ID du nouveau client
            nouveau_client_id = curseur.lastrowid

            # ajout dans historique seances
            connection.execute('INSERT INTO historique_seances (client_id, action, nombre) VALUES (?, ?, ?)',(nouveau_client_id, 'CREATION_COMPTE', seances_initiales))

            # commit des changements
            connection.commit() 
            connection.close()

            # renvoie de l'utilisateur vers l'accueil
            return redirect(url_for('index'))

    if request.method == "GET" :
        connection.close()
        # affichage du formulaire d'ajout de client
        return render_template('ajout_client.html')



# lancement de l'application Flask
if __name__ == '__main__':
    app.run(debug=True)