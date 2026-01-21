import sqlite3
import random
from datetime import datetime, timedelta

# --- CONFIGURATION ---
DB_NAME = 'database_clients_test.db'
NB_CLIENTS = 100
DATE_DEBUT = datetime(2025, 1, 1)
DATE_FIN = datetime(2026, 1, 21) # Date d'aujourd'hui simulée

# Listes pour générer des noms aléatoires
PRENOMS = [
    "Emma", "Gabriel", "Léo", "Louise", "Raphaël", "Jade", "Louis", "Ambre", "Lucas", "Arthur",
    "Alice", "Jules", "Maël", "Liam", "Lina", "Adam", "Chloé", "Sacha", "Mia", "Hugo",
    "Noah", "Tiago", "Rose", "Anna", "Mila", "Lancelot", "Merlin", "Guenièvre", "Perceval", "Karadoc"
]

NOMS = [
    "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent",
    "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David", "Bertrand", "Morel", "Fournier", "Girard",
    "Bonnet", "Dupont", "Lambert", "Fontaine", "Rousseau", "Vincent", "Muller", "Lefevre", "Faure", "Andre"
]

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def generer_date_random(start, end):
    """Retourne une date aléatoire entre start et end"""
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

def main():
    print(f"🚀 Démarrage de la génération de données pour {NB_CLIENTS} clients...")
    conn = get_db_connection()
    
    # 1. NETTOYAGE (On vide les tables pour éviter les doublons/erreurs)
    print("🧹 Nettoyage de la base de données actuelle...")
    conn.execute("DELETE FROM clients")
    conn.execute("DELETE FROM historique_seances")
    conn.execute("DELETE FROM sqlite_sequence") # Réinitialise les compteurs d'ID à 1
    conn.commit()

    clients_generes = 0

    for _ in range(NB_CLIENTS):
        # --- A. Création du profil client ---
        prenom = random.choice(PRENOMS)
        nom = random.choice(NOMS)
        
        # Date d'inscription aléatoire entre Jan 2025 et maintenant
        date_inscription = generer_date_random(DATE_DEBUT, DATE_FIN)
        
        # On insère le client avec sa date d'inscription
        cur = conn.execute('INSERT INTO clients (prenom, nom, seances_restantes, date_inscription) VALUES (?, ?, ?, ?)',
                           (prenom, nom, 0, date_inscription.strftime('%Y-%m-%d')))
        client_id = cur.lastrowid
        
        # --- B. Génération de l'historique ---
        current_date = date_inscription
        solde = 10 # Solde de départ standard
        
        # 1. Événement Création
        conn.execute('''
            INSERT INTO historique_seances (client_id, action, nombre, date_heure) 
            VALUES (?, ?, ?, ?)
        ''', (client_id, 'CREATION_COMPTE', 10, current_date.strftime('%Y-%m-%d %H:%M:%S')))

        # Simulation de la vie du client de son inscription jusqu'à la fin
        # Fréquence : Un client vient en moyenne tous les 3 à 10 jours
        while True:
            # On avance dans le temps
            jours_ecoules = random.randint(2, 10) 
            current_date += timedelta(days=jours_ecoules)
            
            # Si on dépasse la date de fin, on arrête
            if current_date > DATE_FIN:
                break
            
            # Action : Le client vient faire une séance (CHECK_IN)
            solde -= 1
            conn.execute('''
                INSERT INTO historique_seances (client_id, action, nombre, date_heure) 
                VALUES (?, ?, ?, ?)
            ''', (client_id, 'CHECK-IN', -1, current_date.strftime('%Y-%m-%d %H:%M:%S')))
            
            # Gestion du rechargement : Si solde bas, il rachète
            if solde <= 1:
                # Il rachète le même jour ou le lendemain
                recharge = random.choice([5, 10, 20])
                solde += recharge
                conn.execute('''
                    INSERT INTO historique_seances (client_id, action, nombre, date_heure) 
                    VALUES (?, ?, ?, ?)
                ''', (client_id, 'ADD_SEANCES', recharge, current_date.strftime('%Y-%m-%d %H:%M:%S')))

        # --- C. Mise à jour finale du client ---
        # On enregistre le vrai solde restant après toute cette simulation
        conn.execute('UPDATE clients SET seances_restantes = ? WHERE id = ?', (solde, client_id))
        
        clients_generes += 1
        if clients_generes % 10 == 0:
            print(f"   ... {clients_generes} clients générés")

    conn.commit()
    conn.close()
    print("\n✅ TERMINÉ ! La base de données contient maintenant :")
    print(f"- {NB_CLIENTS} clients réalistes")
    print("- Un historique complet de Janvier 2025 à Janvier 2026")
    print("- Des dates cohérentes pour calculer les statistiques.")

# Initialisation de la base de données
connection = get_db_connection()
with open('schema.sql') as f:
    connection.executescript(f.read())

if __name__ == '__main__':
    main()