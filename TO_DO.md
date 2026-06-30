# Principale

## 🔐 Sécurité / Authentification (FAIT)
L'espace admin est protégé par un identifiant + mot de passe.
La borne (`/borne` et `/borne_succes`) reste PUBLIQUE (les clients pointent eux-mêmes).
- [x] Page de connexion `/login` (identifiant : `servane`, mot de passe hashé en pbkdf2).
- [x] Case **"Rester connecté"** : session persistante 30 jours si cochée, sinon session de navigation.
- [x] Fine barre en bas (`layout.html`) avec bouton **"Se déconnecter"** (`/logout`, vide la session).
- [x] Protection de toutes les routes admin via `@app.before_request` (liste blanche : login, borne, borne_succes, static).
- Décision retenue : credentials fixes (pas de flux de 1ère connexion). Mot de passe
  stocké hashé dans `app.py` (constante `ADMIN_PASSWORD_HASH`).
- Améliorations possibles plus tard : sortir le SECRET_KEY et le hash dans des
  variables d'environnement ; déplacer les identifiants dans une table `admin`.

## Implémentation de la base de données
- [x] Ajouter la base de données déja existante

## Implémentation de l'agenda
- [x] Créer la page calendrier
- [x] créer le pop up de quand on clique sur une séance pour afficher plus d'infos et pouvoir valider les présences
- [x] Integrer la gestion client dans l'agenda
- [x] Validation séances dans l'agenda
- [x] Afficher le solde restant à gauche du badge "Présent" dans le pop-up de l'agenda
- [x] Corriger le double-décompte de la borne au rechargement (POST/Redirect/GET + /borne_succes)
- [ ] Ajout méthode ajout suppression
  - [ ] Ajouter des séances dans l'agenda de manière ponctuelle
  - [ ] Ajouter des séances dans l'agenda de manière definitive
  - [ ] Supprimer des séances dans l'agenda de manière ponctuelle
  - [ ] Supprimer des séances dans l'agenda de manière definitive
- [ ] Ajout client non inscrit dans séances

## Implémentation des widgets
- [ ] Ajouter widget bouton pour choix des widgets à afficher
- [x] Ajouter widget client pas venus depuis 1 mois
- [x] Ajouter widget personnes a zero séances
- [ ] Ajout séance en cours dans le widget

## correctifs divers
- [x] corriger le nombre de cours du mois dans le widget
- [x] corriger les couleurs dans gestion client des séances
- [x] corriger le nom dans l'historique dans la fiche client (NEW_ACCOUNT -> Création du compte)
- [x] corriger la plage horaire de présence pour valider a -30 min avant la séance
- [x] corriger la bonne heure
- [ ] corriger l'affichage des séances habituelles dans la fiche client
- [x] corriger l'heure pour ne pas avoir de faille en changeant l'heure de son telephone
- [x] corriger l'affichage jusqu'à 20h dans l'agenda

## Implémentation autre
- [x] supprimer client habituel 4 semaines
- [x] Ajouter séances habituelles dans nouveau client
- [x] Ajouter fonction ajout séances dans fiche client
- [x] Ajouter fonction modification (ou ajouts) séances habituelles dans fiche client
- [ ] ajout bouton pour afficher tout l'historique d'un client dans la fiche client
- [x] Gerer le bouton si il y a déjà une habitude ou non pour le bouton dans la fiche client
- [x] ajout nombre de séances restantes dans après check in (borne : page borne_succes.html ; check-in manuel /presence : pop-up de confirmation)
- [ ] ajout de suppression client
- [x] implémentation des cookis clients 

## Vérifications
- [ ] Vérifier que les séances du mois sont correctes

## Optionnel
- [ ] Ajouter un calendrier pour choisir les séances habituelles dans nouveau clients
- [ ] Ajouter une section commantaires dans l'agenda
- [ ] Ajouter une colonne dernière séance dans la gestion client
- [ ] Rectifier habitude en inscrit (code)
- [ ] présence prévue dans agenda

## Personalisations
- [x] Personnaliser les noms dans les pop up de l'agenda
- [x] Modifier l'emplacement du bouton d'ajout de séances dans la fiche client

## Comprehension du code
- [ ] Comprendre le code de route de la pop up dans l'agnda 
- [ ] Comprendre le code html et css de l'agenda