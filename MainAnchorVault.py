"""
🔐 Anchor Vault — Générateur de mots de passe sécurisé
Stack  : Python 3.10+ | Tkinter | secrets | math | hashlib | threading | requests
Version: 4.3 — Redesign UI Anchor Protocol (black / white / green)
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


# ════════════════════════════════════════════════════════════════════════
#  PALETTE — Anchor Protocol
# ════════════════════════════════════════════════════════════════════════

C = {
    # Fonds
    "bg":            "#0f0f0f",   # fond global noir
    "header_bg":     "#111111",   # header bande noire
    "card":          "#f5f5f5",   # surface card blanche
    "card2":         "#ececec",   # surface card légèrement plus sombre
    "input_bg":      "#e8e8e8",   # fond champ de saisie
    "border_card":   "#dedede",   # bordure subtile sur card
    "border_dark":   "#2a2a2a",   # bordure sur fond noir

    # Textes
    "text_dark":     "#1a1a1a",   # texte principal sur card
    "text_muted":    "#777777",   # texte secondaire
    "text_faint":    "#aaaaaa",   # labels très discrets
    "text_light":    "#e8e8e8",   # texte sur fond noir
    "text_muted_dk": "#666666",   # muted sur fond noir

    # Accent vert Anchor
    "green":         "#4bdc6f",   # vert vif principal
    "green_dark":    "#2d9a4e",   # vert sombre (logo, hover)
    "green_bg":      "#0f2a18",   # fond très sombre teinté vert
    "green_text":    "#1a1a1a",   # texte sur bouton vert

    # États
    "success":       "#4bdc6f",
    "warning":       "#f5a623",
    "error":         "#e84040",
    "error_weak":    "#ff6b6b",

    # Boutons sombres (style Deposit/Withdraw)
    "btn_dark":      "#2a2a2a",
    "btn_dark_hov":  "#3a3a3a",
}


# ════════════════════════════════════════════════════════════════════════
#  LOGIQUE — Génération
# ════════════════════════════════════════════════════════════════════════

def generer_mot_de_passe(longueur, majuscules, minuscules, chiffres, symboles):
    pool, garantis = "", []
    if majuscules: pool += string.ascii_uppercase; garantis.append(secrets.choice(string.ascii_uppercase))
    if minuscules: pool += string.ascii_lowercase; garantis.append(secrets.choice(string.ascii_lowercase))
    if chiffres:   pool += string.digits;          garantis.append(secrets.choice(string.digits))
    if symboles:   pool += string.punctuation;     garantis.append(secrets.choice(string.punctuation))
    if not pool:   return None
    reste = longueur - len(garantis)
    mdp   = garantis + [secrets.choice(pool) for _ in range(reste)]
    secrets.SystemRandom().shuffle(mdp)
    return "".join(mdp)


def evaluer_force_mdp(mdp):
    if not mdp: return "", C["text_muted"], 0.0
    lon  = len(mdp)
    types = sum([
        any(c.isupper()  for c in mdp),
        any(c.islower()  for c in mdp),
        any(c.isdigit()  for c in mdp),
        any(not c.isalnum() for c in mdp),
    ])
    if lon < 8  or types == 1: return "TRÈS FAIBLE", C["error"],   0.15
    if lon < 12 or types == 2: return "FAIBLE",      C["warning"],  0.40
    if lon < 16 or types == 3: return "FORT",        C["green"],    0.70
    return                            "TRÈS FORT",   C["green"],    1.00


def evaluer_force(lon, maj, min_, chf, sym):
    t = sum([maj, min_, chf, sym])
    if lon < 8  or t == 1: return "TRÈS FAIBLE", C["error"],   0.15
    if lon < 12 or t == 2: return "FAIBLE",      C["warning"],  0.40
    if lon < 16 or t == 3: return "FORT",        C["green"],    0.70
    return                        "TRÈS FORT",   C["green"],    1.00


# ════════════════════════════════════════════════════════════════════════
#  LOGIQUE — Entropie + crack time
# ════════════════════════════════════════════════════════════════════════

GPU = 10_000_000_000

def _entropie(lon, maj, min_, chf, sym):
    a = sum([26*maj, 26*min_, 10*chf, 32*sym])
    return lon * math.log2(a) if a else 0.0

def _entropie_mdp(mdp):
    if not mdp: return 0.0
    a = sum([26*any(c.isupper() for c in mdp), 26*any(c.islower() for c in mdp),
             10*any(c.isdigit() for c in mdp), 32*any(not c.isalnum() for c in mdp)])
    return len(mdp) * math.log2(a) if a else 0.0

def _crack(e):
    if e <= 0:   return 0
    if e > 300:  return float("inf")
    return (2**e / 2) / GPU

def _formater(s):
    if s == float("inf"): return "∞", "Plus vieux que l'Univers × 1000", C["green"]
    M,H,J,MO,AN = 60,3600,86400,2592000,31536000
    if s < 1:    return "< 1s",          "Craqué instantanément",                   C["error"]
    if s < M:    return f"{int(s)}s",    "Craqué avant ta prochaine inspiration",   C["error"]
    if s < H:    return f"{int(s//M)}m", "Craqué avant que ton café refroidisse",  C["warning"]
    if s < J:    return f"{int(s//H)}h", "Moins d'une journée de binge-watching",  C["warning"]
    if s < MO:   return f"{int(s//J)}j", "Craqué dans le mois",                    C["warning"]
    if s < AN:   m=int(s//MO); return f"{m} mois",    "Craqué dans l'année",       C["green"]
    if s < AN*100: a=int(s//AN); return f"{a} ans",   "Craqué de ton vivant",      C["green"]
    sc=int(s//(AN*100)); return f"{sc} siècles", "Plus long que l'Empire Romain", C["green"]


# ════════════════════════════════════════════════════════════════════════
#  LOGIQUE — Identicon
# ════════════════════════════════════════════════════════════════════════

IG, IC, IP = 5, 18, 5
IS = IG * IC + IP * 2

def generer_identicon(mdp, canvas, bg_card="#f5f5f5"):
    canvas.delete("all")
    if not mdp:
        canvas.configure(bg=bg_card)
        canvas.create_text(IS//2, IS//2, text="A",
                           fill="#cccccc", font=("Arial", 22, "bold"))
        return
    h = hashlib.sha256(mdp.encode()).digest()
    r, g, b = h[0], h[1], h[2]
    if max(r,g,b)-min(r,g,b) < 50:
        d = [r,g,b].index(max(r,g,b)); p=[r,g,b]
        p[d]=min(255,p[d]+90); p[(d+1)%3]=max(0,p[(d+1)%3]-40)
        r,g,b = p
    col  = f"#{r:02x}{g:02x}{b:02x}"
    rc,gc,bc = (r+128)%256,(g+128)%256,(b+128)%256
    bg_hex = f"#{rc:02x}{gc:02x}{bc:02x}"
    # On garde le fond de la card pour la bordure
    canvas.configure(bg=bg_card)
    # Dessiner fond coloré légèrement transparent via rectangle
    canvas.create_rectangle(0, 0, IS, IS, fill=bg_hex, outline="")
    grille = [[False]*IG for _ in range(IG)]
    bi = 0
    for row in range(IG):
        for col2 in range(3):
            grille[row][col2] = bool((h[3+bi//8] >> (bi%8)) & 1); bi += 1
    for row in range(IG):
        grille[row][3] = grille[row][1]
        grille[row][4] = grille[row][0]
    for row in range(IG):
        for col2 in range(IG):
            x1 = IP + col2*IC; y1 = IP + row*IC
            fill = col if grille[row][col2] else bg_hex
            canvas.create_rectangle(x1, y1, x1+IC-1, y1+IC-1, fill=fill, outline="")


# ════════════════════════════════════════════════════════════════════════
#  LOGIQUE — HIBP
# ════════════════════════════════════════════════════════════════════════

def verifier_hibp(mdp, callback):
    if not REQUESTS_AVAILABLE: callback(-2); return
    def _w():
        try:
            sha1 = hashlib.sha1(mdp.encode()).hexdigest().upper()
            pre, suf = sha1[:5], sha1[5:]
            r = requests.get(f"https://api.pwnedpasswords.com/range/{pre}",
                             timeout=3, headers={"Add-Padding": "true"})
            r.raise_for_status()
            for l in r.text.splitlines():
                hp, cnt = l.split(":")
                if hp.strip() == suf: callback(int(cnt.strip())); return
            callback(0)
        except Exception: callback(-1)
    threading.Thread(target=_w, daemon=True).start()


# ════════════════════════════════════════════════════════════════════════
#  WIDGETS CUSTOM — Logo A + Bouton Pill
# ════════════════════════════════════════════════════════════════════════

def dessiner_logo_a(canvas, cx, cy, taille=32):
    """Logo 'A' Anchor Protocol : 2 capsules vertes croisées."""
    canvas.delete("all")
    t = taille
    ep  = int(t * 0.28)   # épaisseur capsule
    r   = ep // 2         # rayon arrondi
    # Capsule gauche (vert vif)
    pts_g = [
        (cx - int(t*0.38), cy + int(t*0.42)),
        (cx + int(t*0.02), cy - int(t*0.42)),
    ]
    _capsule(canvas, pts_g[0], pts_g[1], ep, C["green"])
    # Capsule droite (vert sombre, léger overlay)
    pts_d = [
        (cx - int(t*0.02), cy - int(t*0.42)),
        (cx + int(t*0.38), cy + int(t*0.42)),
    ]
    _capsule(canvas, pts_d[0], pts_d[1], ep, C["green_dark"])

def _capsule(canvas, p1, p2, ep, couleur):
    """Trace une capsule (rectangle + demi-cercles aux extrémités) entre p1 et p2."""
    import math as _m
    dx, dy = p2[0]-p1[0], p2[1]-p1[1]
    lng = _m.hypot(dx, dy)
    if lng == 0: return
    nx, ny = -dy/lng, dx/lng  # normale
    r = ep // 2
    # 4 coins du rectangle
    corners = [
        (p1[0]+nx*r, p1[1]+ny*r),
        (p2[0]+nx*r, p2[1]+ny*r),
        (p2[0]-nx*r, p2[1]-ny*r),
        (p1[0]-nx*r, p1[1]-ny*r),
    ]
    flat = [v for pt in corners for v in pt]
    canvas.create_polygon(flat, fill=couleur, outline="")
    canvas.create_oval(p1[0]-r, p1[1]-r, p1[0]+r, p1[1]+r, fill=couleur, outline="")
    canvas.create_oval(p2[0]-r, p2[1]-r, p2[0]+r, p2[1]+r, fill=couleur, outline="")


class BoutonPill(tk.Canvas):
    """Bouton arrondi style Anchor Protocol."""
    def __init__(self, parent, texte, commande=None,
                 bg_btn=None, fg_btn=None,
                 bg_parent=None,
                 largeur=200, hauteur=40, **kwargs):
        self._bg_btn  = bg_btn  or C["green"]
        self._fg_btn  = fg_btn  or C["green_text"]
        self._bg_par  = bg_parent or C["card"]
        self._texte   = texte
        self._cmd     = commande
        self._w       = largeur
        self._h       = hauteur
        super().__init__(parent, width=largeur, height=hauteur,
                         bg=self._bg_par, highlightthickness=0, bd=0, **kwargs)
        self._dessiner(self._bg_btn)
        self.bind("<Button-1>",  self._click)
        self.bind("<Enter>",     lambda _: self._dessiner(self._hover()))
        self.bind("<Leave>",     lambda _: self._dessiner(self._bg_btn))
        self.config(cursor="hand2")

    def _hover(self):
        # Assombrit légèrement la couleur
        col = self._bg_btn.lstrip("#")
        r,g,b = int(col[0:2],16),int(col[2:4],16),int(col[4:6],16)
        r,g,b = max(0,r-20),max(0,g-20),max(0,b-20)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _dessiner(self, couleur):
        self.delete("all")
        r = self._h // 2
        self.create_arc(0, 0, 2*r, self._h,
                        start=90, extent=180, fill=couleur, outline="")
        self.create_arc(self._w-2*r, 0, self._w, self._h,
                        start=270, extent=180, fill=couleur, outline="")
        self.create_rectangle(r, 0, self._w-r, self._h,
                              fill=couleur, outline="")
        self.create_text(self._w//2, self._h//2, text=self._texte,
                         fill=self._fg_btn,
                         font=("Segoe UI", 10, "bold"))

    def _click(self, _=None):
        if self._cmd: self._cmd()


# ════════════════════════════════════════════════════════════════════════
#  COMPOSANT — Section Accordion
# ════════════════════════════════════════════════════════════════════════

class SectionCard(tk.Frame):
    """Card blanche avec header cliquable (accordion)."""

    def __init__(self, parent, titre, badge=None,
                 ouvert=True, on_toggle=None, **kwargs):
        super().__init__(parent, bg=C["card"],
                         highlightbackground=C["border_card"],
                         highlightthickness=1, **kwargs)
        self._ouvert    = ouvert
        self._on_toggle = on_toggle

        # Header
        hdr = tk.Frame(self, bg=C["card"], cursor="hand2")
        hdr.pack(fill="x", padx=16, pady=(12, 12))

        self._chevron = tk.Label(hdr,
            text="▾" if ouvert else "▸",
            font=("Segoe UI", 9), fg=C["text_muted"], bg=C["card"])
        self._chevron.pack(side="left", padx=(0, 8))

        tk.Label(hdr, text=titre,
                 font=("Segoe UI", 9, "bold"),
                 fg=C["text_dark"], bg=C["card"]
                 ).pack(side="left")

        if badge:
            btxt, bcol = badge
            tk.Label(hdr, text=f" {btxt} ",
                     font=("Segoe UI", 7, "bold"),
                     fg="white", bg=bcol,
                     padx=5, pady=2
                     ).pack(side="right")

        # Séparateur
        self._sep = tk.Frame(self, bg=C["border_card"], height=1)

        # Corps
        self.corps = tk.Frame(self, bg=C["card"])
        if ouvert:
            self._sep.pack(fill="x")
            self.corps.pack(fill="x", padx=18, pady=(12, 16))

        for w in (hdr, self._chevron):
            w.bind("<Button-1>", self._toggle)
            w.bind("<Enter>",    lambda e: hdr.config(bg="#ebebeb"))
            w.bind("<Leave>",    lambda e: hdr.config(bg=C["card"]))

    def _toggle(self, _=None):
        self._ouvert = not self._ouvert
        if self._ouvert:
            self._sep.pack(fill="x")
            self.corps.pack(fill="x", padx=18, pady=(12, 16))
            self._chevron.config(text="▾")
        else:
            self._sep.pack_forget()
            self.corps.pack_forget()
            self._chevron.config(text="▸")
        if self._on_toggle: self._on_toggle()


# ════════════════════════════════════════════════════════════════════════
#  APPLICATION PRINCIPALE
# ════════════════════════════════════════════════════════════════════════

class AnchorVaultApp:

    LARGEUR      = 480
    HAUTEUR      = 640
    DEBOUNCE_MS  = 600

    def __init__(self, root):
        self.root              = root
        self._dernier_hibp     = ""
        self._debounce_id      = None
        self._placeholder_actif = True
        self._configurer_fenetre()
        self._build_ui()
        self._mettre_a_jour_force()

    def _configurer_fenetre(self):
        self.root.title("Anchor Vault")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{self.LARGEUR}x{self.HAUTEUR}+{(sw-self.LARGEUR)//2}+{(sh-self.HAUTEUR)//2}")
        self.root.resizable(False, False)
        self.root.configure(bg=C["bg"])

    # ── Build UI ──────────────────────────────────────────────────────

    def _build_ui(self):
        # ── HEADER noir ──
        header = tk.Frame(self.root, bg=C["header_bg"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        logo_canvas = tk.Canvas(header, width=36, height=36,
                                bg=C["header_bg"], highlightthickness=0)
        logo_canvas.pack(side="left", padx=(18, 8), pady=12)
        dessiner_logo_a(logo_canvas, 18, 18, taille=30)

        tk.Label(header, text="ANCHOR VAULT",
                 font=("Segoe UI", 13, "bold"),
                 fg=C["text_light"], bg=C["header_bg"]
                 ).pack(side="left", pady=12)

        tk.Label(header, text="v4",
                 font=("Segoe UI", 8),
                 fg=C["green"], bg=C["header_bg"]
                 ).pack(side="left", padx=(6, 0), pady=16)

        # ── Zone scrollable ──
        outer = tk.Frame(self.root, bg=C["bg"])
        outer.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Vault.Vertical.TScrollbar",
                        background=C["border_dark"],
                        troughcolor=C["bg"],
                        arrowcolor=C["text_muted_dk"],
                        borderwidth=0, relief="flat")

        self._cvs = tk.Canvas(outer, bg=C["bg"], highlightthickness=0, bd=0)
        sb  = ttk.Scrollbar(outer, orient="vertical",
                            command=self._cvs.yview,
                            style="Vault.Vertical.TScrollbar")
        self._cvs.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._cvs.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._cvs, bg=C["bg"])
        self._win   = self._cvs.create_window((0,0), window=self._inner, anchor="nw")
        self._inner.bind("<Configure>", lambda _: self._cvs.configure(
            scrollregion=self._cvs.bbox("all")))
        self._cvs.bind("<Configure>",
            lambda e: self._cvs.itemconfig(self._win, width=e.width))
        self.root.bind_all("<MouseWheel>",
            lambda e: self._cvs.yview_scroll(-1*(e.delta//120), "units"))

        PX = 16

        # ── Sections ──
        s1 = SectionCard(self._inner, titre="⚙  OPTIONS",
                         ouvert=True, on_toggle=self._refresh_scroll)
        s1.pack(fill="x", padx=PX, pady=(16, 8))
        self._build_options(s1.corps)

        s2 = SectionCard(self._inner, titre="🔑  RÉSULTAT",
                         ouvert=True, on_toggle=self._refresh_scroll)
        s2.pack(fill="x", padx=PX, pady=(0, 8))
        self._build_resultat(s2.corps)

        s3 = SectionCard(self._inner, titre="🛡  ANALYSE DE SÉCURITÉ",
                         badge=("CYBER", C["green_dark"]),
                         ouvert=False, on_toggle=self._refresh_scroll)
        s3.pack(fill="x", padx=PX, pady=(0, 8))
        self._build_analyse(s3.corps)

        s4 = SectionCard(self._inner, titre="🔍  VÉRIFICATION DES LEAKS",
                         badge=("HIBP", "#2a7a4a"),
                         ouvert=False, on_toggle=self._refresh_scroll)
        s4.pack(fill="x", padx=PX, pady=(0, 8))
        self._build_hibp(s4.corps)

        tk.Frame(self._inner, bg=C["bg"], height=20).pack()

    def _refresh_scroll(self):
        self._inner.update_idletasks()
        self._cvs.configure(scrollregion=self._cvs.bbox("all"))

    # ── Section Options ───────────────────────────────────────────────

    def _build_options(self, p):
        bg = C["card"]

        # Longueur
        row = tk.Frame(p, bg=bg); row.pack(fill="x", pady=(0,4))
        tk.Label(row, text="LONGUEUR",
                 font=("Segoe UI", 8, "bold"),
                 fg=C["text_muted"], bg=bg).pack(side="left")
        self.var_lon = tk.IntVar(value=16)
        self.lbl_lon = tk.Label(row, textvariable=self.var_lon,
                                font=("Segoe UI", 11, "bold"),
                                fg=C["green_dark"], bg=bg)
        self.lbl_lon.pack(side="right")

        tk.Scale(p, from_=4, to=64, orient="horizontal",
                 variable=self.var_lon,
                 bg=bg, fg=C["text_muted"],
                 troughcolor=C["border_card"],
                 activebackground=C["green"],
                 highlightthickness=0, bd=0, showvalue=False,
                 command=lambda _: self._mettre_a_jour_force()
                 ).pack(fill="x", pady=(0, 14))

        tk.Frame(p, bg=C["border_card"], height=1).pack(fill="x", pady=(0,12))
        tk.Label(p, text="TYPES DE CARACTÈRES",
                 font=("Segoe UI", 8, "bold"),
                 fg=C["text_muted"], bg=bg
                 ).pack(anchor="w", pady=(0,8))

        self.var_maj = tk.BooleanVar(value=True)
        self.var_min = tk.BooleanVar(value=True)
        self.var_chf = tk.BooleanVar(value=True)
        self.var_sym = tk.BooleanVar(value=True)

        g = tk.Frame(p, bg=bg); g.pack(fill="x")
        opts = [("Majuscules  (A–Z)", self.var_maj),
                ("Minuscules  (a–z)", self.var_min),
                ("Chiffres    (0–9)", self.var_chf),
                ("Symboles (!@#…)",  self.var_sym)]
        for i,(lbl,var) in enumerate(opts):
            tk.Checkbutton(g, text=lbl, variable=var,
                           font=("Segoe UI", 9),
                           fg=C["text_dark"], bg=bg,
                           selectcolor=C["green_dark"],
                           activebackground=bg,
                           activeforeground=C["text_dark"],
                           cursor="hand2",
                           command=self._mettre_a_jour_force
                           ).grid(row=i//2, column=i%2, sticky="w",
                                  padx=(0,16), pady=2)

        tk.Frame(p, bg=C["border_card"], height=1).pack(fill="x", pady=(14,10))

        # Barre de force
        row2 = tk.Frame(p, bg=bg); row2.pack(fill="x", pady=(0,6))
        tk.Label(row2, text="FORCE",
                 font=("Segoe UI", 8, "bold"),
                 fg=C["text_muted"], bg=bg).pack(side="left")
        self.lbl_force = tk.Label(row2, text="",
                                   font=("Segoe UI", 8, "bold"),
                                   fg=C["green"], bg=bg)
        self.lbl_force.pack(side="right")

        bar_frame = tk.Frame(p, bg=C["input_bg"],
                             highlightbackground=C["border_card"],
                             highlightthickness=1)
        bar_frame.pack(fill="x", pady=(0,4))
        self.cvs_bar = tk.Canvas(bar_frame, height=8, bg=C["input_bg"],
                                  highlightthickness=0, bd=0)
        self.cvs_bar.pack(fill="x")
        self.rect_bar = self.cvs_bar.create_rectangle(
            0, 0, 0, 8, fill=C["green"], outline="")

        self.lbl_err = tk.Label(p, text="", font=("Segoe UI", 9),
                                 fg=C["error"], bg=bg, height=1)
        self.lbl_err.pack(pady=(4,0))

        BoutonPill(p, texte="⚡  GÉNÉRER",
                   commande=self._on_generer,
                   bg_btn=C["green"], fg_btn=C["green_text"],
                   bg_parent=bg,
                   largeur=410, hauteur=42
                   ).pack(pady=(10,0))

    # ── Section Résultat ──────────────────────────────────────────────

    def _build_resultat(self, p):
        bg = C["card"]
        row = tk.Frame(p, bg=bg); row.pack(fill="x")

        # Colonne gauche
        col_g = tk.Frame(row, bg=bg)
        col_g.pack(side="left", fill="both", expand=True, padx=(0,12))

        row_lbl = tk.Frame(col_g, bg=bg); row_lbl.pack(fill="x", pady=(0,6))
        tk.Label(row_lbl, text="MOT DE PASSE",
                 font=("Segoe UI", 8, "bold"),
                 fg=C["text_muted"], bg=bg).pack(side="left")
        tk.Label(row_lbl, text="✏ éditable",
                 font=("Segoe UI", 7, "italic"),
                 fg=C["green_dark"], bg=bg).pack(side="right")

        entry_frame = tk.Frame(col_g, bg=C["input_bg"],
                               highlightbackground=C["border_card"],
                               highlightthickness=1)
        entry_frame.pack(fill="x")

        self.var_mdp = tk.StringVar()
        self.entry = tk.Entry(entry_frame,
                              textvariable=self.var_mdp,
                              font=("Consolas", 12),
                              fg=C["green_dark"],
                              bg=C["input_bg"],
                              insertbackground=C["text_dark"],
                              relief="flat", bd=8)
        self.entry.pack(fill="x")

        # Placeholder
        self._ph_txt = "Génère ou saisis ton mot de passe…"
        self._afficher_ph()
        self.entry.bind("<FocusIn>",  self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)
        self.var_mdp.trace_add("write", self._on_mdp_change)

        BoutonPill(col_g, texte="📋  COPIER",
                   commande=self._on_copier,
                   bg_btn=C["btn_dark"], fg_btn="#e8e8e8",
                   bg_parent=bg,
                   largeur=210, hauteur=38
                   ).pack(pady=(8,0), anchor="w")
        self._btn_copier_ref = None  # on garde ref pour feedback

        # Colonne droite — Identicon
        col_d = tk.Frame(row, bg=bg)
        col_d.pack(side="right", anchor="n")
        tk.Label(col_d, text="ADN VISUEL",
                 font=("Segoe UI", 7, "bold"),
                 fg=C["text_muted"], bg=bg).pack(pady=(0,4))
        self.cvs_id = tk.Canvas(col_d, width=IS, height=IS,
                                 bg=C["card"],
                                 highlightbackground=C["border_card"],
                                 highlightthickness=1, bd=0)
        self.cvs_id.pack()
        generer_identicon("", self.cvs_id, bg_card=C["card"])
        tk.Label(col_d, text="unique par mdp",
                 font=("Segoe UI", 7),
                 fg=C["text_faint"], bg=bg).pack(pady=(4,0))

    # ── Section Analyse ───────────────────────────────────────────────

    def _build_analyse(self, p):
        bg = C["card"]

        row_e = tk.Frame(p, bg=bg); row_e.pack(fill="x", pady=(0,8))
        tk.Label(row_e, text="ENTROPIE",
                 font=("Segoe UI", 8, "bold"),
                 fg=C["text_muted"], bg=bg).pack(side="left")
        self.lbl_entropie = tk.Label(row_e, text="— bits",
                                      font=("Consolas", 10, "bold"),
                                      fg=C["green_dark"], bg=bg)
        self.lbl_entropie.pack(side="right")

        tk.Frame(p, bg=C["border_card"], height=1).pack(fill="x", pady=(0,10))

        row_c = tk.Frame(p, bg=bg); row_c.pack(fill="x", pady=(0,4))
        tk.Label(row_c, text="TEMPS DE CRACK",
                 font=("Segoe UI", 8, "bold"),
                 fg=C["text_muted"], bg=bg).pack(side="left")
        self.lbl_temps = tk.Label(row_c, text="—",
                                   font=("Segoe UI", 10, "bold"),
                                   fg=C["green_dark"], bg=bg)
        self.lbl_temps.pack(side="right")

        self.lbl_analogie = tk.Label(p, text="",
                                      font=("Segoe UI", 9, "italic"),
                                      fg=C["text_muted"], bg=bg,
                                      wraplength=380, justify="center")
        self.lbl_analogie.pack(pady=(4,0))

        tk.Frame(p, bg=C["border_card"], height=1).pack(fill="x", pady=(10,6))
        tk.Label(p, text="Simulé sur RTX 4090 — brute force (10¹⁰ essais/sec)",
                 font=("Segoe UI", 7),
                 fg=C["text_faint"], bg=bg).pack()

    # ── Section HIBP ──────────────────────────────────────────────────

    def _build_hibp(self, p):
        bg = C["card"]

        self.lbl_hibp = tk.Label(p,
            text="Génère ou saisis un mot de passe pour vérifier",
            font=("Segoe UI", 10), fg=C["text_muted"], bg=bg,
            wraplength=390, justify="center")
        self.lbl_hibp.pack(pady=(0,6))

        self.lbl_hibp2 = tk.Label(p, text="",
            font=("Segoe UI", 8, "italic"), fg=C["text_faint"], bg=bg,
            wraplength=390, justify="center")
        self.lbl_hibp2.pack()

        tk.Frame(p, bg=C["border_card"], height=1).pack(fill="x", pady=(10,8))
        tk.Label(p,
            text="🛡 K-anonymity : seuls 5 chars du hash SHA-1 sont envoyés — le vrai mot de passe ne quitte jamais l'app",
            font=("Segoe UI", 7), fg=C["text_faint"], bg=bg,
            wraplength=390, justify="center").pack()

    # ── Placeholder ───────────────────────────────────────────────────

    def _afficher_ph(self):
        self.entry.config(fg="#bbbbbb")
        self.var_mdp.set(self._ph_txt)
        self._placeholder_actif = True

    def _focus_in(self, _=None):
        if self._placeholder_actif:
            self.var_mdp.set("")
            self.entry.config(fg=C["green_dark"])
            self._placeholder_actif = False

    def _focus_out(self, _=None):
        if not self.var_mdp.get(): self._afficher_ph()

    def _mdp_reel(self):
        return "" if self._placeholder_actif else self.var_mdp.get()

    # ── Frappe → debounce ─────────────────────────────────────────────

    def _on_mdp_change(self, *_):
        if self._placeholder_actif: return
        mdp = self.var_mdp.get()

        # Force
        lbl, col, ratio = evaluer_force_mdp(mdp)
        self.lbl_force.config(text=lbl, fg=col)
        self.cvs_bar.update_idletasks()
        lw = self.cvs_bar.winfo_width()
        self.cvs_bar.coords(self.rect_bar, 0, 0, int(lw*ratio), 8)
        self.cvs_bar.itemconfig(self.rect_bar, fill=col)

        # Entropie
        e = _entropie_mdp(mdp); s = _crack(e); dur, ana, coul = _formater(s)
        if e > 0:
            self.lbl_entropie.config(text=f"{e:.1f} bits")
            self.lbl_temps.config(text=dur, fg=coul)
            self.lbl_analogie.config(text=ana, fg=coul)
        else:
            self.lbl_entropie.config(text="— bits")
            self.lbl_temps.config(text="—", fg=C["text_muted"])
            self.lbl_analogie.config(text="")

        # Identicon immédiat
        generer_identicon(mdp, self.cvs_id, bg_card=C["card"])

        # Debounce HIBP
        if self._debounce_id: self.root.after_cancel(self._debounce_id)
        if mdp:
            self.lbl_hibp.config(text="⏳  Vérification en cours…", fg=C["text_muted"])
            self.lbl_hibp2.config(text="")
            self._debounce_id = self.root.after(
                self.DEBOUNCE_MS, lambda m=mdp: self._lancer_hibp(m))
        else:
            self._reset_hibp()

    # ── Logique principale ────────────────────────────────────────────

    def _mettre_a_jour_force(self):
        lon = self.var_lon.get()
        maj,min_,chf,sym = (self.var_maj.get(),self.var_min.get(),
                             self.var_chf.get(),self.var_sym.get())
        lbl,col,ratio = evaluer_force(lon,maj,min_,chf,sym)
        self.lbl_force.config(text=lbl, fg=col)
        self.cvs_bar.update_idletasks()
        lw = self.cvs_bar.winfo_width()
        self.cvs_bar.coords(self.rect_bar, 0, 0, int(lw*ratio), 8)
        self.cvs_bar.itemconfig(self.rect_bar, fill=col)
        e = _entropie(lon,maj,min_,chf,sym); s = _crack(e)
        dur,ana,coul = _formater(s)
        if e > 0:
            self.lbl_entropie.config(text=f"{e:.1f} bits")
            self.lbl_temps.config(text=dur, fg=coul)
            self.lbl_analogie.config(text=ana, fg=coul)
        else:
            self.lbl_entropie.config(text="— bits")
            self.lbl_temps.config(text="—", fg=C["text_muted"])
            self.lbl_analogie.config(text="Coche au moins un type de caractère",
                                      fg=C["error"])

    def _on_generer(self):
        mdp = generer_mot_de_passe(
            self.var_lon.get(),
            self.var_maj.get(), self.var_min.get(),
            self.var_chf.get(), self.var_sym.get())
        if mdp is None:
            self.lbl_err.config(text="⚠  Coche au moins un type de caractère !")
            return
        self.lbl_err.config(text="")
        self._placeholder_actif = False
        self.entry.config(fg=C["green_dark"])
        self.var_mdp.set(mdp)

    def _reset_hibp(self):
        self.lbl_hibp.config(
            text="Génère ou saisis un mot de passe pour vérifier",
            fg=C["text_muted"])
        self.lbl_hibp2.config(text="")
        self._dernier_hibp = ""

    def _lancer_hibp(self, mdp):
        if mdp == self._dernier_hibp: return
        self._dernier_hibp = mdp
        if not REQUESTS_AVAILABLE:
            self.lbl_hibp.config(text="📦  Module 'requests' non installé", fg=C["warning"])
            self.lbl_hibp2.config(text="pip install requests", fg=C["text_muted"])
            return
        def _cb(r): self.root.after(0, lambda: self._show_hibp(r, mdp))
        verifier_hibp(mdp, _cb)

    def _show_hibp(self, res, mdp):
        if mdp != self._dernier_hibp: return
        if res == -2:
            self.lbl_hibp.config(text="📦  pip install requests", fg=C["warning"])
        elif res == -1:
            self.lbl_hibp.config(text="🔌  Pas de connexion", fg=C["warning"])
            self.lbl_hibp2.config(text="Le mot de passe n'a pas quitté l'app.",
                                   fg=C["text_faint"])
        elif res == 0:
            self.lbl_hibp.config(text="✅  Propre — non trouvé dans les leaks",
                                  fg=C["green_dark"])
            self.lbl_hibp2.config(
                text="Aucune fuite de données connue pour ce mot de passe.",
                fg=C["text_muted"])
        else:
            cnt = f"{res:,}".replace(","," ")
            self.lbl_hibp.config(text=f"⚠  Trouvé {cnt} fois dans des leaks !",
                                  fg=C["error"])
            self.lbl_hibp2.config(text="Mot de passe compromis — génères-en un nouveau.",
                                   fg=C["error"])

    def _on_copier(self):
        mdp = self._mdp_reel()
        if not mdp: return
        if CLIPBOARD_AVAILABLE:
            pyperclip.copy(mdp)
        else:
            self.root.clipboard_clear()
            self.root.clipboard_append(mdp)
            self.root.update()
        # feedback visuel temporaire sur le label COPIER
        # (le BoutonPill ne stocke pas de ref directe, on utilise un label flottant)
        fb = tk.Label(self._inner, text="✅  Copié !",
                      font=("Segoe UI", 9, "bold"),
                      fg=C["green_dark"], bg=C["bg"])
        fb.place(relx=0.5, rely=0.92, anchor="center")
        self.root.after(1800, fb.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    AnchorVaultApp(root)
    root.mainloop()
