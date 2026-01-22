# -*- coding: utf-8 -*-
"""
author: @lancelot
name : app.py
description : code principal de l'application Flask pour la gestion des clients de Pilates
date : 2026/01/20
"""

# imports des modules
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from app_lib import get_db_connection, get_best_clients, get_client_most_remaining, get_number_seances

# création de l'application Flask
app = Flask(__name__) # création du site web




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

    # CONFIGURATION DES WIDGETS
    widgets_config = {
        'best_client_month': True,
        'best_client_all_time': False,
        'most_remaining': True,
        'total_clients': True,
        'seances_month': True
    }

    # initialisation des données des widgets
    best_clients_month = None
    best_clients_all_time = None
    client_most_remaining = None
    total_clients = None
    number_seances_month = None

    # récupération des variables
    actual_date = datetime.now().strftime('%Y-%m-%d')
    first_day_of_month = actual_date[:8] + '01' # premier jour du mois courant

    # création des données pour les widgets
    if widgets_config['best_client_month']:
        best_clients_month = get_best_clients(first_day_of_month, actual_date) # du mois courant
    if widgets_config['best_client_all_time']:
        best_clients_all_time = get_best_clients('2000-01-01', actual_date) # depuis le début
    if widgets_config['most_remaining']:
        client_most_remaining = get_client_most_remaining()
    if widgets_config['total_clients']:
        total_clients = connection.execute('SELECT COUNT(*) AS total FROM clients').fetchone()['total']
    if widgets_config['seances_month']:
        number_seances_month = get_number_seances(first_day_of_month, actual_date) # du mois courant


    # fermeture de la connexion à la base de données
    connection.close()

    # envoi des données à la page HTML index.html
    return render_template('index.html', 
                           widgets=widgets_config,
                           best_clients_month=best_clients_month,  
                           client_most_remaining=client_most_remaining, 
                           total_clients=total_clients, 
                           number_seances_month=number_seances_month)


@app.route('/gestion_clients')
def gestion_clients():
    """
    Fonction exécutée lors de l'accès à la page gestion_clients ('/gestion_clients').
    Args:
        None
    Returns:
        str: rendu HTML de la page gestion_clients.
    """
    # connexion à la base de données
    connection = get_db_connection()

    # requête SQL pour récupérer tous les clients de la table 'clients'
    clients = connection.execute('SELECT * FROM clients').fetchall()

    # fermeture de la connexion à la base de données
    connection.close()

    # envoi des données à la page HTML gestion_clients.html
    return render_template('gestion_clients.html', clients=clients)




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
            connection.execute('INSERT INTO historique_seances (client_id, action, nombre) VALUES (?, ?, ?)', (client_id, "CHECK-IN", -1))

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
            connection.execute('INSERT INTO historique_seances (client_id, action, nombre) VALUES (?, ?, ?)',(nouveau_client_id, 'NEW_ACCOUNT', seances_initiales))

            # commit des changements
            connection.commit() 
            connection.close()

            # renvoie de l'utilisateur vers l'accueil
            return redirect(url_for('index'))

    if request.method == "GET" :
        connection.close()
        # affichage du formulaire d'ajout de client
        return render_template('ajout_client.html')




@app.route('/ajout_seances', methods=['GET', 'POST'])
def ajout_seances():
    """
    Fonction exécutée lors de l'accès à la page '/ajout_seances'.
    Args:
        None
    Returns:
        str: rendu HTML de la page d'ajout de séances.
    """
    # connexion à la base de données
    connection = get_db_connection()
    
    if request.method == "POST":
        # récupération des données du formulaire
        prenom = request.form['prenom'].strip().title()
        nom = request.form['nom'].strip().title() 
        seances_ajoutees = int(request.form['seances_ajoutees'])

        # recherche du client dans la base de données
        client = connection.execute('SELECT * FROM clients WHERE prenom = ? AND nom = ?', (prenom, nom)).fetchone()

        if client:
            client_id = client['id']

            # mise à jour du nombre de séances restantes pour le client
            connection.execute('UPDATE clients SET seances_restantes = seances_restantes + ? WHERE id = ?', (seances_ajoutees, client_id))

            # ajout dans historique seances
            connection.execute('INSERT INTO historique_seances (client_id, action, nombre) VALUES (?, ?, ?)', (client_id, "ADD_SEANCES", seances_ajoutees))

            # commit des changements
            connection.commit() 
            connection.close()

            # renvoie l'utilisateur vers l'accueil
            return redirect(url_for('index'))

    if request.method == "GET" :
        # affichage de la liste des clients
        clients = connection.execute('SELECT * FROM clients').fetchall()
        connection.close()
        return render_template('ajout_seances.html', clients=clients)


# lancement de l'application Flask
if __name__ == '__main__':
    app.run(debug=True)