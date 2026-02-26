import pandas as pd
import os

def init_db():
    if not os.path.exists('eleves.xlsx'):
        print("Création de la base de données eleves.xlsx...")
        df = pd.DataFrame([
            {"Nom": "Alice Dupont", "Email": "alice@ecole.fr", "Mot de passe": "password123", "Niveau_Classe": "4ème"},
            {"Nom": "Bob Martin", "Email": "bob@ecole.fr", "Mot de passe": "password123", "Niveau_Classe": "Seconde"},
            {"Nom": "Charlie Durand", "Email": "charlie@ecole.fr", "Mot de passe": "password123", "Niveau_Classe": "Terminale"}
        ])
        df.to_excel('eleves.xlsx', index=False)
        print("Base de données eleves.xlsx créée avec succès.")
    else:
        print("La base de données eleves.xlsx existe déjà.")

if __name__ == '__main__':
    init_db()
