"""
🔐 Anchor Vault — Générateur de mots de passe sécurisé
Stack : Python 3.10+ | Tkinter | secrets
Version : 3.0 — ajout indicateur de force
"""

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
#  INTERFACE GRAPHIQUE
# ══════════════════════════════════════════════════════════════════════════════

class AnchorVaultApp:

    C = {
        "bg":            "#1e1e2e",
        "surface":       "#2a2a3e",
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

    HAUTEUR_FENETRE = 600
    LARGEUR_FENETRE = 460

    def __init__(self, root):
        self.root = root
        self._configurer_fenetre()
        self._construire_ui()
        self._mettre_a_jour_force()

    def _configurer_fenetre(self):
        self.root.title("Anchor Vault v3")
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
            highlightthickness=0, bd=0, showvalue=False, length=380,
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

    # ── Méthodes ──────────────────────────────────────────────────────────────

    def _mettre_a_jour_force(self):
        """Recalcule et affiche l'indicateur de force en temps réel."""
        label, couleur, ratio = evaluer_force(
            self.var_longueur.get(),
            self.var_maj.get(), self.var_min.get(),
            self.var_chf.get(), self.var_sym.get()
        )
        self.lbl_force.config(text=label, fg=couleur)

        # Mise à jour de la barre canvas
        self.canvas_barre.update_idletasks()
        largeur_totale = self.canvas_barre.winfo_width()
        largeur_remplie = int(largeur_totale * ratio)
        self.canvas_barre.coords(self.rect_barre, 0, 0, largeur_remplie, 8)
        self.canvas_barre.itemconfig(self.rect_barre, fill=couleur)

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
