"""
🔐 Anchor Vault — Générateur de mots de passe sécurisé
Stack : Python 3.10+ | Tkinter | secrets | math
Version : 4.0 — ajout temps de crackage + analogies fun
"""

import math
import secrets
import string
import tkinter as tk

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


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

# Vitesse de référence : RTX 4090 en attaque brute force SHA-1
# ~10 milliards de tentatives/seconde (10^10)
VITESSE_GPU = 10_000_000_000  # tentatives/seconde


def calculer_entropie(longueur, majuscules, minuscules, chiffres, symboles):
    """
    Calcule l'entropie en bits du mot de passe généré.
    Entropie = longueur × log2(taille_alphabet)
    """
    alphabet = 0
    if majuscules: alphabet += 26
    if minuscules: alphabet += 26
    if chiffres:   alphabet += 10
    if symboles:   alphabet += 32  # ~32 symboles courants

    if alphabet == 0:
        return 0.0
    return longueur * math.log2(alphabet)


def calculer_temps_crack(entropie_bits):
    """
    Estime le temps de crackage en secondes pour une attaque brute force GPU.
    Temps moyen = (2^entropie / 2) / vitesse_GPU
    On divise par 2 car en moyenne on trouve le mot de passe à mi-chemin.
    """
    if entropie_bits <= 0:
        return 0
    if entropie_bits > 300:
        return float("inf")
    nb_combinaisons = 2 ** entropie_bits
    secondes = (nb_combinaisons / 2) / VITESSE_GPU
    return secondes


def formater_temps(secondes):
    """
    Convertit les secondes en une durée lisible et mémorable.
    Retourne (durée_formatée, analogie_fun, couleur)
    """
    if secondes == float("inf"):
        return (
            "∞ infini",
            "🌌  Plus long que l'âge de l'Univers × 1 000",
            "#4ade80"
        )

    MINUTE   = 60
    HEURE    = 3_600
    JOUR     = 86_400
    MOIS     = 2_592_000
    AN       = 31_536_000
    SIECLE   = AN * 100
    MILLEN   = AN * 1_000
    MILLION  = AN * 1_000_000
    MILLIARD = AN * 1_000_000_000

    if secondes < 1:
        return (
            "< 1 seconde",
            "💀  Craqué instantanément — n'utilise JAMAIS ce mot de passe",
            "#f87171"
        )
    elif secondes < MINUTE:
        s = int(secondes)
        return (
            f"{s} seconde{'s' if s > 1 else ''}",
            "😱  Craqué avant ta prochaine inspiration",
            "#f87171"
        )
    elif secondes < HEURE:
        m = int(secondes // MINUTE)
        return (
            f"{m} minute{'s' if m > 1 else ''}",
            "☕  Craqué avant que ton café refroidisse",
            "#fb923c"
        )
    elif secondes < JOUR:
        h = int(secondes // HEURE)
        return (
            f"{h} heure{'s' if h > 1 else ''}",
            "📺  Craqué en moins d'une journée de binge-watching",
            "#fb923c"
        )
    elif secondes < MOIS:
        j = int(secondes // JOUR)
        return (
            f"{j} jour{'s' if j > 1 else ''}",
            "📅  Craqué dans le mois — trop court !",
            "#fb923c"
        )
    elif secondes < AN:
        mo = int(secondes // MOIS)
        return (
            f"{mo} mois",
            "🗓️  Craqué dans l'année — encore insuffisant",
            "#facc15"
        )
    elif secondes < SIECLE:
        a = int(secondes // AN)
        return (
            f"{a} an{'s' if a > 1 else ''}",
            "🧓  Craqué de ton vivant… à changer !",
            "#facc15"
        )
    elif secondes < MILLEN:
        s = int(secondes // SIECLE)
        return (
            f"{s} siècle{'s' if s > 1 else ''}",
            "🏛️  Plus long que l'Empire Romain complet",
            "#4ade80"
        )
    elif secondes < MILLION:
        m = int(secondes // MILLEN)
        return (
            f"{m} millénaire{'s' if m > 1 else ''}",
            "🦕  L'humanité n'existait pas encore",
            "#4ade80"
        )
    elif secondes < MILLIARD:
        m = int(secondes // MILLION)
        return (
            f"{m} million{'s' if m > 1 else ''} d'années",
            "🌍  Plus vieux que les dinosaures",
            "#4ade80"
        )
    else:
        m = int(secondes // MILLIARD)
        if m < 14:
            return (
                f"{m} milliard{'s' if m > 1 else ''} d'années",
                "💫  Presque aussi vieux que l'Univers lui-même",
                "#4ade80"
            )
        else:
            return (
                f"{m} milliards d'années",
                "🌌  Plus vieux que l'Univers — tu es intouchable",
                "#4ade80"
            )


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
        "error":         "#f87171",
        "text":          "#e2e2f0",
        "text_muted":    "#9898b0",
        "input_bg":      "#12121f",
        "bar_bg":        "#12121f",
    }

    LARGEUR_FENETRE = 480
    HAUTEUR_FENETRE = 760

    def __init__(self, root):
        self.root = root
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

        # ── Titre ──────────────────────────────────────────────────────────
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

        # Curseur longueur
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

        # Cases à cocher
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

        # ── Indicateur de force ───────────────────────────────────────────
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

        # Barre de progression canvas
        self.canvas_barre = tk.Canvas(inner1, height=8, bg=c["bar_bg"],
                                       highlightthickness=0, bd=0)
        self.canvas_barre.pack(fill="x", pady=(0, 4))
        self.rect_barre = self.canvas_barre.create_rectangle(
            0, 0, 0, 8, fill=c["success"], outline=""
        )

        # Message d'erreur
        self.lbl_erreur = tk.Label(
            inner1, text="", font=("Segoe UI", 9),
            fg=c["error"], bg=c["surface"], height=1
        )
        self.lbl_erreur.pack(pady=(6, 0))

        # Bouton Générer
        self.btn_gen = tk.Button(
            inner1, text="⚡  Générer",
            font=("Segoe UI", 11, "bold"),
            fg="white", bg=c["primary"],
            activeforeground="white", activebackground=c["primary_hover"],
            relief="flat", cursor="hand2", pady=10, bd=0,
            command=self._on_generer
        )
        self.btn_gen.pack(fill="x", pady=(8, 0))

        # ── Carte 2 : résultat ─────────────────────────────────────────────
        tk.Frame(self.root, bg=c["bg"], height=14).pack()

        carte2 = tk.Frame(self.root, bg=c["surface"],
                          highlightbackground=c["border"], highlightthickness=1)
        carte2.pack(fill="x", padx=PX)

        inner2 = tk.Frame(carte2, bg=c["surface"])
        inner2.pack(fill="x", padx=18, pady=14)

        tk.Label(inner2, text="Mot de passe généré",
                 font=("Segoe UI", 9),
                 fg=c["text_muted"], bg=c["surface"]
                 ).pack(anchor="w", pady=(0, 6))

        champ_frame = tk.Frame(inner2, bg=c["input_bg"],
                               highlightbackground=c["border"], highlightthickness=1)
        champ_frame.pack(fill="x")
        self.var_resultat = tk.StringVar()
        tk.Entry(
            champ_frame, textvariable=self.var_resultat,
            font=("Consolas", 13), fg=c["success"],
            bg=c["input_bg"], insertbackground=c["text"],
            relief="flat", bd=8,
            state="readonly", readonlybackground=c["input_bg"]
        ).pack(fill="x")

        self.btn_copier = tk.Button(
            inner2, text="📋  Copier",
            font=("Segoe UI", 10),
            fg=c["text"], bg=c["border"],
            activeforeground="white", activebackground=c["primary"],
            relief="flat", cursor="hand2", pady=8, bd=0,
            command=self._on_copier
        )
        self.btn_copier.pack(fill="x", pady=(10, 0))

        # ── Carte 3 : analyse de sécurité (FEATURE 1) ─────────────────────
        tk.Frame(self.root, bg=c["bg"], height=14).pack()

        carte3 = tk.Frame(self.root, bg=c["surface2"],
                          highlightbackground=c["border"], highlightthickness=1)
        carte3.pack(fill="x", padx=PX)

        inner3 = tk.Frame(carte3, bg=c["surface2"])
        inner3.pack(fill="x", padx=18, pady=16)

        # En-tête avec badge "CYBER"
        row_titre = tk.Frame(inner3, bg=c["surface2"])
        row_titre.pack(fill="x", pady=(0, 12))

        tk.Label(row_titre, text="🛡️  Analyse de sécurité",
                 font=("Segoe UI", 10, "bold"),
                 fg=c["text"], bg=c["surface2"]).pack(side="left")

        tk.Label(row_titre, text=" CYBER ",
                 font=("Segoe UI", 7, "bold"),
                 fg=c["primary"], bg="#2e2a52",
                 padx=5, pady=2).pack(side="right")

        # Ligne entropie
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

        # Ligne temps de crackage
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

        # Analogie fun (ligne entière centrée)
        self.lbl_analogie = tk.Label(
            inner3, text="",
            font=("Segoe UI", 9, "italic"),
            fg=c["text_muted"], bg=c["surface2"],
            wraplength=400, justify="center"
        )
        self.lbl_analogie.pack(pady=(4, 0))

        # Note bas de carte
        tk.Frame(inner3, bg=c["border"], height=1).pack(fill="x", pady=(10, 6))

        tk.Label(
            inner3,
            text="⚡ Simulé sur RTX 4090 — attaque brute force (10¹⁰ essais/sec)",
            font=("Segoe UI", 7),
            fg=c["text_muted"], bg=c["surface2"]
        ).pack()

    # ── Méthodes ──────────────────────────────────────────────────────────────

    def _mettre_a_jour_force(self):
        """Recalcule force + entropie + temps de crack en temps réel."""
        longueur   = self.var_longueur.get()
        majuscules = self.var_maj.get()
        minuscules = self.var_min.get()
        chiffres   = self.var_chf.get()
        symboles   = self.var_sym.get()

        # Indicateur de force (v3, inchangé)
        label, couleur, ratio = evaluer_force(longueur, majuscules, minuscules,
                                               chiffres, symboles)
        self.lbl_force.config(text=label, fg=couleur)

        self.canvas_barre.update_idletasks()
        largeur_totale = self.canvas_barre.winfo_width()
        largeur_remplie = int(largeur_totale * ratio)
        self.canvas_barre.coords(self.rect_barre, 0, 0, largeur_remplie, 8)
        self.canvas_barre.itemconfig(self.rect_barre, fill=couleur)

        # Feature 1 — entropie + temps de crack
        entropie = calculer_entropie(longueur, majuscules, minuscules,
                                      chiffres, symboles)
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
            return
        self.lbl_erreur.config(text="")
        self.var_resultat.set(mdp)
        self.btn_copier.config(text="📋  Copier",
                               fg=self.C["text"], bg=self.C["border"])

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
