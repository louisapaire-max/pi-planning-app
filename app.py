import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from workalendar.europe import France

# ═════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="PI Planning - Capacity Tool", layout="wide")
st.title("📊 PI Planning - Capacity Planning avec ETA")

# Vérification rapide de l'import plotly
try:
    import plotly.express as px
except ImportError:
    st.error("Le module 'plotly' est manquant. Installez-le via pip install plotly")
    st.stop()

CAL_FRANCE = France()

# ═════════════════════════════════════════════════════════════════════
# DONNÉES STATIQUES
# ═════════════════════════════════════════════════════════════════════

ITERATIONS = [
    {"name": "Itération #2", "start": "2026-01-12", "end": "2026-01-30"},
    {"name": "Itération #3", "start": "2026-02-02", "end": "2026-02-20"},
    {"name": "Itération #4", "start": "2026-02-23", "end": "2026-03-13"},
]

TEAMS = [
    "Product Owner", "Product unit", "QQE", "Marketing", "Design",
    "Webmaster", "Dev Web Front", "Dev Web Back", "Dev Order",
    "Tracking", "SEO", "QA", "Traduction"
]

TASKS = [
    {"name": "Brief requester Delivery", "team": "Product Owner", "order": 1, "charge": 1},
    {"name": "Catalogue Delivery", "team": "Product unit", "order": 2, "charge": 2},
    {"name": "Control d'interface", "team": "QQE", "order": 3, "charge": 1},
    {"name": "Content", "team": "Marketing", "order": 4, "charge": 2},
    {"name": "Documentation Project", "team": "Product Owner", "order": 5, "charge": 1},
    {"name": "Kick-off Digital", "team": "Product Owner", "order": 6, "charge": 0.5},
    {"name": "Etude d'impact", "team": "Product Owner", "order": 7, "charge": 2},
    {"name": "Maquettes/Wireframe", "team": "Design", "order": 8, "charge": 3},
    {"name": "Redaction US / Jira", "team": "Product Owner", "order": 9, "charge": 2},
    {"name": "Refinement", "team": "Product Owner", "order": 10, "charge": 1},
    {"name": "Integration OCMS", "team": "Webmaster", "order": 11, "charge": 2},
    {"name": "Dev Website Front", "team": "Dev Web Front", "order": 12, "charge": 5},
    {"name": "Dev Website Back", "team": "Dev Web Back", "order": 13, "charge": 5},
    {"name": "Dev Order", "team": "Dev Order", "order": 14, "charge": 3},
    {"name": "Tracking", "team": "Tracking", "order": 15, "charge": 2},
    {"name": "check SEO", "team": "SEO", "order": 16, "charge": 1},
    {"name": "QA & UAT (langue source)", "team": "QA", "order": 17, "charge": 3},
    {"name": "Traduction", "team": "Traduction", "order": 18, "charge": 2},
    {"name": "QA WW", "team": "QA", "order": 19, "charge": 2},
    {"name": "Plan de Production", "team": "Product Owner", "order": 20, "charge": 1},
    {"name": "PROD", "team": "Product Owner", "order": 21, "charge": 1}
]

PROJECTS = [
    {"name": "Email - Add File Edition to Zimbra Pro", "priority": 1, "status": "To Do"},
    {"name": "Website Revamp - homepage telephony", "priority": 2, "status": "To Do"},
    {"name": "VPS - Add more choice on Disk options", "priority": 3, "status": "To Do"},
    {"name": "Zimbra add yearly commitment prod", "priority": 4, "status": "To Do"},
    {"name": "Telco - Create new plans for Trunk product", "priority": 5, "status": "To Do"},
    {"name": "Funnel order improvement - Pre-select OS & APP", "priority": 6, "status": "To Do"},
    {"name": "[VPS 2026 RBX7] - Deploy RBX7 region for VPS 2026", "priority": 7, "status": "To Do"},
    {"name": "lot 2 website page Phone & Headset", "priority": 8, "status": "To Do"},
    {"name": "Website Revamp - numbers page", "priority": 9, "status": "To Do"},
    {"name": "VOIP Offers - Update 40 Included Destinations", "priority": 10, "status": "To Do"},
    {"name": "Email - Website Quick Wins - Zimbra Webmail", "priority": 11, "status": "To Do"},
    {"name": "Email - Website Quick Wins - New Exchange Product pages", "priority": 12, "status": "To Do"},
    {"name": "VPS - Website New pages (Resellers & Panels)", "priority": 13, "status": "To Do"},
    {"name": "Email - Website Quick Wins", "priority": 14, "status": "To Do"},
    {"name": "Revamp Telephony", "priority": 15, "status": "To Do"},
]

TASK_STATUSES = ["À faire", "En cours", "Terminé", "Bloqué", "En attente"]

# ═════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═════════════════════════════════════════════════════════════════════

# Initialisation des capacités par défaut (10 jours)
if "capacity" not in st.session_state:
    st.session_state.capacity = {}
    for team in TEAMS:
        for it in ITERATIONS:
            st.session_state.capacity[(team, it["name"])] = 10.0

# Initialisation des congés (0 jour)
if "leaves" not in st.session_state:
    st.session_state.leaves = {}
    for team in TEAMS:
        for it in ITERATIONS:
            st.session_state.leaves[(team, it["name"])] = 0.0

# Initialisation du run (0 jour)
if "run_days" not in st.session_state:
    st.session_state.run_days = {}
    for team in TEAMS:
        for it in ITERATIONS:
            st.session_state.run_days[(team, it["name"])] = 0.0

# Initialisation des détails spécifiques aux tâches (dates et statuts personnalisés)
if "task_details" not in st.session_state:
    st.session_state.task_details = {}

# ═════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═════════════════════════════════════════════════════════════════════

def get_net_capacity(team: str, iteration: dict) -> float:
    """Calcule la capacité nette : Capacité Brute - Congés - Run."""
    key = (team, iteration["name"])
    brute = st.session_state.capacity.get(key, 0)
    leaves = st.session_state.leaves.get(key, 0)
    run = st.session_state.run_days.get(key, 0)
    return max(0, brute - leaves - run)

def get_task_key(row):
    """Génère une clé unique pour chaque tâche d'un projet."""
    prio = row.get('Priorité')
    proj = row.get('Projet')
    tache = row.get('Tâche')
    equipe = row.get('Équipe')
    return f"{prio}_{proj}_{tache}_{equipe}"

def get_holidays_2026():
    """Récupère les jours fériés 2026 en France format String ISO pour Plotly."""
    holidays = CAL_FRANCE.holidays(2026)
    # On retourne juste la liste des dates (ex: '2026-01-01')
    return [d[0].isoformat() for d in holidays]

def calculate_planning():
    """Algorithme principal de placement des tâches selon la capacité disponible."""
    remaining = {}
    for team in TEAMS:
        for it in ITERATIONS:
            remaining[(team, it["name"])] = get_net_capacity(team, it)
    
    planning = []
    
    # Tri des projets par priorité
    for project in sorted(PROJECTS, key=lambda x: x["priority"]):
        # Tri des tâches par ordre logique
        for task in sorted(TASKS, key=lambda t: t["order"]):
            placed = False
            for it in ITERATIONS:
                key = (task["team"], it["name"])
                # Si capacité suffisante dans cette itération
                if (remaining.get(key, 0) >= task["charge"]):
                    remaining[key] -= task["charge"]
                    
                    # Calcul des dates théoriques basées sur l'itération
                    start_date = it["start"]
                    end_date = it["end"]

                    planning.append({
                        "Priorité": project["priority"],
                        "Projet": project["name"],
                        "Tâche": task["name"],
                        "Équipe": task["team"],
                        "Itération": it["name"],
                        "Début": start_date,
                        "Fin": end_date,
                        "Charge": task["charge"],
                        "Statut": "✅ Planifié"
                    })
                    placed = True
                    break
            
            if not placed:
                planning.append({
                    "Priorité": project["priority"],
                    "Projet": project["name"],
                    "Tâche": task["name"],
                    "Équipe": task["team"],
                    "Itération": "⚠️ Dépassement",
                    "Début": None,
                    "Fin": None,
                    "Charge": task["charge"],
                    "Statut": "❌ Bloqué"
                })
    
    return planning, remaining

# ═════════════════════════════════════════════════════════════════════
# INTERFACE PRINCIPALE
# ═════════════════════════════════════════════════════════════════════

tab_planning, tab_capa, tab_cong, tab_time, tab_active = st.tabs([
    "📋 Planning & ETA",
    "📊 Capacités",
    "🏖️ Congés & Run",
    "📈 Timeline Globale",
    "✅ En cours"
])

# ---------------------------------------------------------------------
# ONGLET 1: PLANNING & ETA
# ---------------------------------------------------------------------
with tab_planning:
    st.subheader("📋 Planning détaillé & Gantt par Projet")
    
    # 1. Calcul initial
    planning, remaining = calculate_planning()
    df_plan = pd.DataFrame(planning)
    
    if not df_plan.empty:
        # Appliquer les overrides depuis le session_state si existants
        df_plan["Start Date"] = df_plan.apply(
            lambda row: st.session_state.task_details.get(get_task_key(row), {}).get("start_date", row["Début"]),
            axis=1
        )
        df_plan["End Date"] = df_plan.apply(
            lambda row: st.session_state.task_details.get(get_task_key(row), {}).get("end_date", row["Fin"]),
            axis=1
        )
        df_plan["Statut Custom"] = df_plan.apply(
            lambda row: st.session_state.task_details.get(get_task_key(row), {}).get("status", "À faire"),
            axis=1
        )
        
        # Conversion stricte en datetime
        df_plan["Start Date"] = pd.to_datetime(df_plan["Start Date"], errors='coerce')
        df_plan["End Date"] = pd.to_datetime(df_plan["End Date"], errors='coerce')

    # 2. Sélecteur de projet
    project_list = ["Vue Globale (Édition)"] + sorted(list(df_plan["Projet"].unique())) if not df_plan.empty else []
    selected_project = st.selectbox("🎯 Sélectio
