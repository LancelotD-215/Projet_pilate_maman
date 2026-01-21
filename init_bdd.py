# -*- coding: utf-8 -*-
"""
author: @lancelot
name : init_bdd.py
description : code d'initialisation de la base de données
date : 2026/01/20
"""

print("Début du programme.")

# import des modules
import sqlite3 # pour gérer la bdd SQLite

# connexion à la base de données (ou création si elle n'existe pas)
connection = sqlite3.connect('database_clients.db') # connexion à la bdd
print("Base de données connectée avec succès.")

# execution du shema de la base de données
with open('schema.sql') as f:
    connection.executescript(f.read()) # exécution du script SQL
print("Schéma de la base de données créé avec succès.")

# ajout de données test 
curseur = connection.cursor() # création d'un curseur (stylo pour écrire) pour exécuter des commandes SQL

# création d'utilisateurs test
curseur.execute("INSERT INTO clients (prenom, nom, seances_restantes) VALUES (?, ?, ?)", ('Lancelot', 'Du Lac', 5)) # ? remplacés par tuple (pour contrer les injections SQL)
curseur.execute("INSERT INTO clients (prenom, nom, seances_restantes) VALUES (?, ?, ?)", ('Guenièvre', 'La Belle', 3)) 
# utilisation d'une séance test
curseur.execute("INSERT INTO historique_seances (client_id, action, nombre) VALUES (?, ?, ?)", (1, 'CHECK-IN', 1))
curseur.execute("UPDATE clients SET seances_restantes = seances_restantes - 1 WHERE id = ?", (1,))

print("Utilisateurs test insérés avec succès.")

# validation des changements
connection.commit()

# fermeture de la connexion
connection.close()

print("Connexion à la base de données fermée.")
print("Fin du programme.")