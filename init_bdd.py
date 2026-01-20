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