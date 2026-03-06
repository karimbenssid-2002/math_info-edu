import os
import re
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
    Parcourt le dossier 'cours' et liste les cours et chapitres disponibles 
    pour le niveau de l'élève.
    """
    courses = {'Mathématiques': [], 'Informatique': []}
    for matiere in courses.keys():
        path = os.path.join(COURSES_DIR, matiere, niveau_classe)
        if os.path.isdir(path):
            items = []
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append({'type': 'chapter', 'name': item})
                elif os.path.isfile(item_path) and item.endswith('.md'):
                    items.append({'type': 'file', 'name': os.path.splitext(item)[0]})
            courses[matiere] = items
    return courses

@app.route('/chapitre/<matiere>/<nom_chapitre>')
def view_chapter(matiere, nom_chapitre):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    niveau_classe = session['user']['Niveau_Classe']
    
    if matiere not in ['Mathématiques', 'Informatique']:
        abort(404)
        
    chapter_path = os.path.join(COURSES_DIR, matiere, niveau_classe, nom_chapitre)
    if not os.path.isdir(chapter_path):
        abort(404, description="Chapitre introuvable.")
        
    vignettes = {}
    for item in sorted(os.listdir(chapter_path)):
        vignette_path = os.path.join(chapter_path, item)
        if os.path.isdir(vignette_path):
            files = []
            for f in sorted(os.listdir(vignette_path)):
                if f.endswith('.md'):
                    files.append(os.path.splitext(f)[0])
            vignettes[item] = files
            
    return render_template('chapter.html', user=session['user'], matiere=matiere, chapitre_nom=nom_chapitre, vignettes=vignettes)


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

@app.route('/cours/<matiere>/<path:chapitre>')
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
        
    # Pre-processing: ensure lists have a preceding blank line so they aren't rendered inline
    content_md = re.sub(r'([^\n])\n([*+\-] )', r'\1\n\n\2', content_md)
        
    # Conversion du markdown en HTML
    # Conversion du markdown en HTML avec l'extension TOC
    md = markdown.Markdown(
        extensions=['fenced_code', 'tables', 'mdx_math', 'sane_lists', 'md_in_html', 'toc'],
        extension_configs={
            'mdx_math': {'enable_dollar_delimiter': True},
            'toc': {'title': 'Sommaire'}
        }
    )
    content_html = md.convert(content_md)
    toc_html = md.toc # Contient uniquement le HTML du sommaire généré
    
    # Convert MathJax v2 script tags (generated by mdx_math) to MathJax v3 compatible brackets
    content_html = re.sub(r'<script type="math/tex">(.*?)</script>', r'\\(\1\\)', content_html, flags=re.DOTALL)
    content_html = re.sub(r'<script type="math/tex; mode=display">(.*?)</script>', r'\\[\1\\]', content_html, flags=re.DOTALL)
    
    # Vérifier s'il y a un PDF portant le même nom que le fichier markdown
    # (ex: "cours.md" → "cours.pdf")
    md_basename = os.path.splitext(os.path.basename(file_path))[0]
    pdf_candidate = os.path.join(os.path.dirname(file_path), md_basename + '.pdf')
    pdf_filename = (md_basename + '.pdf') if os.path.isfile(pdf_candidate) else None
                
    # Savoir si on doit inclure le terminal PyScript
    is_informatique = (matiere == 'Informatique')
    
    # Extraire le nom du chapitre parent (1er dossier du chemin)
    # Ex: "Chapitre 1 - Nombres relatifs/Exercices/cours" → "Chapitre 1 - Nombres relatifs"
    chapitre_parent = chapitre.split('/')[0]
    
    return render_template(
        'course.html', 
        user=session['user'],
        matiere=matiere, 
        chapitre=chapitre, 
        chapitre_parent=chapitre_parent,
        content=content_html,
        toc=toc_html,
        is_informatique=is_informatique,
        pdf_filename=pdf_filename
    )

from flask import send_from_directory

@app.route('/download_pdf/<matiere>/<path:chapitre>/<filename>')
def download_pdf(matiere, chapitre, filename):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    niveau_classe = session['user']['Niveau_Classe']
    chapitre_dir = os.path.dirname(chapitre) 
    
    directory = os.path.join(COURSES_DIR, matiere, niveau_classe, chapitre_dir)
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/cours_media/<matiere>/<path:filepath>')
def cours_media(matiere, filepath):
    """Sert les images et fichiers statiques stockés dans les dossiers de cours."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if matiere not in ['Mathématiques', 'Informatique']:
        abort(404)
    
    niveau_classe = session['user']['Niveau_Classe']
    
    # Le filepath inclut le sous-chemin depuis le dossier de niveau (ex: "Chapitre 2 - Pythagore/Exercices/image_1.png")
    # On sépare le dossier du nom de fichier
    file_dir = os.path.dirname(os.path.join(COURSES_DIR, matiere, niveau_classe, filepath))
    filename = os.path.basename(filepath)
    
    # Sécurité: vérifier que le chemin est bien dans COURSES_DIR
    abs_dir = os.path.realpath(file_dir)
    courses_abs = os.path.realpath(COURSES_DIR)
    if not abs_dir.startswith(courses_abs):
        abort(403)
    
    return send_from_directory(file_dir, filename)

@app.route('/dump_dom', methods=['POST'])
def dump_dom():
    with open("dom_dump.txt", "w", encoding="utf-8") as f:
        f.write(request.get_data(as_text=True))
    return "OK"

if __name__ == '__main__':
    # Initialise les dossiers au lancement si besoin
    os.makedirs(COURSES_DIR, exist_ok=True)
    for mat in ['Mathématiques', 'Informatique']:
        for niv in ['4ème', 'Seconde', 'Terminale']:
            os.makedirs(os.path.join(COURSES_DIR, mat, niv), exist_ok=True)
            
    app.run(debug=True, port=5000)
