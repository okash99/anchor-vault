# 🔐 Anchor Vault

> Générateur de mots de passe sécurisé — application de bureau Python avec interface graphique.

![Anchor Vault Screenshot](screenshotanchor.jpg)

---

## ✨ Fonctionnalités

- 🎚️ **Longueur personnalisable** — de 4 à 64 caractères via un curseur
- 🔡 **Types de caractères au choix** — Majuscules, Minuscules, Chiffres, Symboles
- ⚡ **Génération instantanée** — sécurisée avec le module cryptographique `secrets`
- 📋 **Copie en un clic** — avec feedback visuel ✅
- ⚠️ **Validation intégrée** — message d'erreur si aucune option n'est sélectionnée
- 🖥️ **Interface native** — fenêtre de bureau légère, aucune connexion internet requise

---

## 🛡️ Sécurité

Ce projet utilise le module Python [`secrets`](https://docs.python.org/3/library/secrets.html) plutôt que `random`.  
`secrets` est conçu pour générer des valeurs **cryptographiquement sécurisées**, adapté à la création de mots de passe et de tokens.

> ❌ Aucune donnée n'est stockée, enregistrée ou transmise. L'application est 100% locale.

---

## 🚀 Installation & Lancement

### Prérequis

- Python 3.10 ou supérieur → [Télécharger Python](https://www.python.org/downloads/)

### Étapes

```bash
# 1. Clone le repo
git clone https://github.com/okash99/anchor-vault.git
cd anchor-vault

# 2. Installe la dépendance (optionnelle, recommandée)
pip install pyperclip

# 3. Lance l'application
python MainAnchorVault.py
```

> 💡 `pyperclip` améliore la compatibilité du presse-papier sur tous les OS.  
> Sans lui, l'app fonctionne quand même grâce au fallback natif Tkinter.

---

## 🗂️ Structure du projet

```
anchor-vault/
├── MainAnchorVault.py      # Code principal de l'application
├── requirements.txt        # Dépendances Python
├── RULES.md                # Spécifications & règles du projet
├── screenshotanchor.jpg    # Capture d'écran de l'app
└── README.md               # Ce fichier
```

---

## 🧰 Stack technique

| Outil | Rôle |
|---|---|
| `Python 3.10+` | Langage principal |
| `tkinter` | Interface graphique (inclus nativement) |
| `secrets` | Génération cryptographiquement sécurisée |
| `string` | Jeux de caractères standards |
| `pyperclip` | Copie dans le presse-papier (dépendance optionnelle) |

---

## 📋 Utilisation

1. **Règle la longueur** avec le curseur (défaut : 16 caractères)
2. **Coche les types de caractères** souhaités
3. Clique sur **⚡ Générer**
4. Clique sur **📋 Copier** pour copier dans le presse-papier

---

## 👤 Auteur

Projet réalisé par **okash99** — premier projet GitHub 🎉  
Apprentissage Python | GUI Tkinter | Bonnes pratiques de sécurité

---

## 📄 Licence

Ce projet est open source sous licence MIT — libre d'utilisation et de modification.
