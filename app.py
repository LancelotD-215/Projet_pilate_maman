# -*- coding: utf-8 -*-
"""
author: @lancelot
name : app.py
description : code principal de l'application Flask pour la gestion des clients de Pilates
date : 2026/01/20
"""

# Test de synchronisation sécurisée

# imports des modules
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, make_response, session
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from app_lib import client_not_comming, get_db_connection, get_best_clients, get_client_most_remaining, get_number_seances, get_negative_seances_clients, get_zero_clients
import pytz
import os

# création de l'application Flask
app = Flask(__name__) # création du site web
app.config['SECRET_KEY'] = 'xcbxf0xfaZxedxb29xbaxdcx19xccxf2x11x01xcc2x13xff7x94px14xf1'

# durée de vie de la session si "Rester connecté" est coché
app.permanent_session_lifetime = timedelta(days=30)

# récupération de l'heure de paris
paris_tz = pytz.timezone('Europe/Paris')


# --- AUTHENTIFICATION ---
# identifiant et mot de passe (hashé) de l'administratrice
ADMIN_USERNAME = 'servane'
ADMIN_PASSWORD_HASH = 'pbkdf2:sha256:1000000$tMYspdsLckEdJMMV$143b828ba4c711efb9e176cf5435bd443849242904d7c54a51997b6a23324c76'

# pages accessibles SANS être connecté (la borne reste publique pour les clients)
PUBLIC_ENDPOINTS = {'login', 'borne', 'borne_succes', 'static'}


@app.before_request
def require_login():
    """
    Avant chaque requête, on vérifie que l'utilisateur est connecté,
    sauf pour les pages publiques (borne, page de connexion, fichiers statiques).
    """
    # on laisse passer les pages publiques et les requêtes sans endpoint (404)
    if request.endpoint in PUBLIC_ENDPOINTS or request.endpoint is None:
        return
    # sinon, connexion obligatoire
    if not session.get('logged_in'):
        return redirect(url_for('login', next=request.path))


@app.template_filter('format_datetime')
def format_datetime(value, format="%d/%m/%Y à %H:%M"):
    """Filtre Jinja pour formater les dates proprement."""
    if value is None:
        return ""
    
    # Si c'est déjà un objet datetime, on formate direct
    if isinstance(value, datetime):
        return value.strftime(format)
    
    # Si c'est une string (ex: venant de SQLite), on essaie de la parser
    try:
        # On nettoie le 'T' éventuel et les microsecondes
        value = value.replace('T', ' ').split('.')[0]
        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return dt.strftime(format)
    except ValueError:
        # Si ça ne marche pas (ex: format date seul YYYY-MM-DD), on essaie juste la date
        try:
            dt = datetime.strptime(value, '%Y-%m-%d')
            return dt.strftime('%d/%m/%Y')
        except ValueError:
            return value # On renvoie tel quel si on n'y arrive pas




# création des routes pour le site web (pages)
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Page de connexion à l'espace d'administration.
    Args:
        None
    Returns:
        str: rendu HTML de la page de connexion, ou redirection si succès.
    """
    # si déjà connecté, on redirige vers l'accueil
    if session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember')  # case "Rester connecté"

        # vérification de l'identifiant et du mot de passe
        if username.lower() == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            # "Rester connecté" => session persistante (cookie 30 jours), sinon session de navigation
            session.permanent = bool(remember)

            # redirection vers la page demandée initialement (en restant sur le site)
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                return redirect(next_url)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', erreur="Identifiant ou mot de passe incorrect.")

    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Déconnexion : vide la session et supprime le cookie de connexion.
    Args:
        None
    Returns:
        str: redirection vers la page de connexion.
    """
    session.clear()
    return redirect(url_for('login'))


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
        'negative_balance': True,
        'zero_balance': True,
        'best_client_month': True,
        'best_client_all_time': False,
        'most_remaining': True,
        'total_clients': True,
        'seances_month': True,
        'client_not_comming' : True
    }

    # initialisation des données des widgets
    negative_clients = []
    best_clients_month = None
    best_clients_all_time = None
    client_most_remaining = None
    total_clients = None
    number_seances_month = None
    clients_not_coming = None

    # récupération des variables
    actual_date = datetime.now(paris_tz).strftime('%Y-%m-%d')
    first_day_of_month = actual_date[:8] + '01' # premier jour du mois courant

    # création des données pour les widgets
    if widgets_config['negative_balance']:
        negative_clients = get_negative_seances_clients()
    if widgets_config['zero_balance']:
        zero_clients = get_zero_clients()
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
    if widgets_config['client_not_comming']:
        clients_not_coming = client_not_comming((datetime.now(paris_tz) - timedelta(days=30)).strftime('%Y-%m-%d'), actual_date)

    # fermeture de la connexion à la base de données
    connection.close()

    # envoi des données à la page HTML index.html
    return render_template('index.html', 
                            widgets=widgets_config,
                            negative_clients=negative_clients,
                            zero_clients=zero_clients,
                            best_clients_month=best_clients_month,  
                            client_most_remaining=client_most_remaining, 
                            total_clients=total_clients, 
                            number_seances_month=number_seances_month,
                            clients_not_coming=clients_not_coming
                           )


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

        # récuperation de l'heure actuelle à Paris
        current_time = datetime.now(paris_tz).strftime('%Y-%m-%d %H:%M:%S')

        # recherche du client dans la base de données
        client = connection.execute('SELECT * FROM clients WHERE prenom = ? AND nom = ?', (prenom, nom)).fetchone()
        
        if client:
            # récupération de l'ID du client
            client_id = client['id']

            # mise à jour de la présence du client dans la base de données
            connection.execute('UPDATE clients SET seances_restantes = seances_restantes - 1, total_seances_faites = total_seances_faites + 1 WHERE id = ?', (client_id,))

            # ajout dans historique seances
            connection.execute('INSERT INTO historique_seances (client_id, action, nombre, date_heure) VALUES (?, ?, ?, ?)', (client_id, "CHECK-IN", -1, current_time))

            # calcul du solde restant après le check-in
            nouveau_solde = client['seances_restantes'] - 1

            # commit des changements
            connection.commit()
            connection.close()

            # ré-affichage de la page avec la pop-up de confirmation
            return render_template('presence.html', success={
                'prenom': prenom,
                'nom': nom,
                'solde': nouveau_solde
            })
        
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
        seances_initiales = int(request.form['seances_restantes'])

        email = request.form.get('email') # .get pour champ optionnel
        telephone = request.form.get('telephone')

        abonnement = 1 if request.form.get('abonnement') else 0

        creneau = request.form.get('creneau') # pour les habitudes (optionnel car on pourra le remplir par la suite)

        # vérification si le client existe déjà
        existing_client = connection.execute('SELECT * FROM clients WHERE prenom = ? AND nom = ?', (prenom, nom)).fetchone()

        if existing_client:
            connection.close()
            return (f"<h1>Erreur : Le client '{prenom} {nom}' existe déjà.</h1><p>Veuillez vérifier les informations et réessayer.</p><a href='/ajout_client'>Réessayer</a>")
        
        else:
            # curseur pour récupérer l'ID du nouveau client
            curseur = connection.execute('INSERT INTO clients (prenom, nom, seances_restantes, email, telephone, abonnement) VALUES (?, ?, ?, ?, ?, ?)',(prenom, nom, seances_initiales, email, telephone, abonnement))
            
            # récupération de l'ID du nouveau client
            nouveau_client_id = curseur.lastrowid

            current_time = datetime.now(paris_tz).strftime('%Y-%m-%d %H:%M:%S')

            # ajout dans historique seances
            connection.execute('INSERT INTO historique_seances (client_id, action, nombre, date_heure) VALUES (?, ?, ?, ?)',(nouveau_client_id, 'NEW_ACCOUNT', seances_initiales, current_time))

            # ajout des habitudes si un créneau a été sélectionné
            if creneau:
                connection.execute('INSERT INTO habitudes (client_id, creneau_id) VALUES (?, ?)', (nouveau_client_id, creneau))

            # commit des changements
            connection.commit() 
            connection.close()

            # renvoie de l'utilisateur vers l'accueil
            return redirect(url_for('index'))

    if request.method == "GET" :
        planning = connection.execute('''
        SELECT * FROM semaine_type
        WHERE actif = 1 
        ORDER BY jour_semaine, heure_debut
        ''').fetchall()
        connection.close()
        # affichage du formulaire d'ajout de client
        return render_template('ajout_client.html', planning=planning)




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

            current_time = datetime.now(paris_tz).strftime('%Y-%m-%d %H:%M:%S')

            # ajout dans historique seances
            connection.execute('INSERT INTO historique_seances (client_id, action, nombre, date_heure) VALUES (?, ?, ?, ?)', (client_id, "ADD_SEANCES", seances_ajoutees, current_time))

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



@app.route('/ajout_seances_rapide', methods=['POST'])
def ajout_seances_rapide():
    """
    Fonction exécutée lors de l'accès à la page '/ajout_seances_rapide'.
    Args:
        None
    Returns:
        str: redirection vers la page de gestion des clients.
    """
    # connexion à la base de données
    connection = get_db_connection()
    
    if request.method == "POST":
        # récupération des données du formulaire
        client_id = int(request.form['client_id'])
        seances_ajoutees = int(request.form['seances_ajoutees'])

        # récupération de l'heure de paris 
        current_time = datetime.now(paris_tz).strftime('%Y-%m-%d %H:%M:%S')

        # mise à jour du nombre de séances restantes pour le client
        connection.execute('UPDATE clients SET seances_restantes = seances_restantes + ? WHERE id = ?', (seances_ajoutees, client_id))

        # ajout dans historique seances
        connection.execute('INSERT INTO historique_seances (client_id, action, nombre, date_heure) VALUES (?, ?, ?, ?)', (client_id, "ADD_SEANCES", seances_ajoutees, current_time))

        # récupération de l'origine de la requête
        origine = request.form.get('origine')

        # commit des changements
        connection.commit() 
        connection.close()

        # renvoie l'utilisateur vers la page appropriée selon l'origine du formulaire
        if origine == 'index':
            # Si le formulaire contenait <input name="origine" value="index">
            return redirect(url_for('index'))
        elif origine == 'fiche_client':
            # Si le formulaire contenait <input name="origine" value="fiche_client">
            return redirect(url_for('fiche_client', client_id=client_id))
        else:
            # Sinon (comportement par défaut pour la page gestion_clients)
            return redirect(url_for('gestion_clients'))



@app.route('/recherche_client', methods=['GET'])
def recherche_client():
    """
    Fonction exécutée lors de l'accès à la page '/recherche_client'.
    Recherche un client par son nom complet et redirige vers sa fiche.
    Gère les noms et prénoms composés.
    Args:
        None
    Returns:
        str: rendu HTML de la page de résultats de recherche de client.
    """
    # récupération du terme de recherche depuis les paramètres GET
    query = request.args.get('q', '').strip()

    if not query:
        return redirect(url_for('gestion_clients'))
    
    # connexion à la base de données
    connection = get_db_connection()

    client = connection.execute('''
        SELECT id FROM clients 
        WHERE (prenom || ' ' || nom) LIKE ? 
           OR (nom || ' ' || prenom) LIKE ?
    ''', (query, query)).fetchone()

    connection.close()

    # envoi des résultats à la page HTML recherche_client.html
    if client:
        return redirect(url_for('fiche_client', client_id=client['id']))
    else:
        # Si aucun client n'est trouvé, on peut rediriger vers la liste avec un message
        return "<h1>Client introuvable</h1><p>Désolé, aucun client ne correspond à cette recherche.</p><a href='/gestion_clients'>Retour à la liste</a>"



@app.route('/client/<int:client_id>')
def fiche_client(client_id):
    """
    Fonction exécutée lors de l'accès à la page '/client/<client_id>'.
    Args:
        client_id (int): ID du client à afficher.
    Returns:
        str: rendu HTML de la fiche du client.
    """
    # connexion à la base de données
    connection = get_db_connection()

    # récupération des informations du client
    client = connection.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()

    # récupération des habitudes du client
    habitudes = connection.execute('''
        SELECT s.id, s.jour_semaine, s.heure_debut, s.type_seance 
        FROM habitudes h
        JOIN semaine_type s ON h.creneau_id = s.id
        WHERE h.client_id = ?
    ''', (client_id,)).fetchall()

    # récupération de l'historique des séances du client (10 dernières actions)
    historique = connection.execute('''
        SELECT date_heure, action, nombre 
        FROM historique_seances 
        WHERE client_id = ? 
        ORDER BY date_heure DESC 
        LIMIT 10
    ''', (client_id,)).fetchall()

    # récupération des tous les créneaux pour la modale
    creneaux = connection.execute('''
        SELECT id, jour_semaine, heure_debut, type_seance 
        FROM semaine_type 
        WHERE actif = 1 
        ORDER BY jour_semaine, heure_debut
    ''').fetchall()

    # fermeture de la connexion à la base de données
    connection.close()

    # pour affichage des jours
    jours_semaine = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}

    # envoi des données à la page HTML fiche_client.html
    return render_template('fiche_client.html', 
                            client=client, 
                            habitudes=habitudes, 
                            historique=historique,
                            creneaux=creneaux,
                            jours=jours_semaine)



@app.route('/planning')
def planning():
    """
    Fonction exécutée lors de l'accès à la page '/planning'.
    Args:
        None
    Returns:
        str: rendu HTML de la page de planning.
    """
    # récupération du paramètre 'semaine' pour décaler l'affichage du planning
    try:
        offset = int(request.args.get('semaine', 0))
    except ValueError:
        offset = 0

    # calcul des dates de début et de fin de la semaine à afficher
    today = datetime.now(paris_tz)
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    end_of_week = start_of_week + timedelta(days=4)
    
    # Formatage dates pour SQL
    start_sql = start_of_week.strftime('%Y-%m-%d')
    end_sql = (end_of_week + timedelta(days=1)).strftime('%Y-%m-%d') # +1 jour pour inclure le vendredi soir

    # Calcul du numéro de semaine ISO
    week_number = start_of_week.isocalendar()[1]
    period_title = f"Semaine {week_number}"

    connection = get_db_connection()
    
    # 1. Squelette planning
    planning_squelett = connection.execute('SELECT * FROM semaine_type WHERE actif = 1 ORDER BY heure_debut').fetchall()

    # 2. Habitudes (Qui est censé venir ?)
    habitudes_data = connection.execute('''
        SELECT h.creneau_id, c.id as client_id, c.prenom, c.nom, c.seances_restantes
        FROM habitudes h
        JOIN clients c ON h.client_id = c.id
    ''').fetchall()
    
    # 3. Historique de la semaine (Qui est DÉJÀ venu ?)
    # On cherche les CHECK-IN ou PRESENCE_VALIDEE dans la plage de la semaine affichée
    presence_data = connection.execute('''
        SELECT client_id, date_heure 
        FROM historique_seances 
        WHERE date_heure >= ? AND date_heure < ? 
        AND action IN ('CHECK-IN', 'PRESENCE_VALIDEE')
    ''', (start_sql, end_sql)).fetchall()

    connection.close()

    # --- TRAITEMENT DES DONNÉES EN PYTHON ---

    # A. Organiser les habitudes par créneau
    # Dict: { creneau_id : [ {id: 1, nom: "Lancelot D"}, ... ] }
    clients_par_creneau = {}
    for h in habitudes_data:
        cid = h['creneau_id']
        if cid not in clients_par_creneau:
            clients_par_creneau[cid] = []
        clients_par_creneau[cid].append({
            'id': h['client_id'],
            'nom': f"{h['prenom']} {h['nom']}",
            'solde': h['seances_restantes']
        })

    # B. Créer un set de présence pour vérification rapide
    # Format de la clé : "ID_CLIENT|YYYY-MM-DD HH:MM" (On compare à la minute près le début du cours)
    # Note : Dans la route 'presence', le check-in insère datetime.now(). 
    # Si tu veux une correspondance parfaite, il faudra s'assurer que le check-in soit tolerant ou utilise l'heure du cours.
    # ICI : On va simplifier -> Si le client a un check-in ce jour là dans une plage de +/- 2h autour du cours, ou pile à l'heure.
    # Pour ton besoin strict "durant le créneau", on va faire une logique simple : Check sur la DATE et l'HEURE approximative.
    
    # Pour simplifier ton code actuel, supposons que 'PRESENCE_VALIDEE' met l'heure pile (c'est le cas).
    # Pour les 'CHECK-IN' faits à la borne, ils ont l'heure réelle. 
    # On va stocker : "client_id|YYYY-MM-DD" -> Liste des heures pointées
    presences_map = {} 
    for p in presence_data:
        date_str = p['date_heure'].replace('T', ' ')  # Gérer le format ISO avec T
        p_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        key = f"{p['client_id']}|{p_date.strftime('%Y-%m-%d')}" # Clé = ID + Jour
        if key not in presences_map:
            presences_map[key] = []
        presences_map[key].append(p_date.strftime('%H:%M')) # On stocke l'heure du pointage

    # ... (Constantes HEURE_DEBUT, etc. inchangées) ...
    HEURE_DEBUT = 9
    HEURE_FIN = 21
    DUREE_TOTAL_MINUTES = (HEURE_FIN - HEURE_DEBUT) * 60
    heure_affichage = [f"{h:02d}:00" for h in range(HEURE_DEBUT, HEURE_FIN + 1)]

    semaine_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
    planning = []

    for jour in range(5):
        jour_date = start_of_week + timedelta(days=jour)
        jour_date_str = jour_date.strftime('%Y-%m-%d') # Ex: 2026-02-06
        
        creneaux_jour = [c for c in planning_squelett if c['jour_semaine'] == jour]
        creneaux_jour_processed = []

        for creneau in creneaux_jour:
            # Calculs position (inchangé)
            start_time = datetime.strptime(creneau['heure_debut'], '%H:%M')
            h_debut, m_debut = map(int, start_time.strftime('%H:%M').split(':'))
            min_from_begin = (h_debut - HEURE_DEBUT) * 60 + m_debut
            top_percent = (min_from_begin / DUREE_TOTAL_MINUTES) * 100
            height_percent = (creneau['duree'] / DUREE_TOTAL_MINUTES) * 100

            # --- LOGIQUE PRÉSENCE ---
            # On récupère les habitués de ce créneau
            raw_clients = clients_par_creneau.get(creneau['id'], [])
            final_clients = []

            for cl in raw_clients:
                is_present = False
                # Clé de recherche : Ce client, ce jour là
                lookup_key = f"{cl['id']}|{jour_date_str}"
                
                if lookup_key in presences_map:
                    # Le client a pointé ce jour là. Est-ce pendant CE cours ?
                    # On regarde s'il y a un pointage proche de l'heure de début (ex: check-in réel)
                    # OU si c'est pile l'heure de début (bouton manuel)
                    heures_pointages = presences_map[lookup_key]
                    cours_h_debut = creneau['heure_debut'] # "10:00"
                    
                    # Logique : Si on trouve l'heure exacte (Marquage manuel) OU heure proche (Check-in borne)
                    # Pour l'instant, vérifions simple : Si le bouton manuel met l'heure pile, ça matchera ici.
                    # Pour les check-ins bornes, il faudrait convertir en minutes et voir si écart < 60min.
                    # Simplifions : Si une action existe ce jour là vers cette heure.
                    # Pour ton code actuel, je vais check si l'heure du cours est dans la liste (cas bouton manuel)
                    # ou si on a un checkin.
                    
                    # Amélioration : On considère présent si un pointage existe entre heure_debut et heure_fin
                    course_start_min = h_debut * 60 + m_debut
                    course_end_min = course_start_min + creneau['duree']

                    for hp in heures_pointages:
                        hp_h, hp_m = map(int, hp.split(':'))
                        pointage_min = hp_h * 60 + hp_m
                        # Si le pointage est entre le début (avance de 30 minutes) et la fin du cours
                        if (course_start_min - 30) <= pointage_min <= course_end_min: # le -30min permet de prendre en compte les check-ins faits un peu avant le début du cours
                            is_present = True
                            break

                final_clients.append({
                    'id': cl['id'],
                    'nom': cl['nom'],
                    'present': is_present,
                    'solde': cl['solde']
                })

            creneaux_jour_processed.append({
                'data': creneau,
                'style': f"top: {top_percent}%; height: {height_percent}%;",
                'clients': final_clients,
                'date_reelle': jour_date_str # On passe la vraie date pour le formulaire
            })
        
        planning.append({
            'nom': semaine_fr[jour],
            'date_courte': jour_date.strftime('%d/%m'),
            'is_today': jour_date.date() == today.date(),
            'creneaux': creneaux_jour_processed
        })
        
    return render_template('planning.html',
                           semaine=planning,
                           period_title=period_title,
                           offset=offset,
                           heures=heure_affichage)



@app.route('/marquer_presence', methods=['POST'])
def marquer_presence():
    """
    Fonction exécutée lors de l'accès à la page '/marquer_presence'.
    Args:
        None
    Returns:
        str: redirection vers la page de planning.
    """
    client_id = request.form['client_id']
    date_seance = request.form['date_seance'] # Format YYYY-MM-DD
    heure_seance = request.form['heure_seance'] # Format HH:MM
    
    # On reconstruit le timestamp exact du début du cours
    timestamp_seance = f"{date_seance} {heure_seance}:00"

    connection = get_db_connection()

    # Débiter le client
    connection.execute('UPDATE clients SET seances_restantes = seances_restantes - 1, total_seances_faites = total_seances_faites + 1 WHERE id = ?', (client_id,))
    
    # Ajouter l'historique (Note le -1 et l'action spécifique)
    connection.execute('''
        INSERT INTO historique_seances (client_id, action, nombre, date_heure) 
        VALUES (?, ?, ?, ?)
    ''', (client_id, "PRESENCE_VALIDEE", -1, timestamp_seance))

    connection.commit()
    connection.close()

    # On recharge la page planning (on essaie de rester sur la même semaine si possible)
    return redirect(request.referrer or url_for('planning'))



@app.route('/modif_inscriptions', methods=['POST'])
def modif_inscriptions():
    """
    Fonction exécutée lors de l'accès à la page '/modif_inscriptions'.
    Args:
        None
    Returns:
        str: redirection vers la page de gestion des clients.
    """
    # connexion à la base de données
    connection = get_db_connection()
    
    if request.method == "POST":
        # récupération des données du formulaire
        client_id = int(request.form['client_id'])
        nouveaux_creneaux = request.form.getlist('creneaux')

        # 1. On nettoie les anciennes habitudes
        connection.execute('DELETE FROM habitudes WHERE client_id = ?', (client_id,))

        # 2. On ajoute les nouvelles
        for creneau_id in nouveaux_creneaux:
            connection.execute('INSERT INTO habitudes (client_id, creneau_id) VALUES (?, ?)', 
                            (client_id, creneau_id))
        
        # commit des changements
        connection.commit()
        connection.close()
        
        return redirect(url_for('fiche_client', client_id=client_id))



@app.route('/modif_client', methods=['POST'])
def modif_client():
    """
    Fonction exécutée lors de l'accès à la page '/modif_client'.
    Met à jour les informations d'un client (prénom, nom, email, téléphone).
    Args:
        None
    Returns:
        str: redirection vers la fiche du client.
    """
    # connexion à la base de données
    connection = get_db_connection()

    # récupération des données du formulaire
    client_id = int(request.form['client_id'])
    prenom = request.form['prenom'].strip().title()
    nom = request.form['nom'].strip().title()
    email = request.form.get('email', '').strip() or None
    telephone = request.form.get('telephone', '').strip() or None

    # vérification qu'un AUTRE client ne porte pas déjà ce prénom/nom
    existing_client = connection.execute(
        'SELECT id FROM clients WHERE prenom = ? AND nom = ? AND id != ?',
        (prenom, nom, client_id)
    ).fetchone()

    if existing_client:
        connection.close()
        return (f"<h1>Erreur : Le client '{prenom} {nom}' existe déjà.</h1>"
                f"<p>Veuillez vérifier les informations et réessayer.</p>"
                f"<a href='/client/{client_id}'>Retour à la fiche</a>")

    # mise à jour des informations du client
    connection.execute(
        'UPDATE clients SET prenom = ?, nom = ?, email = ?, telephone = ? WHERE id = ?',
        (prenom, nom, email, telephone, client_id)
    )

    # commit des changements
    connection.commit()
    connection.close()

    # renvoie de l'utilisateur vers la fiche du client
    return redirect(url_for('fiche_client', client_id=client_id))



@app.route('/supprimer_client', methods=['POST'])
def supprimer_client():
    """
    Fonction exécutée lors de l'accès à la page '/supprimer_client'.
    Supprime définitivement un client ainsi que ses données liées
    (habitudes et historique des séances).
    Args:
        None
    Returns:
        str: redirection vers la page de gestion des clients.
    """
    # connexion à la base de données
    connection = get_db_connection()

    # récupération de l'ID du client à supprimer
    client_id = int(request.form['client_id'])

    # suppression des données liées puis du client lui-même
    # (SQLite n'applique pas le ON DELETE CASCADE par défaut, on le fait manuellement)
    connection.execute('DELETE FROM habitudes WHERE client_id = ?', (client_id,))
    connection.execute('DELETE FROM historique_seances WHERE client_id = ?', (client_id,))
    connection.execute('DELETE FROM clients WHERE id = ?', (client_id,))

    # commit des changements
    connection.commit()
    connection.close()

    # renvoie de l'utilisateur vers la liste des clients
    return redirect(url_for('gestion_clients'))




@app.route('/borne', methods=['GET', 'POST'])
def borne():
    """
    Fonction exécutée lors de l'accès à la page '/borne'. 
    Args: 
        None 
    Returns: 
        str: rendu HTML de la page de la borne de check-in. """
    connection = get_db_connection()
    
    # récupération des cookies pour pré-remplir le formulaire si disponibles
    id_cookie = request.cookies.get('borne_id')
    prenom_cookie = request.cookies.get('borne_prenom')
    nom_cookie = request.cookies.get('borne_nom')

    if request.method == "POST":
        client_id = request.form.get('client_id')
        if client_id:
            # validation rapide
            client = connection.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
        else :
            # validation manuelle
            prenom = request.form['prenom'].strip().title()
            nom = request.form['nom'].strip().title()
            client = connection.execute('SELECT * FROM clients WHERE prenom = ? AND nom = ?', (prenom, nom)).fetchone()
        
        if client:
            # Calcul du nouveau solde
            nouveau_solde = client['seances_restantes'] - 1
            client_id = client['id']
            prenom = client['prenom']
            nom = client['nom']
            current_time = datetime.now(paris_tz).strftime('%Y-%m-%d %H:%M:%S')

            # Mise à jour
            connection.execute('UPDATE clients SET seances_restantes = ?, total_seances_faites = total_seances_faites + 1 WHERE id = ?', (nouveau_solde, client_id))
            connection.execute('INSERT INTO historique_seances (client_id, action, nombre, date_heure) VALUES (?, ?, ?, ?)', (client_id, "CHECK-IN", -1, current_time))
            connection.commit()
            connection.close()

            # On stocke le résultat en session puis on REDIRIGE vers la page de succès.
            # (Schéma POST/Redirect/GET : empêche le re-décompte si le client recharge la page.)
            session['borne_succes'] = {'prenom': prenom, 'solde': nouveau_solde}

            response = make_response(redirect(url_for('borne_succes')))

            # on enregistre le cookie pour 60 jours
            max_age = 60 * 24 * 60 * 60 # 60 jours en secondes
            response.set_cookie('borne_id', str(client_id), max_age=max_age)
            response.set_cookie('borne_prenom', prenom, max_age=max_age)
            response.set_cookie('borne_nom', nom, max_age=max_age)

            return response

        else:
            connection.close()
            # On renvoie l'erreur ET les infos du cookie pour que la pop-up puisse se ré-ouvrir
            return render_template('borne.html', 
                                erreur="Client non trouvé.",
                                id_cookie=id_cookie, 
                                prenom_cookie=prenom_cookie, 
                                nom_cookie=nom_cookie)

    # Affichage du formulaire vide
    connection.close()
    return render_template('borne.html',
                           id_cookie=id_cookie,
                           prenom_cookie=prenom_cookie,
                           nom_cookie=nom_cookie)




@app.route('/borne_succes')
def borne_succes():
    """
    Page de confirmation affichée après un pointage à la borne.
    Lit le résultat depuis la session (et le retire, pour qu'un rechargement
    ne re-décompte pas de séance et n'affiche pas une info périmée).
    Args:
        None
    Returns:
        str: rendu HTML de la page de succès, ou redirection vers la borne.
    """
    # on récupère ET on supprime les infos de la session (usage unique)
    data = session.pop('borne_succes', None)

    # si on arrive ici sans pointage récent (rechargement, accès direct), retour à la borne
    if not data:
        return redirect(url_for('borne'))

    return render_template('borne_succes.html', prenom=data['prenom'], solde=data['solde'])




# lancement de l'application Flask
if __name__ == '__main__':
    is_local = 'PYTHONANYWHERE_DOMAIN' not in os.environ
    app.run(debug=is_local)
