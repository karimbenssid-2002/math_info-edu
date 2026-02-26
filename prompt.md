> **Rôle :**
> Agis comme un développeur web Full-Stack expert en Python. Ton objectif est de me fournir le code complet pour créer une plateforme éducative sécurisée pour mes élèves.
> **Stack Technique :**
> * Backend : Python avec Flask (ou FastAPI).
> * Base de données utilisateurs : Un simple fichier Excel (`eleves.xlsx`) lu avec `pandas`.
> * Frontend : HTML, CSS, rendu des fichiers Markdown en HTML.
> * Exécution de code : Intégration de PyScript dans le frontend pour les exercices Python.
> 
> 
> **Fonctionnalités requises :**
> 1. **Authentification :** Une page de connexion (Login / Mot de passe). Le backend doit vérifier ces informations en lisant le fichier `eleves.xlsx`.
> 2. **Gestion des droits d'accès :** Le fichier Excel contient les colonnes "Nom", "Email", "Mot de passe" et "Niveau_Classe". Un élève ne doit voir et accéder qu'aux cours qui correspondent à sa classe (ex: un élève de 4ème n'a pas accès au contenu de Seconde).
> 3. **Structure du contenu :** Le site a deux grandes sections (Mathématiques et Informatique). Chaque section liste les classes, et chaque classe liste ses chapitres. Les cours sont rédigés dans des fichiers `.md` locaux que le backend convertit en HTML pour l'affichage.
> 4. **Console interactive :** Dans la section Informatique, les pages doivent inclure un bloc PyScript permettant à l'élève d'écrire et d'exécuter du code Python directement dans son navigateur pour faire ses exercices.
> 
> 
> **Règles de sortie :**
> * Donne-moi l'arborescence complète et exacte du projet (dossiers statiques, templates, fichiers de cours, fichier Excel).
> * Fournis le code du fichier Python principal (ex: `app.py`) gérant les routes, la lecture de l'Excel et l'authentification.
> * Fournis un exemple de template HTML (avec Jinja2 si tu utilises Flask) pour afficher un cours en Markdown et le terminal PyScript.
> * Le code doit être clair, sécurisé (gestion des sessions) et massivement commenté pour que je puisse l'adapter facilement.
> 
> 

