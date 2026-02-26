import os
import markdown
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_in_production'

EXCEL_FILE = 'eleves.xlsx'
COURSES_DIR = 'cours'

def get_user(email, password):
    """Vérifie les informations de connexion à partir du fichier Excel."""
    if not os.path.exists(EXCEL_FILE):
        return None
    df = pd.read_excel(EXCEL_FILE)
    # Chercher correspondances
    user = df[(df['Email'] == email) & (df['Mot de passe'] == password)]
    if not user.empty:
        return user.iloc[0].to_dict()
    return None

def get_courses_for_class(niveau_classe):
    """
    Parcourt le dossier 'cours' et liste les cours disponibles 
    pour le niveau de l'élève.
    """
    courses = {'Mathématiques': [], 'Informatique': []}
    for matiere in courses.keys():
        path = os.path.join(COURSES_DIR, matiere, niveau_classe)
        if os.path.isdir(path):
            files = [f for f in os.listdir(path) if f.endswith('.md')]
            # Remove extension
            files_no_ext = [os.path.splitext(f)[0] for f in files]
            courses[matiere] = files_no_ext
    return courses

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    niveau_classe = session['user']['Niveau_Classe']
    courses = get_courses_for_class(niveau_classe)
    
    return render_template('index.html', user=session['user'], courses=courses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = get_user(email, password)
        if user:
            # Stockage des infos utiles dans la session
            session['user'] = {
                'Nom': user['Nom'],
                'Email': user['Email'],
                'Niveau_Classe': user['Niveau_Classe']
            }
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Email ou mot de passe incorrect.")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/cours/<matiere>/<chapitre>')
def view_course(matiere, chapitre):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    niveau_classe = session['user']['Niveau_Classe']
    
    # Sécurité: empêcher l'accès aux autres matières/fichiers
    if matiere not in ['Mathématiques', 'Informatique']:
        abort(404)
        
    # Vérifier que le fichier existe pour cette classe
    file_path = os.path.join(COURSES_DIR, matiere, niveau_classe, f"{chapitre}.md")
    if not os.path.isfile(file_path):
        abort(404, description="Cours introuvable ou vous n'y avez pas accès.")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content_md = f.read()
        
    # Conversion du markdown en HTML
    content_html = markdown.markdown(content_md, extensions=['fenced_code', 'tables', 'mdx_math'])
    
    # Savoir si on doit inclure le terminal PyScript
    is_informatique = (matiere == 'Informatique')
    
    return render_template(
        'course.html', 
        user=session['user'],
        matiere=matiere, 
        chapitre=chapitre, 
        content=content_html,
        is_informatique=is_informatique
    )

if __name__ == '__main__':
    # Initialise les dossiers au lancement si besoin
    os.makedirs(COURSES_DIR, exist_ok=True)
    for mat in ['Mathématiques', 'Informatique']:
        for niv in ['4ème', 'Seconde', 'Terminale']:
            os.makedirs(os.path.join(COURSES_DIR, mat, niv), exist_ok=True)
            
    app.run(debug=True, port=5000)
