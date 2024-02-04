# create_repositories.py
import os
import django
import tempfile
import shutil
import zipfile
 
# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CKBProject.settings')
 
# Initialize Django
django.setup()
 
from github import Github
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from .models import Battle, Repository

def create_github_repository(tournament_name, battle_name, code_kata_zip):
   
    github_token = settings.GITHUB_ACCESS_TOKEN
    g = Github(github_token)
    user = g.get_user()
    repo_name = f"{battle_name}_{tournament_name}"
    repo = user.create_repo(repo_name)
    
    # Estrai i file dallo zip in una directory temporanea
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Estrai i file dallo zip
        with zipfile.ZipFile(code_kata_zip, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
        
        # Carica tutti i file estratti nella repository GitHub
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    content = f.read()
                    # Carica il file nella repository GitHub
                    if file == "python-app.yml":
                        file=".github/workflows/" + file
                    repo.create_file(file, "Upload code_kata file", content)
    return repo.html_url

def create_github_repositories():
    return