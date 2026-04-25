# Anchor Vault

> Generateur de mots de passe securise — application de bureau Python avec interface graphique.

![Anchor Vault Screenshot](https://raw.githubusercontent.com/okash99/anchor-vault/main/screenshotanchor.png)

---

## Fonctionnalites

### Generation
- **Longueur personnalisable** — de 4 a 64 caracteres via un curseur
- **Types de caracteres au choix** — Majuscules, Minuscules, Chiffres, Symboles
- **Generation instantanee** — securisee avec le module cryptographique `secrets`
- **Copie en un clic** — avec feedback visuel
- **Champ editable** — tu peux aussi saisir ton propre mot de passe pour l'analyser

### Analyse de securite (v4)
- **Entropie en bits** — calcul precis selon la longueur et les types de caracteres
- **Temps de crackage GPU** — estimation realiste sur RTX 4090 (10^10 essais/sec)
- **Analogies memorables** — "Plus long que l'Empire Romain", "Craque avant ton cafe", etc.

### Identicon visuel (v4)
- **ADN visuel unique** — chaque mot de passe genere une image 5x5 symetrique basee sur son hash SHA-256
- Affichage en temps reel : deux mots de passe proches donnent des images radicalement differentes
- Inspiration : GitHub Identicons, appliquee pour la premiere fois a un generateur de mots de passe Python/Tkinter

### Verification des leaks (v4)
- **HaveIBeenPwned** — verifie si le mot de passe a ete trouve dans des bases de donnees volees
- **K-anonymity** : seuls les 5 premiers caracteres du hash SHA-1 sont envoyes — le vrai mot de passe ne quitte jamais l'application
- Verification automatique avec debounce (600ms) a chaque frappe

---

## Securite

Ce projet utilise le module Python [`secrets`](https://docs.python.org/3/library/secrets.html) plutot que `random`.  
`secrets` est concu pour generer des valeurs **cryptographiquement securisees**, adapte a la creation de mots de passe et de tokens.

> Aucune donnee n'est stockee, enregistree ou transmise en clair.  
> Le check HIBP utilise la technique k-anonymity : le serveur ne recoit jamais le mot de passe complet.

---

## Installation & Lancement

### Prerequis

- Python 3.10 ou superieur -> [Telecharger Python](https://www.python.org/downloads/)

### Etapes

```bash
# 1. Clone le repo
git clone https://github.com/okash99/anchor-vault.git
cd anchor-vault

# 2. Installe les dependances
pip install -r requirements.txt

# 3. Lance l'application
python MainAnchorVault.py
```

> `requests` est necessaire pour la verification HIBP.  
> `pyperclip` ameliore la compatibilite du presse-papier.  
> Sans eux, l'app fonctionne quand meme (verification HIBP desactivee, fallback presse-papier natif).

---

## Structure du projet

```
anchor-vault/
|-- MainAnchorVault.py      # Code principal (un seul fichier)
|-- requirements.txt        # Dependances Python
|-- RULES.md                # Specifications & regles du projet
|-- screenshotanchor.png    # Capture d'ecran de l'app
`-- README.md               # Ce fichier
```

---

## Stack technique

| Outil | Role |
|---|---|
| `Python 3.10+` | Langage principal |
| `tkinter` | Interface graphique (inclus nativement) |
| `secrets` | Generation cryptographiquement securisee |
| `hashlib` | SHA-256 (identicon) + SHA-1 (HIBP k-anonymity) |
| `math` | Calcul d'entropie |
| `threading` | Verification HIBP en arriere-plan (non bloquant) |
| `requests` | Appel API HaveIBeenPwned (dependance optionnelle) |
| `pyperclip` | Copie presse-papier (dependance optionnelle) |

---

## Utilisation

1. **Regle la longueur** avec le curseur (defaut : 16 caracteres)
2. **Coche les types de caracteres** souhaites
3. Clique sur **GENERER** — ou saisis ton propre mot de passe
4. Clique sur **COPIER** pour copier dans le presse-papier
5. Deplie **ANALYSE DE SECURITE** pour voir l'entropie et le temps de crackage
6. Deplie **VERIFICATION DES LEAKS** pour le check HaveIBeenPwned

---

## Historique des versions

| Version | Contenu |
|---|---|
| v1 | Generation basique, interface simple |
| v2 | Barre de force, curseur longueur, validation |
| v3 | Interface redesignee (dark header + cartes), champ editable, placeholder, sections accordeon |
| v4 | Identicon SHA-256, temps de crackage GPU + analogies, check HaveIBeenPwned k-anonymity |

---

## Auteur

Projet realise par **okash99** — premier projet GitHub  
Apprentissage Python | GUI Tkinter | Bonnes pratiques de securite

---

## Licence

Ce projet est open source sous licence MIT — libre d'utilisation et de modification.
