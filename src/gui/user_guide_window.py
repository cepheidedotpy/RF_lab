
from __future__ import annotations
import tkinter as tk
import ttkbootstrap as ttk
from typing import TYPE_CHECKING
from tkinter import scrolledtext

if TYPE_CHECKING:
    from .main_window import Window

class UserGuideWindow(ttk.Frame):
    def __init__(self, master, app: "Window"):
        super().__init__(master)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)

        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 1. Introduction & Démarrage
        self.tab_intro = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_intro, text="Démarrage & Sécurité")
        self.setup_intro_tab()

        # 2. Utilisation de l'IHM
        self.tab_gui = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gui, text="Guide de l'IHM")
        self.setup_gui_tab()

        # 3. Procédures de Mesure
        self.tab_measure = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_measure, text="Procédures")
        self.setup_measure_tab()

        # 4. Hardware & Architecture
        self.tab_hardware = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_hardware, text="Hardware")
        self.setup_hardware_tab()

        # 5. Dépannage (Troubleshooting)
        self.tab_trouble = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_trouble, text="Dépannage")
        self.setup_trouble_tab()

        # 6. Maintenance & Données
        self.tab_maintenance = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_maintenance, text="Maintenance")
        self.setup_maintenance_tab()

    def add_scrolled_text(self, parent, content):
        st = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=("Bahnschrift Light", 11), padx=10, pady=10)
        st.insert(tk.END, content)
        st.config(state=tk.DISABLED) # Make it read-only
        st.pack(fill=tk.BOTH, expand=True)
        return st

    def setup_intro_tab(self):
        content = """--- Sécurité ---
• Sécurité RF : Les signaux RF sont conduits. Le risque de rayonnement est faible.
• Protection ESD : Port de bracelet obligatoire pour toute manipulation des équipements (particulièrement le VNA).

--- Démarrage du Banc ---
1. Séquence d'allumage : Respecter l'ordre pour éviter les pics de tension sur le DUT. Vérifier que les sources de tensions sont à 0V avant de commencer.
2. Temps de chauffe : Laisser le matériel se stabiliser thermiquement (~30 min).
3. Initialisation Logicielle : S'assurer que tous les instruments sont accessibles (Resource Page).
"""
        self.add_scrolled_text(self.tab_intro, content)

    def setup_gui_tab(self):
        content = """--- Zones de l'interface ---
• Menu Principal : Accès aux différents tests (SNP, Power, Pull-in, Cycling).
• Resource Page : Configuration des adresses IP des instruments.
• Graphiques : Affichage des mesures.
• Contrôles : Boutons de lancement (Start, Stop, Plot, Update Files).
• Visualisation Double : Le 'Pull-in Test' affiche désormais deux graphiques (Isolation et Dérivée Seconde) pour une validation visuelle précise de la mesure de tension d'actionnement et de.
• Marqueurs : Points rouges (PI) et croix vertes (PO) indiquent les événements détectés.

--- Configuration ---
• Avant tout test, vérifiez les adresses IP dans la 'Resource Page'.
• Sélectionnez les répertoires de sauvegarde via les champs 'Directory'.
• Utilisez le bouton 'Update Files' pour rafraîchir la liste des fichiers disponibles.
"""
        self.add_scrolled_text(self.tab_gui, content)

    def setup_measure_tab(self):
        content = """--- Procédure de Mesure (Pas-à-pas) ---
1. Configuration des instruments : Fréquence centrale, Span, Puissance de sortie.
2. Connexion du DUT : Respectez l'alignement et les précautions ESD.
3. Exécution des tests :
   • SNP Test : Mesure de gain/pertes (S21) et adaptation (S11).
   • Power Test : Mesure de tenue en puissance.
   • Pull-in Test : Détermination des tensions d'actionnement. (Algorithme amélioré supportant les transitions douces et le filtrage du bruit).
   • Cycling : Test de fiabilité sur grand nombre de cycles.
4. Capture des données : Sauvegarde automatique vers les répertoires configurés.

--- Algorithme Pull-in/out (v2) ---
• Méthode : Analyse de la dérivée seconde (D2) du signal de détection.
• Détection robuste : Utilisation de 'find_peaks' avec filtrage par proéminence.
• Sécurité : Fallback automatique vers un seuil de 10% d'isolation si la pente est trop faible.

--- Calibration ---
• Étape critique pour tenir compte des pertes dans les câbles et transitions.
• Vérifiez le standard de calibration avant de valider la correction.
"""
        self.add_scrolled_text(self.tab_measure, content)

    def setup_hardware_tab(self):
        content = """--- Architecture du Banc ---
• VNA : Analyseur de réseau vectoriel pour les paramètres S.
• RF Generator (SMB100A/SMF100A) : Source principale jusqu'à 20 GHz.
• Amplificateur Logarithmique (HMC662LP3E) : Conversion puissance RF -> DC (5-10 ns temps de réponse).
• Amplificateur de puissance (BLMA6018-35) : 35W crête pour les tests forte puissance.
• Système eVue III : Visualisation numérique des dispositifs.

--- Connexions ---
• Connecteurs : SMA, N, 2.92mm.
• Serrage : Utilisez une clé dynamométrique aux couples requis.
"""
        self.add_scrolled_text(self.tab_hardware, content)

    def setup_trouble_tab(self):
        content = """--- Gestion des Erreurs ---
• Message 'ALC unlocked' : Vérifiez que la puissance RF est réglée avant d'activer l'output.
• Communication VISA : Si un instrument ne répond pas, vérifiez l'adresse IP dans 'Resource Page' et effectuez un Ping.
• Logs Système : En cas de plantage, vérifiez le fichier 'changes_log.md' ou les sorties console pour diagnostiquer.

--- Initialisation ---
• Assurez-vous que l'IHM est connectée à la base de données (si applicable).
• Vérifiez que le 'Main Window' affiche bien la version courante (v10).
"""
        self.add_scrolled_text(self.tab_trouble, content)

    def setup_maintenance_tab(self):
        content = """--- Gestion des Données ---
• Arborescence : Les fichiers sont rangés selon la structure : Project/Cell/Device.
• Formats : .txt (brut), .s2p/.s3p (S-parameters), .csv (logs de puissance/cyclage).
• Backup : Périodicité des sauvegardes recommandée sur serveur.

--- Maintenance ---
• Connecteurs : Nettoyer à l'alcool isopropylique avec précaution.
• Inspection : Vérification visuelle des câbles à la loupe régulièrement.
• Logiciel : Assurez-vous d'utiliser la dernière version (Current v10).
"""
        self.add_scrolled_text(self.tab_maintenance, content)
