# Générateur de Devis — Application Web

Application Flask pour générer des devis professionnels en PDF (format FCFA).

## Structure
```
devis-app/
├── app.py              # Backend Flask + génération PDF
├── templates/
│   └── index.html      # Interface utilisateur
├── requirements.txt
├── render.yaml
└── Procfile
```

## Déploiement sur Render (gratuit)

### Étape 1 — Mettre le projet sur GitHub
1. Crée un compte sur https://github.com si pas encore fait
2. Crée un nouveau repository (ex: `generateur-devis`)
3. Upload tous les fichiers de ce dossier dans le repo

### Étape 2 — Déployer sur Render
1. Va sur https://render.com et crée un compte gratuit
2. Clique **New → Web Service**
3. Connecte ton compte GitHub
4. Sélectionne le repository `generateur-devis`
5. Render détecte automatiquement la config grâce à `render.yaml`
6. Clique **Create Web Service**
7. Attends 2-3 minutes → tu obtiens une URL publique du type :
   `https://generateur-devis.onrender.com`

### Test en local
```bash
pip install -r requirements.txt
python app.py
# Ouvre http://localhost:5000
```

## Fonctionnalités
- Saisie multi-sections avec lignes dynamiques
- Calcul automatique Qté × PU ou saisie directe du montant
- Aperçu avant génération
- Téléchargement PDF avec mise en forme professionnelle
- Format FCFA avec séparateurs de milliers
