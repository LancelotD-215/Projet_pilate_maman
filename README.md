# 📂 Projet : Gestionnaire de Séances Pilate

## 🎯 1. Objectif Global
Créer une application web simple et efficace permettant à une coach de Pilates de gérer les carnets de séances de ses clients. L'objectif est de remplacer le suivi papier par une base de données numérique centralisée, accessible sur ordinateur et mobile.

## 🛠 2. Stack Technique
* **Langage Backend :** Python 3.14
* **Framework Web :** Flask (léger, simple, robuste).
* **Base de Données :** SQLite (fichier `.db` local).
* **Frontend :** HTML5 + Bootstrap (pour le design responsive) + Jinja2 (moteur de template).
* **Architecture :** Monolithique simple (pas de séparation API/Client complexe).

## 🗄 3. Structure des Données (Schéma SQL)

### Table `clients`
* `id` (Integer, PK): Identifiant unique.
* `nom` (Text): Nom de famille.
* `prenom` (Text): Prénom.
* `seances_restantes` (Integer): Solde actuel (ex: 4, 12).
* `date_inscription` (Date): Date d'ajout du client.

### Table `historique_seances`
* `id` (Integer, PK): Identifiant unique de l'action.
* `client_id` (Integer, FK): Lien vers le client concerné.
* `date_heure` (Datetime): Quand l'action a eu lieu.
* `action` (Text): Type d'événement (`CHECK_IN`, `ACHAT_FORFAIT`, `CORRECTION`).
* `montant` (Integer): Variation du solde (ex: -1, +10).

## 💻 4. Fonctionnalités (MVP - Minimum Viable Product)

### A. Interface "Check-in" (Côté Client/Tablette entrée)
* **Liste déroulante** des clients inscrits (triée alphabétiquement).
* Bouton **"Valider ma présence"**.
* **Action :** Décrémente le solde de 1 séance et logue l'action.
* **Feedback :** "Bon cours [Prénom] ! Il vous reste X séances".

### B. Interface Administration (Côté Coach)
* **Tableau de bord :** Liste de tous les clients avec solde visible.
* **Gestion des crédits :** Boutons rapides (+1, +10, +20 séances).
* **Création de profil :** Formulaire ajout client (Nom, Prénom).
* **Sécurité (V1) :** Authentification basique.

## 🚀 5. Évolutions Futures (Roadmap V2)
* **Identification :** QR Codes individuels ou Cookies persistants.
* **Statistiques :** Graphiques de fréquentation.
* **Historique détaillé :** Consultation des logs par client.

## Architecture des fichiers
Projet_Pilate/
├── app.py              (Le cerveau - Python)
├── init_db.py          (Le constructeur de la BDD - Python)
├── schema.sql          (Le plan de la BDD - SQL)
└── templates/          (Dossier pour le HTML)
    ├── layout.html     (Le squelette visuel avec Bootstrap)
    └── index.html      (La page d'accueil)
├── static/             (Dossier pour les fichiers fixes)
│   └── style.css       (Ton CSS personnalisé (si besoin))