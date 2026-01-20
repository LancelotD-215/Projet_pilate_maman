# -*- coding: utf-8 -*-
"""
author: @lancelot
name : init_bdd.py
description : code d'initialisation de la base de données
date : 2026/01/20
"""

# import des modules
import sqlite3 # pour gérer la bdd SQLite

# connexion à la base de données (ou création si elle n'existe pas)
connection = sqlite3.connect('pilate_maman.db')

# execution du shema de la base de données
with open('schema.sql') as f:
    connection.executescript(f.read()) # exécution du script SQL

# ajout de données test 
curseur = connection.cursor() # création d'un curseur (stylo pour écrire) pour exécuter des commandes SQL

# création d'utilisateurs test
curseur.execute("INSERT INTO clients (prenom, nom, seances_restantes) VALUES (?, ?, ?)", ('Lancelot', 'Du Lac', 5)) # ? remplacés par tuple (pour contrer les injections SQL)
curseur.execute("INSERT INTO clients (prenom, nom, seances_restantes) VALUES (?, ?, ?)", ('Guenièvre', 'La Belle', 3)) 

# validation des changements
connection.commit()

# fermeture de la connexion
connection.close()