"""
🔐 Anchor Vault — Générateur de mots de passe sécurisé
Stack : Python 3.10+ | Tkinter | secrets | math | hashlib | threading | requests
Version : 4.0 — Feature 1 (entropie + crack time) + Feature 2 (identicon) + Feature 3 (HIBP)
"""

import hashlib
import math
import secrets
import string
import threading
import tkinter as tk

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIQUE DE GÉNÉRATION
# ══════════════════════════════════════════════════════════════════════════════

def generer_mot_de_passe(longueur, majuscules, minuscules, chiffres, symboles):
    pool = ""
    garantis = []

    if majuscules:
        pool += string.ascii_uppercase
        garantis.append(secrets.choice(string.ascii_uppercase))
    if minuscules:
        pool += string.ascii_lowercase
        garantis.append(secrets.choice(string.ascii_lowercase))
    if chiffres:
        pool += string.digits
        garantis.append(secrets.choice(string.digits))
    if symboles:
        pool += string.punctuation
        garantis.append(secrets.choice(string.punctuation))

    if not pool:
        return None

    reste = longueur - len(garantis)
    mdp = garantis + [secrets.choice(pool) for _ in range(reste)]
    secrets.SystemRandom().shuffle(mdp)
    return "".join(mdp)


def evaluer_force(longueur, majuscules, minuscules, chiffres, symboles):
    """Retourne (label, couleur, largeur_barre%) selon les critères."""
    types_actifs = sum([majuscules, minuscules, chiffres, symboles])

    if longueur < 8 or types_actifs == 1:
        return "😟  Très faible", "#f87171", 0.15
    elif longueur < 12 or types_actifs == 2:
        return "😐  Faible",      "#fb923c", 0.40
    elif longueur < 16 or types_actifs == 3:
        return "🙂  Fort",        "#facc15", 0.70
    else:
        return "😎  Très fort",   "#4ade80", 1.00


# ══════════════════════════════════════════════════════════════════════════════
#  FEATURE 1 — ENTROPIE + TEMPS DE CRACKAGE + ANALOGIES FUN
# ══════════════════════════════════════════════════════════════════════════════

VITESSE_GPU = 10_000_000_000  # RTX 4090 : ~10^10 tentatives/sec (SHA-1)


def calculer_entropie(longueur, majuscules, minuscules, chiffres, symboles):
    alphabet = 0
    if majuscules: alphabet += 26
    if minuscules: alphabet += 26
    if chiffres:   alphabet += 10
    if symboles:   alphabet += 32
    if alphabet == 0:
        return 0.0
    return longueur * math.log2(alphabet)


def calculer_temps_crack(entropie_bits):
    if entropie_bits <= 0:
        return 0
    if entropie_bits > 300:
        return float("inf")
    return (2 ** entropie_bits / 2) / VITESSE_GPU


def formater_temps(secondes):
    """Retourne (durée_formatée, analogie_fun, couleur_hex)."""
    if secondes == float("inf"):
        return "∞ infini", "🌌  Plus long que l'âge de l'Univers × 1 000", "#4ade80"

    M = 60; H = 3_600; J = 86_400; MO = 2_592_000
    AN = 31_536_000; SC = AN*100; ML = AN*1_000
    MIL = AN*1_000_000; MLD = AN*1_000_000_000

    if secondes < 1:
        return "< 1 seconde",  "💀  Craqué instantanément — n'utilise JAMAIS ce mot de passe", "#f87171"
    elif secondes < M:
        s = int(secondes)
        return f"{s} seconde{'s' if s>1 else ''}", "😱  Craqué avant ta prochaine inspiration", "#f87171"
    elif secondes < H:
        m = int(secondes//M)
        return f"{m} minute{'s' if m>1 else ''}", "☕  Craqué avant que ton café refroidisse", "#fb923c"
    elif secondes < J:
        h = int(secondes//H)
        return f"{h} heure{'s' if h>1 else ''}", "📺  Craqué en moins d'une journée de binge-watching", "#fb923c"
    elif secondes < MO:
        j = int(secondes//J)
        return f"{j} jour{'s' if j>1 else ''}", "📅  Craqué dans le mois — trop court !", "#fb923c"
    elif secondes < AN:
        mo = int(secondes//MO)
        return f"{mo} mois", "🗓️  Craqué dans l'année — encore insuffisant", "#facc15"
    elif secondes < SC:
        a = int(secondes//AN)
        return f"{a} an{'s' if a>1 else ''}", "🧓  Craqué de ton vivant… à changer !", "#facc15"
    elif secondes < ML:
        s = int(secondes//SC)
        return f"{s} siècle{'s' if s>1 else ''}", "🏛️  Plus long que l'Empire Romain complet", "#4ade80"
    elif secondes < MIL:
        m = int(secondes//ML)
        return f"{m} millénaire{'s' if m>1 else ''}", "🦕  L'humanité n'existait pas encore", "#4ade80"
    elif secondes < MLD:
        m = int(secondes//MIL)
        return f"{m} million{'s' if m>1 else ''} d'années", "🌍  Plus vieux que les dinosaures", "#4ade80"
    else:
        m = int(secondes//MLD)
        if m < 14:
            return f"{m} milliard{'s' if m>1 else ''} d'années", "💫  Presque aussi vieux que l'Univers", "#4ade80"
        return f"{m} milliards d'années", "🌌  Plus vieux que l'Univers — tu es intouchable", "#4ade80"


# ══════════════════════════════════════════════════════════════════════════════
#  FEATURE 2 — IDENTICON : ADN VISUEL DU MOT DE PASSE
# ══════════════════════════════════════════════════════════════════════════════

IDENTICON_GRID   = 5
IDENTICON_CELL   = 18
IDENTICON_PAD    = 5
IDENTICON_SIZE   = IDENTICON_GRID * IDENTICON_CELL + IDENTICON_PAD * 2  # 100px


def _hex_couleur(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def _couleur_complementaire(r, g, b):
    rc = (r + 128) % 256
    gc = (g + 128) % 256
    bc = (b + 128) % 256
    luminosite = 0.299 * rc + 0.587 * gc + 0.114 * bc
    if luminosite < 30:
        rc, gc, bc = 28, 28, 45
    return rc, gc, bc


def generer_identicon(mdp, canvas):
    canvas.delete("all")

    if not mdp:
        bg_vide = "#1e1e30"
        canvas.configure(bg=bg_vide)
        canvas.create_text(
            IDENTICON_SIZE // 2, IDENTICON_SIZE // 2,
            text="?", fill="#3d3d5c",
            font=("Consolas", 28, "bold")
        )
        return

    h = hashlib.sha256(mdp.encode("utf-8")).digest()

    r, g, b = h[0], h[1], h[2]
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    if max_c - min_c < 60:
        dominant = [r, g, b].index(max_c)
        palette = [r, g, b]
        palette[dominant] = min(255, palette[dominant] + 80)
        palette[(dominant + 1) % 3] = max(0, palette[(dominant + 1) % 3] - 40)
        r, g, b = palette

    couleur_active = _hex_couleur(r, g, b)
    rc, gc, bc = _couleur_complementaire(r, g, b)
    couleur_fond = _hex_couleur(rc, gc, bc)
    canvas.configure(bg=couleur_fond)

    grille = [[False] * IDENTICON_GRID for _ in range(IDENTICON_GRID)]
    bit_index = 0
    for ligne in range(IDENTICON_GRID):
        for col in range(3):
            octet = h[3 + bit_index // 8]
            bit   = (octet >> (bit_index % 8)) & 1
            grille[ligne][col] = bool(bit)
            bit_index += 1

    for ligne in range(IDENTICON_GRID):
        grille[ligne][3] = grille[ligne][1]
        grille[ligne][4] = grille[ligne][0]

    for ligne in range(IDENTICON_GRID):
        for col in range(IDENTICON_GRID):
            x1 = IDENTICON_PAD + col  * IDENTICON_CELL
            y1 = IDENTICON_PAD + ligne * IDENTICON_CELL
            x2 = x1 + IDENTICON_CELL - 1
            y2 = y1 + IDENTICON_CELL - 1
            fill = couleur_active if grille[ligne][col] else couleur_fond
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")


# ══════════════════════════════════════════════════════════════════════════════
#  FEATURE 3 — HAVEIBEENPWNED : VÉRIFICATION K-ANONYMITY
# ══════════════════════════════════════════════════════════════════════════════
#
#  Principe k-anonymity (Troy Hunt / HIBP) :
#  1. SHA-1(mdp) → ex: "A94F2B8C3D1E..."
#  2. On envoie UNIQUEMENT les 5 premiers chars → "A94F2"
#  3. L'API répond avec TOUS les suffixes dont le hash commence par "A94F2"
#  4. On cherche LOCALEMENT si notre suffixe "B8C3D..." est dans la liste
#  5. Résultat : 0% du vrai mot de passe ne quitte l'appareil ✅
#
#  Le check tourne dans un thread séparé pour ne pas bloquer l'UI Tkinter.
# ══════════════════════════════════════════════════════════════════════════════

HIBP_URL = "https://api.pwnedpasswords.com/range/{}"
HIBP_TIMEOUT = 3  # secondes


def verifier_hibp(mdp, callback):
    """
    Lance la vérification HIBP en arrière-plan.
    callback(résultat) est appelé dans le thread principal via root.after().

    Valeurs de résultat :
      -2  → requests non installé
      -1  → erreur réseau / timeout
       0  → propre (non trouvé dans les leaks)
      >0  → nombre de fois trouvé dans les leaks
    """
    if not REQUESTS_AVAILABLE:
        callback(-2)
        return

    def _worker():
        try:
            sha1 = hashlib.sha1(mdp.encode("utf-8")).hexdigest().upper()
            prefix, suffix = sha1[:5], sha1[5:]
            r = requests.get(
                HIBP_URL.format(prefix),
                timeout=HIBP_TIMEOUT,
                headers={"Add-Padding": "true"}   # meilleure confidentialité
            )
            r.raise_for_status()
            for ligne in r.text.splitlines():
                hash_partiel, count = ligne.split(":")
                if hash_partiel.strip() == suffix:
                    callback(int(count.strip()))
                    return
            callback(0)
        except Exception:
            callback(-1)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()


# ══════════════════════════════════════════════════════════════════════════════
#  INTERFACE GRAPHIQUE
# ══════════════════════════════════════════════════════════════════════════════

class AnchorVaultApp:

    C = {
        "bg":            "#1e1e2e",
        "surface":       "#2a2a3e",
        "surface2":      "#23233a",
        "border":        "#3d3d5c",
        "primary":       "#7c6af7",
        "primary_hover": "#6a58e0",
        "success":       "#4ade80",
        "warning":       "#facc15",
        "error":         "#f87171",
        "text":          "#e2e2f0",
        "text_muted":    "#9898b0",
        "input_bg":      "#12121f",
        "bar_bg":        "#12121f",
    }

    LARGEUR_FENETRE = 480
    HAUTEUR_FENETRE = 1020   # +140px pour la carte HIBP

    def __init__(self, root):
        self.root = root
        self._dernier_mdp_hibp = ""   # pour éviter les vérifs en double
        self._configurer_fenetre()
        self._construire_ui()
        self._mettre_a_jour_force()

    def _configurer_fenetre(self):
        self.root.title("Anchor Vault v4")
        w, h = self.LARGEUR_FENETRE, self.HAUTEUR_FENETRE
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.configure(bg=self.C["bg"])

    def _construire_ui(self):
        c = self.C
        PX = 24

        # ── Titre ────────────────────────────────────────────────────────
        tk.Label(
            self.root, text="🔐  Anchor Vault",
            font=("Segoe UI", 20, "bold"),
            fg=c["primary"], bg=c["bg"]
        ).pack(pady=(22, 3))

        tk.Label(
            self.root, text="Générateur de mots de passe sécurisé",
            font=("Segoe UI", 10),
            fg=c["text_muted"], bg=c["bg"]
        ).pack(pady=(0, 14))

        # ── Carte 1 : options ──────────────────────────────────────────────
        carte1 = tk.Frame(self.root, bg=c["surface"],
                          highlightbackground=c["border"], highlightthickness=1)
        carte1.pack(fill="x", padx=PX)
        inner1 = tk.Frame(carte1, bg=c["surface"])
        inner1.pack(fill="x", padx=18, pady=16)

        self.var_longueur = tk.IntVar(value=16)
        row_len = tk.Frame(inner1, bg=c["surface"])
        row_len.pack(fill="x", pady=(0, 4))
        tk.Label(row_len, text="Longueur", font=("Segoe UI", 10, "bold"),
                 fg=c["text"], bg=c["surface"]).pack(side="left")
        tk.Label(row_len, textvariable=self.var_longueur,
                 font=("Segoe UI", 10, "bold"),
                 fg=c["primary"], bg=c["surface"]).pack(side="right")

        tk.Scale(
            inner1, from_=4, to=64, orient="horizontal",
            variable=self.var_longueur,
            bg=c["surface"], fg=c["text_muted"],
            troughcolor=c["border"], activebackground=c["primary"],
            highlightthickness=0, bd=0, showvalue=False, length=400,
            command=lambda _: self._mettre_a_jour_force()
        ).pack(fill="x", pady=(0, 12))

        tk.Frame(inner1, bg=c["border"], height=1).pack(fill="x", pady=(0, 12))

        tk.Label(inner1, text="Types de caractères",
                 font=("Segoe UI", 10, "bold"),
                 fg=c["text"], bg=c["surface"]).pack(anchor="w", pady=(0, 8))

        self.var_maj = tk.BooleanVar(value=True)
        self.var_min = tk.BooleanVar(value=True)
        self.var_chf = tk.BooleanVar(value=True)
        self.var_sym = tk.BooleanVar(value=True)

        options = [
            ("Majuscules  (A–Z)", self.var_maj),
            ("Minuscules  (a–z)", self.var_min),
            ("Chiffres      (0–9)", self.var_chf),
            ("Symboles  (!@#$…)", self.var_sym),
        ]
        grille = tk.Frame(inner1, bg=c["surface"])
        grille.pack(fill="x")
        for i, (label, var) in enumerate(options):
            tk.Checkbutton(
                grille, text=label, variable=var,
                font=("Segoe UI", 9),
                fg=c["text"], bg=c["surface"],
                selectcolor=c["primary"],
                activebackground=c["surface"],
                activeforeground=c["text"],
                cursor="hand2",
                command=self._mettre_a_jour_force
            ).grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 16), pady=2)

        tk.Frame(inner1, bg=c["border"], height=1).pack(fill="x", pady=(14, 10))

        row_force = tk.Frame(inner1, bg=c["surface"])
        row_force.pack(fill="x", pady=(0, 6))
        tk.Label(row_force, text="Force du mot de passe",
                 font=("Segoe UI", 9, "bold"),
                 fg=c["text_muted"], bg=c["surface"]).pack(side="left")
        self.lbl_force = tk.Label(row_force, text="",
                                   font=("Segoe UI", 9, "bold"),
                                   fg=c["success"], bg=c["surface"])
        self.lbl_force.pack(side="right")

        self.canvas_barre = tk.Canvas(inner1, height=8, bg=c["bar_bg"],
                                       highlightthickness=0, bd=0)
        self.canvas_barre.pack(fill="x", pady=(0, 4))
        self.rect_barre = self.canvas_barre.create_rectangle(
            0, 0, 0, 8, fill=c["success"], outline=""
        )

        self.lbl_erreur = tk.Label(
            inner1, text="", font=("Segoe UI", 9),
            fg=c["error"], bg=c["surface"], height=1
        )
        self.lbl_erreur.pack(pady=(6, 0))

        self.btn_gen = tk.Button(
            inner1, text="⚡  Générer",
            font=("Segoe UI", 11, "bold"),
            fg="white", bg=c["primary"],
            activeforeground="white", activebackground=c["primary_hover"],
            relief="flat", cursor="hand2", pady=10, bd=0,
            command=self._on_generer
        )
        self.btn_gen.pack(fill="x", pady=(8, 0))

        # ── Carte 2 : résultat + identicon ───────────────────────────────
        tk.Frame(self.root, bg=c["bg"], height=14).pack()

        carte2 = tk.Frame(self.root, bg=c["surface"],
                          highlightbackground=c["border"], highlightthickness=1)
        carte2.pack(fill="x", padx=PX)
        inner2 = tk.Frame(carte2, bg=c["surface"])
        inner2.pack(fill="x", padx=18, pady=14)

        row_resultat = tk.Frame(inner2, bg=c["surface"])
        row_resultat.pack(fill="x")

        col_gauche = tk.Frame(row_resultat, bg=c["surface"])
        col_gauche.pack(side="left", fill="both", expand=True, padx=(0, 12))

        tk.Label(col_gauche, text="Mot de passe généré",
                 font=("Segoe UI", 9),
                 fg=c["text_muted"], bg=c["surface"]
                 ).pack(anchor="w", pady=(0, 6))

        champ_frame = tk.Frame(col_gauche, bg=c["input_bg"],
                               highlightbackground=c["border"], highlightthickness=1)
        champ_frame.pack(fill="x")
        self.var_resultat = tk.StringVar()
        tk.Entry(
            champ_frame, textvariable=self.var_resultat,
            font=("Consolas", 12), fg=c["success"],
            bg=c["input_bg"], insertbackground=c["text"],
            relief="flat", bd=8,
            state="readonly", readonlybackground=c["input_bg"]
        ).pack(fill="x")

        self.btn_copier = tk.Button(
            col_gauche, text="📋  Copier",
            font=("Segoe UI", 10),
            fg=c["text"], bg=c["border"],
            activeforeground="white", activebackground=c["primary"],
            relief="flat", cursor="hand2", pady=8, bd=0,
            command=self._on_copier
        )
        self.btn_copier.pack(fill="x", pady=(8, 0))

        col_droite = tk.Frame(row_resultat, bg=c["surface"])
        col_droite.pack(side="right", anchor="n")

        tk.Label(col_droite, text="ADN visuel",
                 font=("Segoe UI", 7),
                 fg=c["text_muted"], bg=c["surface"]).pack(pady=(0, 4))

        self.canvas_identicon = tk.Canvas(
            col_droite,
            width=IDENTICON_SIZE,
            height=IDENTICON_SIZE,
            bg="#1e1e30",
            highlightbackground=c["border"],
            highlightthickness=1,
            bd=0
        )
        self.canvas_identicon.pack()
        generer_identicon("", self.canvas_identicon)

        tk.Label(col_droite, text="unique par mdp",
                 font=("Segoe UI", 7),
                 fg=c["text_muted"], bg=c["surface"]).pack(pady=(4, 0))

        # ── Carte 3 : analyse de sécurité (Feature 1) ────────────────────
        tk.Frame(self.root, bg=c["bg"], height=14).pack()

        carte3 = tk.Frame(self.root, bg=c["surface2"],
                          highlightbackground=c["border"], highlightthickness=1)
        carte3.pack(fill="x", padx=PX)
        inner3 = tk.Frame(carte3, bg=c["surface2"])
        inner3.pack(fill="x", padx=18, pady=16)

        row_titre3 = tk.Frame(inner3, bg=c["surface2"])
        row_titre3.pack(fill="x", pady=(0, 12))
        tk.Label(row_titre3, text="🛡️  Analyse de sécurité",
                 font=("Segoe UI", 10, "bold"),
                 fg=c["text"], bg=c["surface2"]).pack(side="left")
        tk.Label(row_titre3, text=" CYBER ",
                 font=("Segoe UI", 7, "bold"),
                 fg=c["primary"], bg="#2e2a52",
                 padx=5, pady=2).pack(side="right")

        row_entropie = tk.Frame(inner3, bg=c["surface2"])
        row_entropie.pack(fill="x", pady=(0, 8))
        tk.Label(row_entropie, text="Entropie",
                 font=("Segoe UI", 9),
                 fg=c["text_muted"], bg=c["surface2"]).pack(side="left")
        self.lbl_entropie = tk.Label(
            row_entropie, text="— bits",
            font=("Consolas", 9, "bold"),
            fg=c["primary"], bg=c["surface2"]
        )
        self.lbl_entropie.pack(side="right")

        tk.Frame(inner3, bg=c["border"], height=1).pack(fill="x", pady=(0, 10))

        row_crack = tk.Frame(inner3, bg=c["surface2"])
        row_crack.pack(fill="x", pady=(0, 4))
        tk.Label(row_crack, text="⏱️  Temps de crack",
                 font=("Segoe UI", 9),
                 fg=c["text_muted"], bg=c["surface2"]).pack(side="left")
        self.lbl_temps = tk.Label(
            row_crack, text="—",
            font=("Segoe UI", 9, "bold"),
            fg=c["success"], bg=c["surface2"]
        )
        self.lbl_temps.pack(side="right")

        self.lbl_analogie = tk.Label(
            inner3, text="",
            font=("Segoe UI", 9, "italic"),
            fg=c["text_muted"], bg=c["surface2"],
            wraplength=410, justify="center"
        )
        self.lbl_analogie.pack(pady=(4, 0))

        tk.Frame(inner3, bg=c["border"], height=1).pack(fill="x", pady=(10, 6))
        tk.Label(
            inner3,
            text="⚡ Simulé sur RTX 4090 — attaque brute force (10¹⁰ essais/sec)",
            font=("Segoe UI", 7),
            fg=c["text_muted"], bg=c["surface2"]
        ).pack()

        # ── Carte 4 : HaveIBeenPwned (Feature 3) ─────────────────────────
        tk.Frame(self.root, bg=c["bg"], height=14).pack()

        carte4 = tk.Frame(self.root, bg=c["surface2"],
                          highlightbackground=c["border"], highlightthickness=1)
        carte4.pack(fill="x", padx=PX)
        inner4 = tk.Frame(carte4, bg=c["surface2"])
        inner4.pack(fill="x", padx=18, pady=16)

        # Titre de la carte
        row_titre4 = tk.Frame(inner4, bg=c["surface2"])
        row_titre4.pack(fill="x", pady=(0, 10))
        tk.Label(row_titre4, text="🔍  Vérification des leaks",
                 font=("Segoe UI", 10, "bold"),
                 fg=c["text"], bg=c["surface2"]).pack(side="left")
        tk.Label(row_titre4, text=" HIBP ",
                 font=("Segoe UI", 7, "bold"),
                 fg="#4ade80", bg="#1a2e1a",
                 padx=5, pady=2).pack(side="right")

        # Zone de statut (icône + message)
        self.lbl_hibp_statut = tk.Label(
            inner4, text="🔒  Génère un mot de passe pour vérifier",
            font=("Segoe UI", 10),
            fg=c["text_muted"], bg=c["surface2"],
            wraplength=410, justify="center"
        )
        self.lbl_hibp_statut.pack(pady=(0, 6))

        # Sous-texte pédagogique (explication k-anonymity)
        self.lbl_hibp_detail = tk.Label(
            inner4, text="",
            font=("Segoe UI", 8, "italic"),
            fg=c["text_muted"], bg=c["surface2"],
            wraplength=410, justify="center"
        )
        self.lbl_hibp_detail.pack()

        # Séparateur + explication permanente de la méthode
        tk.Frame(inner4, bg=c["border"], height=1).pack(fill="x", pady=(10, 8))
        tk.Label(
            inner4,
            text="🛡️ K-anonymity : seuls 5 chars du hash SHA-1 sont envoyés — le vrai mdp ne quitte jamais l'app",
            font=("Segoe UI", 7),
            fg=c["text_muted"], bg=c["surface2"],
            wraplength=410, justify="center"
        ).pack()

        # Espace bas
        tk.Frame(self.root, bg=c["bg"], height=18).pack()

    # ── Méthodes ────────────────────────────────────────────────────────────

    def _mettre_a_jour_force(self):
        longueur   = self.var_longueur.get()
        maj = self.var_maj.get()
        min_ = self.var_min.get()
        chf = self.var_chf.get()
        sym = self.var_sym.get()

        label, couleur, ratio = evaluer_force(longueur, maj, min_, chf, sym)
        self.lbl_force.config(text=label, fg=couleur)
        self.canvas_barre.update_idletasks()
        lw = self.canvas_barre.winfo_width()
        self.canvas_barre.coords(self.rect_barre, 0, 0, int(lw * ratio), 8)
        self.canvas_barre.itemconfig(self.rect_barre, fill=couleur)

        entropie = calculer_entropie(longueur, maj, min_, chf, sym)
        secondes = calculer_temps_crack(entropie)
        duree, analogie, couleur_crack = formater_temps(secondes)

        if entropie > 0:
            self.lbl_entropie.config(text=f"{entropie:.1f} bits")
            self.lbl_temps.config(text=duree, fg=couleur_crack)
            self.lbl_analogie.config(text=analogie, fg=couleur_crack)
        else:
            self.lbl_entropie.config(text="— bits")
            self.lbl_temps.config(text="—", fg=self.C["text_muted"])
            self.lbl_analogie.config(text="Coche au moins un type de caractère",
                                      fg=self.C["error"])

    def _on_generer(self):
        mdp = generer_mot_de_passe(
            self.var_longueur.get(),
            self.var_maj.get(), self.var_min.get(),
            self.var_chf.get(), self.var_sym.get()
        )
        if mdp is None:
            self.lbl_erreur.config(text="⚠️  Coche au moins un type de caractère !")
            self.var_resultat.set("")
            generer_identicon("", self.canvas_identicon)
            self._reset_hibp()
            return

        self.lbl_erreur.config(text="")
        self.var_resultat.set(mdp)
        self.btn_copier.config(text="📋  Copier",
                               fg=self.C["text"], bg=self.C["border"])

        # Feature 2 : identicon
        generer_identicon(mdp, self.canvas_identicon)

        # Feature 3 : check HIBP en arrière-plan
        self._lancer_hibp(mdp)

    def _reset_hibp(self):
        """Remet la carte HIBP à l'état initial."""
        self.lbl_hibp_statut.config(
            text="🔒  Génère un mot de passe pour vérifier",
            fg=self.C["text_muted"]
        )
        self.lbl_hibp_detail.config(text="")
        self._dernier_mdp_hibp = ""

    def _lancer_hibp(self, mdp):
        """Lance la vérification HIBP et affiche l'état 'vérification en cours'."""
        if mdp == self._dernier_mdp_hibp:
            return  # Pas de double vérification pour le même mdp
        self._dernier_mdp_hibp = mdp

        if not REQUESTS_AVAILABLE:
            self.lbl_hibp_statut.config(
                text="📦  Module 'requests' non installé",
                fg=self.C["warning"]
            )
            self.lbl_hibp_detail.config(
                text="Lance : pip install requests  puis relance l'app",
                fg=self.C["text_muted"]
            )
            return

        # Afficher l'état "en cours"
        self.lbl_hibp_statut.config(
            text="⏳  Vérification en cours…",
            fg=self.C["text_muted"]
        )
        self.lbl_hibp_detail.config(text="")

        # Callback appelé depuis le thread worker → on repasse dans le thread Tkinter
        def _callback(resultat):
            self.root.after(0, lambda: self._afficher_resultat_hibp(resultat, mdp))

        verifier_hibp(mdp, _callback)

    def _afficher_resultat_hibp(self, resultat, mdp_verifie):
        """
        Met à jour la carte HIBP avec le résultat.
        On vérifie que le mdp n'a pas changé entre temps.
        """
        # Si l'utilisateur a déjà généré un nouveau mdp, on ignore ce résultat
        if mdp_verifie != self._dernier_mdp_hibp:
            return

        if resultat == -2:
            # requests non installé (ne devrait pas arriver ici, mais par sécurité)
            self.lbl_hibp_statut.config(
                text="📦  Module 'requests' requis",
                fg=self.C["warning"]
            )
            self.lbl_hibp_detail.config(
                text="pip install requests",
                fg=self.C["text_muted"]
            )
        elif resultat == -1:
            self.lbl_hibp_statut.config(
                text="🔌  Vérification impossible (pas de connexion)",
                fg=self.C["warning"]
            )
            self.lbl_hibp_detail.config(
                text="Le mot de passe n'a pas été envoyé sur le réseau.",
                fg=self.C["text_muted"]
            )
        elif resultat == 0:
            self.lbl_hibp_statut.config(
                text="✅  Propre — non trouvé dans les bases de leaks",
                fg=self.C["success"]
            )
            self.lbl_hibp_detail.config(
                text="Ce mot de passe n'apparaît dans aucune fuite de données connue.",
                fg=self.C["text_muted"]
            )
        else:
            # Trouvé dans des leaks
            count_str = f"{resultat:,}".replace(",", " ")
            self.lbl_hibp_statut.config(
                text=f"⚠️  Trouvé {count_str} fois dans des leaks !",
                fg=self.C["error"]
            )
            self.lbl_hibp_detail.config(
                text="Ce mot de passe est compromis. Génères-en un nouveau.",
                fg=self.C["error"]
            )

    def _on_copier(self):
        mdp = self.var_resultat.get()
        if not mdp:
            return
        if CLIPBOARD_AVAILABLE:
            pyperclip.copy(mdp)
        else:
            self.root.clipboard_clear()
            self.root.clipboard_append(mdp)
            self.root.update()
        self.btn_copier.config(text="✅  Copié !",
                               fg="white", bg="#3aad6a")
        self.root.after(2000, lambda: self.btn_copier.config(
            text="📋  Copier", fg=self.C["text"], bg=self.C["border"]))


if __name__ == "__main__":
    root = tk.Tk()
    AnchorVaultApp(root)
    root.mainloop()
