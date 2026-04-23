# 🔐 Anchor Vault — Password Generator App
### Règles & Spécifications du Projet

---

## 🎯 Objectif du Projet

Créer une application de bureau avec interface graphique (GUI) en Python permettant de générer des mots de passe forts, personnalisables et sécurisés. Le projet est conçu comme un premier projet GitHub d'apprentissage complet, avec un code propre, versionné et documenté.

---

## 🧩 Fonctionnalités Obligatoires (Core Features)

| # | Fonctionnalité | Détails |
|---|---------------|---------|
| 1 | **Longueur personnalisable** | Curseur ou champ numérique — min 4, max 64 caractères |
| 2 | **Types de caractères** | Cases à cocher : Majuscules, Minuscules, Chiffres, Symboles |
| 3 | **Bouton "Générer"** | Déclenche la génération du mot de passe |
| 4 | **Affichage du résultat** | Champ texte en lecture seule affichant le mot de passe généré |
| 5 | **Bouton "Copier"** | Copie le mot de passe dans le presse-papier en un clic |

---

## 🔒 Règles de Sécurité

- Au moins **un type de caractère** doit être sélectionné avant de générer
- Utiliser exclusivement le module Python `secrets` (et **non** `random`) pour garantir une génération cryptographiquement sécurisée
- **Aucune donnée** ne doit être stockée, enregistrée, ni transmise — l'application est 100% locale et sans persistance

---

## 🐍 Règles Techniques

- **Langage :** Python 3.10+
- **Framework GUI :** `tkinter` (inclus nativement avec Python, aucune installation requise)
- **Modules autorisés :**
  - `tkinter` — interface graphique
  - `secrets` — génération sécurisée
  - `string` — jeux de caractères standards
  - `pyperclip` — copier dans le presse-papier *(seule dépendance externe)*
- **Structure :** Un seul fichier `main.py` pour garder le projet simple et lisible
- **Style de code :** Code commenté en français, bien indenté, accessible à un débutant

---

## 🎨 Règles d'Interface (UI)

- Fenêtre de taille **fixe** (ex : 420 × 360 px), non redimensionnable par l'utilisateur
- Police lisible, taille minimum **11pt**
- Boutons avec états visuellement distincts (actif / désactivé)
- **Message d'erreur** affiché dans l'interface si aucun type de caractère n'est sélectionné
- Bouton "Copier" avec **feedback visuel** temporaire (ex : texte devient "✅ Copié !" pendant 2 secondes)

---

## 📁 Structure du Projet GitHub

```
anchor-vault/
├── MainAnchorVault.py   # Code principal de l'application GUI
├── README.md            # Description, instructions d'installation et screenshot
├── requirements.txt     # Dépendances (pyperclip uniquement)
├── RULES.md             # Spécifications du projet
└── .gitignore           # Fichiers à ignorer
```

---

## 🚀 Règles de Versioning Git

- **1 fonctionnalité = 1 commit** (commits atomiques et descriptifs)
- Messages de commit en français, format conventionnel :
  - `feat: ajout du bouton copier`
  - `fix: correction message d'erreur si aucune option cochée`
  - `docs: mise à jour du README avec screenshot`
- **Branche principale :** `main`

---

## ✅ Critères de Complétion (Definition of Done)

- [ ] L'app se lance sans erreur avec `python MainAnchorVault.py`
- [ ] Les 5 fonctionnalités core sont implémentées et fonctionnelles
- [ ] Un message d'erreur s'affiche si aucune option n'est cochée
- [ ] Le code utilise `secrets` et non `random`
- [ ] Le code est versionné sur GitHub avec un historique de commits propre
- [ ] Le `README.md` explique comment installer et lancer l'app
- [ ] Un **screenshot** de l'app est intégré dans le `README.md`
- [ ] Un fichier `requirements.txt` liste les dépendances
