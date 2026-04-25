"""
🔐 Anchor Vault — Générateur de mots de passe sécurisé
Stack : Python 3.10+ | Tkinter | secrets | math | hashlib | threading | requests
Version : 4.1 — Fenêtre scrollable + sections expandables (accordion)
"""

import hashlib
import math
import secrets
import string
import threading
import tkinter as tk
from tkinter import ttk

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

VITESSE_GPU = 10_000_000_000


def calculer_entropie(longueur, majuscules, minuscules, chiffres, symboles):
    alphabet = 0
    if majuscules: alphabet += 26
    if minuscules: alphabet += 26
    if chiffres:   alphabet += 10
    if symboles:   alphabet += 32
    return longueur * math.log2(alphabet) if alphabet > 0 else 0.0


def calculer_temps_crack(entropie_bits):
    if entropie_bits <= 0: return 0
    if entropie_bits > 300: return float("inf")
    return (2 ** entropie_bits / 2) / VITESSE_GPU


def formater_temps(secondes):
    if secondes == float("inf"):
        return "∞ infini", "🌌  Plus long que l'âge de l'Univers × 1 000", "#4ade80"
    M=60; H=3600; J=86400; MO=2592000; AN=31536000
    SC=AN*100; ML=AN*1000; MIL=AN*1000000; MLD=AN*1000000000
    if secondes < 1:    return "< 1 seconde",  "💀  Craqué instantanément", "#f87171"
    elif secondes < M:  s=int(secondes); return f"{s}s", "😱  Craqué avant ta prochaine inspiration", "#f87171"
    elif secondes < H:  m=int(secondes//M); return f"{m} min", "☕  Craqué avant que ton café refroidisse", "#fb923c"
    elif secondes < J:  h=int(secondes//H); return f"{h}h", "📺  Moins d'une journée de binge-watching", "#fb923c"
    elif secondes < MO: j=int(secondes//J); return f"{j}j", "📅  Craqué dans le mois", "#fb923c"
    elif secondes < AN: mo=int(secondes//MO); return f"{mo} mois", "🗓️  Craqué dans l'année", "#facc15"
    elif secondes < SC: a=int(secondes//AN); return f"{a} ans", "🧓  Craqué de ton vivant", "#facc15"
    elif secondes < ML: s=int(secondes//SC); return f"{s} siècles", "🏛️  Plus long que l'Empire Romain", "#4ade80"
    elif secondes < MIL: m=int(secondes//ML); return f"{m} millénaires", "🦕  L'humanité n'existait pas", "#4ade80"
    elif secondes < MLD: m=int(secondes//MIL); return f"{m}M d'années", "🌍  Plus vieux que les dinos", "#4ade80"
    else:
        m=int(secondes//MLD)
        return f"{m}Mrd d'années", "🌌  Plus vieux que l'Univers", "#4ade80"


# ══════════════════════════════════════════════════════════════════════════════
#  FEATURE 2 — IDENTICON
# ══════════════════════════════════════════════════════════════════════════════

IDENTICON_GRID = 5
IDENTICON_CELL = 18
IDENTICON_PAD  = 5
IDENTICON_SIZE = IDENTICON_GRID * IDENTICON_CELL + IDENTICON_PAD * 2


def _hex_couleur(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def _couleur_complementaire(r, g, b):
    rc, gc, bc = (r+128)%256, (g+128)%256, (b+128)%256
    if 0.299*rc + 0.587*gc + 0.114*bc < 30:
        rc, gc, bc = 28, 28, 45
    return rc, gc, bc

def generer_identicon(mdp, canvas):
    canvas.delete("all")
    if not mdp:
        canvas.configure(bg="#1e1e30")
        canvas.create_text(IDENTICON_SIZE//2, IDENTICON_SIZE//2,
                           text="?", fill="#3d3d5c", font=("Consolas", 28, "bold"))
        return
    h = hashlib.sha256(mdp.encode("utf-8")).digest()
    r, g, b = h[0], h[1], h[2]
    if max(r,g,b) - min(r,g,b) < 60:
        d = [r,g,b].index(max(r,g,b))
        p = [r,g,b]; p[d]=min(255,p[d]+80); p[(d+1)%3]=max(0,p[(d+1)%3]-40)
        r,g,b = p
    couleur_active = _hex_couleur(r,g,b)
    rc,gc,bc = _couleur_complementaire(r,g,b)
    canvas.configure(bg=_hex_couleur(rc,gc,bc))
    grille = [[False]*IDENTICON_GRID for _ in range(IDENTICON_GRID)]
    bi = 0
    for row in range(IDENTICON_GRID):
        for col in range(3):
            octet = h[3 + bi//8]
            grille[row][col] = bool((octet >> (bi%8)) & 1)
            bi += 1
    for row in range(IDENTICON_GRID):
        grille[row][3] = grille[row][1]
        grille[row][4] = grille[row][0]
    for row in range(IDENTICON_GRID):
        for col in range(IDENTICON_GRID):
            x1 = IDENTICON_PAD + col*IDENTICON_CELL
            y1 = IDENTICON_PAD + row*IDENTICON_CELL
            fill = couleur_active if grille[row][col] else _hex_couleur(rc,gc,bc)
            canvas.create_rectangle(x1, y1, x1+IDENTICON_CELL-1, y1+IDENTICON_CELL-1,
                                    fill=fill, outline="")


# ══════════════════════════════════════════════════════════════════════════════
#  FEATURE 3 — HAVEIBEENPWNED K-ANONYMITY
# ══════════════════════════════════════════════════════════════════════════════

HIBP_URL     = "https://api.pwnedpasswords.com/range/{}"
HIBP_TIMEOUT = 3


def verifier_hibp(mdp, callback):
    if not REQUESTS_AVAILABLE:
        callback(-2); return
    def _worker():
        try:
            sha1 = hashlib.sha1(mdp.encode("utf-8")).hexdigest().upper()
            prefix, suffix = sha1[:5], sha1[5:]
            r = requests.get(HIBP_URL.format(prefix), timeout=HIBP_TIMEOUT,
                             headers={"Add-Padding": "true"})
            r.raise_for_status()
            for ligne in r.text.splitlines():
                hp, count = ligne.split(":")
                if hp.strip() == suffix:
                    callback(int(count.strip())); return
            callback(0)
        except Exception:
            callback(-1)
    threading.Thread(target=_worker, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
#  COMPOSANT : SECTION EXPANDABLE (ACCORDION)
# ══════════════════════════════════════════════════════════════════════════════

class SectionExpandable(tk.Frame):
    """
    Carte accordion réutilisable.
    - En-tête cliquable avec titre, badge optionnel et chevron ▶/▼
    - Corps masquable d'un clic
    - S'intègre dans un conteneur scrollable
    """

    C = {
        "bg":         "#1e1e2e",
        "surface":    "#2a2a3e",
        "surface2":   "#23233a",
        "border":     "#3d3d5c",
        "primary":    "#7c6af7",
        "text":       "#e2e2f0",
        "text_muted": "#9898b0",
        "header_hover": "#32324a",
    }

    def __init__(self, parent, titre, badge_texte=None, badge_couleur=None,
                 badge_bg=None, ouvert=True, couleur_surface="surface",
                 on_toggle=None, **kwargs):
        c = self.C
        bg_surface = c[couleur_surface]
        super().__init__(parent, bg=bg_surface,
                         highlightbackground=c["border"], highlightthickness=1,
                         **kwargs)

        self._ouvert    = ouvert
        self._on_toggle = on_toggle
        self._bg        = bg_surface

        # ─ En-tête (toujours visible) ────────────────────────────────
        self._header = tk.Frame(self, bg=bg_surface, cursor="hand2")
        self._header.pack(fill="x", padx=14, pady=(10, 10))

        self._lbl_chevron = tk.Label(
            self._header,
            text="▼" if ouvert else "▶",
            font=("Segoe UI", 8),
            fg=c["text_muted"], bg=bg_surface
        )
        self._lbl_chevron.pack(side="left", padx=(0, 6))

        tk.Label(
            self._header, text=titre,
            font=("Segoe UI", 10, "bold"),
            fg=c["text"], bg=bg_surface
        ).pack(side="left")

        if badge_texte:
            tk.Label(
                self._header,
                text=f" {badge_texte} ",
                font=("Segoe UI", 7, "bold"),
                fg=badge_couleur or c["primary"],
                bg=badge_bg or "#2e2a52",
                padx=4, pady=2
            ).pack(side="right")

        # ─ Corps (masquable) ───────────────────────────────────────
        self._separateur = tk.Frame(self, bg=c["border"], height=1)
        self._corps = tk.Frame(self, bg=bg_surface)
        self._corps.pack(fill="x", padx=18, pady=(0, 16))

        if not ouvert:
            self._corps.pack_forget()
        else:
            self._separateur.pack(fill="x")

        # Binding clics sur l'en-tête
        for widget in (self._header, self._lbl_chevron):
            widget.bind("<Button-1>", self._basculer)
            widget.bind("<Enter>",    lambda e: self._header.config(bg=c["header_hover"]))
            widget.bind("<Leave>",    lambda e: self._header.config(bg=bg_surface))

    @property
    def corps(self):
        """Le Frame intérieur où placer le contenu de la section."""
        return self._corps

    def _basculer(self, _event=None):
        self._ouvert = not self._ouvert
        if self._ouvert:
            self._separateur.pack(fill="x")
            self._corps.pack(fill="x", padx=18, pady=(0, 16))
            self._lbl_chevron.config(text="▼")
        else:
            self._separateur.pack_forget()
            self._corps.pack_forget()
            self._lbl_chevron.config(text="▶")
        if self._on_toggle:
            self._on_toggle()


# ══════════════════════════════════════════════════════════════════════════════
#  INTERFACE GRAPHIQUE PRINCIPALE
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

    LARGEUR  = 480
    HAUTEUR  = 620   # fenêtre compacte — scroll pour le reste

    def __init__(self, root):
        self.root = root
        self._dernier_mdp_hibp = ""
        self._configurer_fenetre()
        self._construire_ui()
        self._mettre_a_jour_force()

    # ── Fenêtre ─────────────────────────────────────────────────────────

    def _configurer_fenetre(self):
        self.root.title("Anchor Vault v4")
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw - self.LARGEUR)  // 2
        y  = (sh - self.HAUTEUR) // 2
        self.root.geometry(f"{self.LARGEUR}x{self.HAUTEUR}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.configure(bg=self.C["bg"])

    # ── Zone scrollable ────────────────────────────────────────────────

    def _construire_ui(self):
        c = self.C

        # ─ Conteneur principal avec scrollbar ─────────────────────────
        outer = tk.Frame(self.root, bg=c["bg"])
        outer.pack(fill="both", expand=True)

        self._canvas_scroll = tk.Canvas(
            outer, bg=c["bg"], highlightthickness=0, bd=0
        )
        scrollbar = ttk.Scrollbar(
            outer, orient="vertical", command=self._canvas_scroll.yview
        )
        self._canvas_scroll.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._canvas_scroll.pack(side="left", fill="both", expand=True)

        # Frame intérieur (tout le contenu s'y place)
        self._frame_interieur = tk.Frame(self._canvas_scroll, bg=c["bg"])
        self._window_id = self._canvas_scroll.create_window(
            (0, 0), window=self._frame_interieur, anchor="nw"
        )

        # Mise à jour de la scrollregion quand le contenu change de taille
        self._frame_interieur.bind("<Configure>", self._on_frame_configure)
        self._canvas_scroll.bind("<Configure>",   self._on_canvas_configure)

        # Molette souris
        self.root.bind_all("<MouseWheel>",
            lambda e: self._canvas_scroll.yview_scroll(-1*(e.delta//120), "units"))

        # ─ Contenu ──────────────────────────────────────────────────
        fi = self._frame_interieur
        PX = 20

        # Titre
        tk.Label(fi, text="🔐  Anchor Vault",
                 font=("Segoe UI", 20, "bold"),
                 fg=c["primary"], bg=c["bg"]).pack(pady=(22, 3))
        tk.Label(fi, text="Générateur de mots de passe sécurisé",
                 font=("Segoe UI", 10),
                 fg=c["text_muted"], bg=c["bg"]).pack(pady=(0, 14))

        # ── SECTION 1 : Options (▼ ouverte par défaut) ───────────────
        sec1 = SectionExpandable(
            fi, titre="⚙️  Options", ouvert=True,
            couleur_surface="surface", on_toggle=self._refresh_scroll
        )
        sec1.pack(fill="x", padx=PX, pady=(0, 10))
        self._construire_section_options(sec1.corps)

        # ── SECTION 2 : Résultat (▼ ouverte par défaut) ─────────────
        sec2 = SectionExpandable(
            fi, titre="🔑  Résultat", ouvert=True,
            couleur_surface="surface", on_toggle=self._refresh_scroll
        )
        sec2.pack(fill="x", padx=PX, pady=(0, 10))
        self._construire_section_resultat(sec2.corps)

        # ── SECTION 3 : Analyse (▶ fermée par défaut) ─────────────
        sec3 = SectionExpandable(
            fi, titre="🛡️  Analyse de sécurité",
            badge_texte="CYBER", badge_couleur=c["primary"], badge_bg="#2e2a52",
            ouvert=False, couleur_surface="surface2", on_toggle=self._refresh_scroll
        )
        sec3.pack(fill="x", padx=PX, pady=(0, 10))
        self._construire_section_analyse(sec3.corps)

        # ── SECTION 4 : HIBP (▶ fermée par défaut) ───────────────
        sec4 = SectionExpandable(
            fi, titre="🔍  Vérification des leaks",
            badge_texte="HIBP", badge_couleur="#4ade80", badge_bg="#1a2e1a",
            ouvert=False, couleur_surface="surface2", on_toggle=self._refresh_scroll
        )
        sec4.pack(fill="x", padx=PX, pady=(0, 10))
        self._construire_section_hibp(sec4.corps)

        # Espace bas
        tk.Frame(fi, bg=c["bg"], height=20).pack()

    def _on_frame_configure(self, _event=None):
        self._canvas_scroll.configure(
            scrollregion=self._canvas_scroll.bbox("all")
        )

    def _on_canvas_configure(self, event):
        # Le frame intérieur prend toute la largeur du canvas
        self._canvas_scroll.itemconfig(self._window_id, width=event.width)

    def _refresh_scroll(self):
        """Appelé après chaque toggle pour recalculer la scrollregion."""
        self._frame_interieur.update_idletasks()
        self._canvas_scroll.configure(
            scrollregion=self._canvas_scroll.bbox("all")
        )

    # ── Constructeurs de sections ─────────────────────────────────────

    def _construire_section_options(self, parent):
        c = self.C
        bg = c["surface"]

        self.var_longueur = tk.IntVar(value=16)
        row_len = tk.Frame(parent, bg=bg)
        row_len.pack(fill="x", pady=(0, 4))
        tk.Label(row_len, text="Longueur", font=("Segoe UI", 10, "bold"),
                 fg=c["text"], bg=bg).pack(side="left")
        tk.Label(row_len, textvariable=self.var_longueur,
                 font=("Segoe UI", 10, "bold"),
                 fg=c["primary"], bg=bg).pack(side="right")

        tk.Scale(
            parent, from_=4, to=64, orient="horizontal",
            variable=self.var_longueur,
            bg=bg, fg=c["text_muted"],
            troughcolor=c["border"], activebackground=c["primary"],
            highlightthickness=0, bd=0, showvalue=False,
            command=lambda _: self._mettre_a_jour_force()
        ).pack(fill="x", pady=(0, 12))

        tk.Frame(parent, bg=c["border"], height=1).pack(fill="x", pady=(0, 12))

        tk.Label(parent, text="Types de caractères",
                 font=("Segoe UI", 10, "bold"),
                 fg=c["text"], bg=bg).pack(anchor="w", pady=(0, 8))

        self.var_maj = tk.BooleanVar(value=True)
        self.var_min = tk.BooleanVar(value=True)
        self.var_chf = tk.BooleanVar(value=True)
        self.var_sym = tk.BooleanVar(value=True)

        grille = tk.Frame(parent, bg=bg)
        grille.pack(fill="x")
        opts = [("Majuscules  (A–Z)", self.var_maj), ("Minuscules  (a–z)", self.var_min),
                ("Chiffres      (0–9)", self.var_chf), ("Symboles  (!@#$…)", self.var_sym)]
        for i, (lbl, var) in enumerate(opts):
            tk.Checkbutton(
                grille, text=lbl, variable=var,
                font=("Segoe UI", 9), fg=c["text"], bg=bg,
                selectcolor=c["primary"],
                activebackground=bg, activeforeground=c["text"],
                cursor="hand2", command=self._mettre_a_jour_force
            ).grid(row=i//2, column=i%2, sticky="w", padx=(0,16), pady=2)

        tk.Frame(parent, bg=c["border"], height=1).pack(fill="x", pady=(14, 10))

        row_force = tk.Frame(parent, bg=bg)
        row_force.pack(fill="x", pady=(0, 6))
        tk.Label(row_force, text="Force du mot de passe",
                 font=("Segoe UI", 9, "bold"),
                 fg=c["text_muted"], bg=bg).pack(side="left")
        self.lbl_force = tk.Label(row_force, text="",
                                   font=("Segoe UI", 9, "bold"),
                                   fg=c["success"], bg=bg)
        self.lbl_force.pack(side="right")

        self.canvas_barre = tk.Canvas(parent, height=8, bg=c["bar_bg"],
                                       highlightthickness=0, bd=0)
        self.canvas_barre.pack(fill="x", pady=(0, 4))
        self.rect_barre = self.canvas_barre.create_rectangle(
            0, 0, 0, 8, fill=c["success"], outline="")

        self.lbl_erreur = tk.Label(parent, text="", font=("Segoe UI", 9),
                                    fg=c["error"], bg=bg, height=1)
        self.lbl_erreur.pack(pady=(4, 0))

        tk.Button(
            parent, text="⚡  Générer",
            font=("Segoe UI", 11, "bold"),
            fg="white", bg=c["primary"],
            activeforeground="white", activebackground=c["primary_hover"],
            relief="flat", cursor="hand2", pady=10, bd=0,
            command=self._on_generer
        ).pack(fill="x", pady=(8, 0))

    def _construire_section_resultat(self, parent):
        c = self.C
        bg = c["surface"]

        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x")

        col_g = tk.Frame(row, bg=bg)
        col_g.pack(side="left", fill="both", expand=True, padx=(0, 12))

        tk.Label(col_g, text="Mot de passe généré",
                 font=("Segoe UI", 9), fg=c["text_muted"], bg=bg
                 ).pack(anchor="w", pady=(0, 6))

        champ_frame = tk.Frame(col_g, bg=c["input_bg"],
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
            col_g, text="📋  Copier",
            font=("Segoe UI", 10), fg=c["text"], bg=c["border"],
            activeforeground="white", activebackground=c["primary"],
            relief="flat", cursor="hand2", pady=8, bd=0,
            command=self._on_copier
        )
        self.btn_copier.pack(fill="x", pady=(8, 0))

        col_d = tk.Frame(row, bg=bg)
        col_d.pack(side="right", anchor="n")
        tk.Label(col_d, text="ADN visuel", font=("Segoe UI", 7),
                 fg=c["text_muted"], bg=bg).pack(pady=(0, 4))
        self.canvas_identicon = tk.Canvas(
            col_d, width=IDENTICON_SIZE, height=IDENTICON_SIZE,
            bg="#1e1e30", highlightbackground=c["border"],
            highlightthickness=1, bd=0
        )
        self.canvas_identicon.pack()
        generer_identicon("", self.canvas_identicon)
        tk.Label(col_d, text="unique par mdp", font=("Segoe UI", 7),
                 fg=c["text_muted"], bg=bg).pack(pady=(4, 0))

    def _construire_section_analyse(self, parent):
        c  = self.C
        bg = c["surface2"]

        row_e = tk.Frame(parent, bg=bg)
        row_e.pack(fill="x", pady=(0, 8))
        tk.Label(row_e, text="Entropie", font=("Segoe UI", 9),
                 fg=c["text_muted"], bg=bg).pack(side="left")
        self.lbl_entropie = tk.Label(row_e, text="— bits",
                                      font=("Consolas", 9, "bold"),
                                      fg=c["primary"], bg=bg)
        self.lbl_entropie.pack(side="right")

        tk.Frame(parent, bg=c["border"], height=1).pack(fill="x", pady=(0, 10))

        row_c = tk.Frame(parent, bg=bg)
        row_c.pack(fill="x", pady=(0, 4))
        tk.Label(row_c, text="⏱️  Temps de crack", font=("Segoe UI", 9),
                 fg=c["text_muted"], bg=bg).pack(side="left")
        self.lbl_temps = tk.Label(row_c, text="—",
                                   font=("Segoe UI", 9, "bold"),
                                   fg=c["success"], bg=bg)
        self.lbl_temps.pack(side="right")

        self.lbl_analogie = tk.Label(
            parent, text="", font=("Segoe UI", 9, "italic"),
            fg=c["text_muted"], bg=bg, wraplength=390, justify="center"
        )
        self.lbl_analogie.pack(pady=(4, 0))

        tk.Frame(parent, bg=c["border"], height=1).pack(fill="x", pady=(10, 6))
        tk.Label(parent,
                 text="⚡ Simulé sur RTX 4090 — brute force (10¹⁰ essais/sec)",
                 font=("Segoe UI", 7), fg=c["text_muted"], bg=bg).pack()

    def _construire_section_hibp(self, parent):
        c  = self.C
        bg = c["surface2"]

        self.lbl_hibp_statut = tk.Label(
            parent, text="🔒  Génère un mot de passe pour vérifier",
            font=("Segoe UI", 10), fg=c["text_muted"], bg=bg,
            wraplength=390, justify="center"
        )
        self.lbl_hibp_statut.pack(pady=(0, 6))

        self.lbl_hibp_detail = tk.Label(
            parent, text="", font=("Segoe UI", 8, "italic"),
            fg=c["text_muted"], bg=bg, wraplength=390, justify="center"
        )
        self.lbl_hibp_detail.pack()

        tk.Frame(parent, bg=c["border"], height=1).pack(fill="x", pady=(10, 8))
        tk.Label(
            parent,
            text="🛡️ K-anonymity : seuls 5 chars du hash SHA-1 sont envoyés — le vrai mdp ne quitte jamais l'app",
            font=("Segoe UI", 7), fg=c["text_muted"], bg=bg,
            wraplength=390, justify="center"
        ).pack()

    # ── Logique ────────────────────────────────────────────────────────

    def _mettre_a_jour_force(self):
        lon = self.var_longueur.get()
        maj, min_, chf, sym = (
            self.var_maj.get(), self.var_min.get(),
            self.var_chf.get(), self.var_sym.get()
        )
        label, couleur, ratio = evaluer_force(lon, maj, min_, chf, sym)
        self.lbl_force.config(text=label, fg=couleur)
        self.canvas_barre.update_idletasks()
        lw = self.canvas_barre.winfo_width()
        self.canvas_barre.coords(self.rect_barre, 0, 0, int(lw * ratio), 8)
        self.canvas_barre.itemconfig(self.rect_barre, fill=couleur)

        entropie = calculer_entropie(lon, maj, min_, chf, sym)
        secondes = calculer_temps_crack(entropie)
        duree, analogie, coul = formater_temps(secondes)

        if entropie > 0:
            self.lbl_entropie.config(text=f"{entropie:.1f} bits")
            self.lbl_temps.config(text=duree, fg=coul)
            self.lbl_analogie.config(text=analogie, fg=coul)
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
        generer_identicon(mdp, self.canvas_identicon)
        self._lancer_hibp(mdp)

    def _reset_hibp(self):
        self.lbl_hibp_statut.config(
            text="🔒  Génère un mot de passe pour vérifier",
            fg=self.C["text_muted"]
        )
        self.lbl_hibp_detail.config(text="")
        self._dernier_mdp_hibp = ""

    def _lancer_hibp(self, mdp):
        if mdp == self._dernier_mdp_hibp:
            return
        self._dernier_mdp_hibp = mdp
        if not REQUESTS_AVAILABLE:
            self.lbl_hibp_statut.config(
                text="📦  Module 'requests' non installé",
                fg=self.C["warning"]
            )
            self.lbl_hibp_detail.config(
                text="Lance : pip install requests",
                fg=self.C["text_muted"]
            )
            return
        self.lbl_hibp_statut.config(text="⏳  Vérification en cours…",
                                     fg=self.C["text_muted"])
        self.lbl_hibp_detail.config(text="")
        def _cb(res):
            self.root.after(0, lambda: self._afficher_resultat_hibp(res, mdp))
        verifier_hibp(mdp, _cb)

    def _afficher_resultat_hibp(self, resultat, mdp_verifie):
        if mdp_verifie != self._dernier_mdp_hibp:
            return
        if resultat == -2:
            self.lbl_hibp_statut.config(text="📦  Module 'requests' requis",
                                         fg=self.C["warning"])
            self.lbl_hibp_detail.config(text="pip install requests",
                                         fg=self.C["text_muted"])
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
        self.btn_copier.config(text="✅  Copié !", fg="white", bg="#3aad6a")
        self.root.after(2000, lambda: self.btn_copier.config(
            text="📋  Copier", fg=self.C["text"], bg=self.C["border"]))


if __name__ == "__main__":
    root = tk.Tk()
    AnchorVaultApp(root)
    root.mainloop()
