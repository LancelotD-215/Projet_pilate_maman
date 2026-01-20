/*
author: @lancelot
name : schema.sql
description : 
date : 2026/01/20
*/



-- Supprimer les tables existantes pour éviter les conflits
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS historique_seances;

-- Création de la table des clients
CREATE TABLE clients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identifiant unique pour chaque client, INTEGER pour un entier, AUTOINCREMENT pour qu'il s'incrémente automatiquement
    prenom TEXT NOT NULL, --TEXT pour chaine de caractères, NOT NULL pour que ce champ soit obligatoire
    nom TEXT NOT NULL,
    seances_restantes INTEGER DEFAULT 0,
    date_inscription DATE DEFAULT CURRENT_DATE
);

-- Création de la table de l'historique des séances
CREATE TABLE historique_seances(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    date_heure DATETIME DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL, -- le quoi de l'action (ajout, utilisation, correction, etc.)
    nombre INTEGER DEFAULT 0, -- le nombre de séances ajoutées ou utilisées
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE -- ON DELETE CASCADE pour supprimer les séances associées si un client est supprimé
);