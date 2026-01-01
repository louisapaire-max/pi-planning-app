import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import streamlit_shadcn_ui as ui

st.set_page_config(page_title="PI Planning", layout="wide")
st.title("PI Planning - Capacity Planning avec ETA")


# =========================
# ITÉRATIONS
# =========================
iterations = [
    {"name": "Itération #2", "start": "2026-01-12", "end": "2026-01-30"},
    {"name": "Itération #3", "start": "2026-02-02", "end": "2026-02-20"},
    {"name": "Itération #4", "start": "2026-02-23", "end": "2026-03-13"},
]

# =========================
# ÉQUIPES PAR DÉFAUT
# =========================
default_teams = [
    "Product unit",
    "Dev Web Front",
    "Dev Web Back",
    "Dev Order",
    "Webmaster",
    "SEO",
    "Tracking",
    "QA"
]

# =========================
# =========================
# BACKLOG - Projets et Tâches
# =========================

# Template de tâches Catalogue Delivery (sans équipe assignée par défaut)
catalogue_tasks_template = [
    {"Tâche": "Brief requester Delivery", "Équipe": "Product Owner", "Ordre": 1, "Charge": 1},
    {"Tâche": "Catalogue Delivery", "Équipe": "Product unit", "Ordre": 2, "Charge": 2},
    {"Tâche": "Contrat d'interface", "Équipe": "QOE", "Ordre": 3, "Charge": 1},
    {"Tâche": "Content", "Équipe": "Marketing", "Ordre": 4, "Charge": 2},
    {"Tâche": "Documentation Project", "Équipe": "Product Owner", "Ordre": 5, "Charge": 1},
    {"Tâche": "Kick-off Digital", "Équipe": "Product Owner", "Ordre": 6, "Charge": 0.5},
    {"Tâche": "Étude d'impact", "Équipe": "Product Owner", "Ordre": 7, "Charge": 2},
    {"Tâche": "Maquettes/Wireframe", "Équipe": "Design", "Ordre": 8, "Charge": 3},
    {"Tâche": "Rédaction US / Jira", "Équipe": "Product Owner", "Ordre": 9, "Charge": 2},
    {"Tâche": "Refinement", "Équipe": "Product Owner", "Ordre": 10, "Charge": 1},
    {"Tâche": "Integration OCMS", "Équipe": "Webmaster", "Ordre": 11, "Charge": 2},
    {"Tâche": "Dev Website Front", "Équipe": "Dev Web Front", "Ordre": 12, "Charge": 5},
    {"Tâche": "Dev Website Back", "Équipe": "Dev Web Back", "Ordre": 13, "Charge": 5},
    {"Tâche": "Dev Order", "Équipe": "Dev Order", "Ordre": 14, "Charge": 3},
    {"Tâche": "Tracking", "Équipe": "Tracking", "Ordre": 15, "Charge": 2},
    {"Tâche": "check SEO", "Équipe": "SEO", "Ordre": 16, "Charge": 1},
    {"Tâche": "QA & UAT (langue source)", "Équipe": "QA", "Ordre": 17, "Charge": 3},
    {"Tâche": "Traduction", "Équipe": "Traduction", "Ordre": 18, "Charge": 2},
    {"Tâche": "QA WW", "Équipe": "QA", "Ordre": 19, "Charge": 2},
    {"Tâche": "Plan de Production", "Équipe": "Product Owner", "Ordre": 20, "Charge": 1},
    {"Tâche": "PROD", "Équipe": "Product Owner", "Ordre": 21, "Charge": 1},
]
# Liste des projets
projects = [
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Priorité": 1, "Statut": "To Do"},
    {"Projet": "Website Revamp - homepage telephony", "Priorité": 2, "Statut": "To Do"},
    {"Projet": "VPS - Add more choice on Disk options", "Priorité": 3, "Statut": "To Do"},
    {"Projet": "Zimbra add yearly commitment prod", "Priorité": 4, "Statut": "To Do"},
    {"Projet": "Telco - Create new plans for Trunk product", "Priorité": 5, "Statut": "To Do"},
    {"Projet": "Funnel order improvement - Pre-select OS & APP", "Priorité": 6, "Statut": "To Do"},
    {"Projet": "[VPS 2026 RBX7] - Deploy RBX7 region for VPS 2026", "Priorité": 7, "Statut": "To Do"},
    {"Projet": "lot 2 website page Phone & Headset", "Priorité": 8, "Statut": "To Do"},
    {"Projet": "Website Revamp - numbers page", "Priorité": 9, "Statut": "To Do"},
    {"Projet": "VOIP Offers - Update 40 Included Destinations", "Priorité": 10, "Statut": "To Do"},
    {"Projet": "Email - Website Quick Wins - Zimbra Webmail", "Priorité": 11, "Statut": "To Do"},
    {"Projet": "Email - Website Quick Wins - New Exchange Product pages", "Priorité": 12, "Statut": "To Do"},
    {"Projet": "VPS - Website New pages (Resellers & Panels)", "Priorité": 13, "Statut": "To Do"},
    {"Projet": "Email - Website Quick Wins", "Priorité": 14, "Statut": "To Do"},
    {"Projet": "Revamp Telephony", "Priorité": 15, "Statut": "To Do"},
]


# Extraire la liste des noms de projets
projects_names = [p["Projet"] for p in projects]

# =========================
# ONGLET 1 - SIZING PROJET/ÉQUIPE
# =========================

st.header("📊 PI Planning - Sizing des Projets")

tab1, tab2 = st.tabs(["Sizing Projets", "Planning & Gantt"])

with tab1:
    st.subheader("Matrice de Sizing: Projets x Équipes")
    st.markdown("Renseignez la charge de travail (en jours) pour chaque combinaison projet/équipe")
    
    # Initialiser le session state pour les sizings
    if "project_sizing" not in st.session_state:
        st.session_state.project_sizing = {}
        for project in projects_names:
            for team in default_teams:
                key = f"{project}_{team}"
                st.session_state.project_sizing[key] = 0.0
    
    # Créer un DataFrame pour afficher la matrice
    sizing_data = {}
    for team in default_teams:
        sizing_data[team] = []
        for project in projects_names:
            key = f"{project}_{team}"
            sizing_data[team].append(st.session_state.project_sizing.get(key, 0.0))
    
    df_sizing = pd.DataFrame(sizing_data, index=projects_names)
    
    # Afficher le DataFrame éditable
    edited_df = st.data_editor(
        df_sizing,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            team: st.column_config.NumberColumn(
                team,
                min_value=0,
                max_value=100,
                step=0.5,
                format="%.1f j"
            ) for team in default_teams
        }
    )
    
    # Mettre à jour le session state avec les valeurs éditées
    for team in default_teams:
        for idx, project in enumerate(projects_names):
            key = f"{project}_{team}"
            st.session_state.project_sizing[key] = edited_df[team].iloc[idx]
    
    # Statistiques rapides
    st.subheader("📊 Statistiques")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_charge = edited_df.sum().sum()
        st.metric("Charge totale", f"{total_charge:.1f} jours")
    
    with col2:
        charge_par_equipe = edited_df.sum(axis=0)
        equipe_max = charge_par_equipe.idxmax()
        st.metric("Équipe la plus chargée", equipe_max, f"{charge_par_equipe[equipe_max]:.1f} j")
    
    with col3:
        charge_par_projet = edited_df.sum(axis=1)
        projet_max = charge_par_projet.idxmax()
        st.metric("Projet le plus gros", projet_max[:30] + "...", f"{charge_par_projet[projet_max]:.1f} j")

with tab2:
    
    st.subheader("Planning et Diagramme de Gantt")
    st.info("🚧 Section en cours de développement - Affichera le planning détaillé et le Gantt")


# SESSION STATE pour les affectations tâche-équipe
if "task_assignments" not in st.session_state:
    st.session_state.task_assignments = {}
    # Initialiser avec valeurs par défaut
    for p in projects:
        for task in catalogue_tasks_template:
            key = (p["Projet"], task["Tâche"])
            st.session_state.task_assignments[key] = "Product Owner"  # Équipe par défaut
# =========================
# SESSION STATE – CAPACITÉS
# =========================
if "capacity" not in st.session_state:
    st.session_state.capacity = {}
    for team in default_teams:
        for it in iterations:
            st.session_state.capacity[(team, it["name"])] = 10.0  # Capacité par défaut

# =========================
# SESSION STATE – CONGÉS & RUN DAYS
# =========================
if "leaves" not in st.session_state:
    st.session_state.leaves = {}
    for team in default_teams:
        for it in iterations:
            st.session_state.leaves[(team, it["name"])] = 0.0

if "run_days" not in st.session_state:
    st.session_state.run_days = {}
    for team in default_teams:
        for it in iterations:
            st.session_state.run_days[(team, it["name"])] = 0.0

# =========================
# CALCUL CAPACITÉ NETTE
# =========================
def calculate_net_capacity():
    """Calcule la capacité nette = capacité - congés - run days"""
    net_capacity = {}
    for team in default_teams:
        for it in iterations:
            key = (team, it["name"])
            brute = st.session_state.capacity.get(key, 0)
            leaves = st.session_state.leaves.get(key, 0)
            run = st.session_state.run_days.get(key, 0)
            net_capacity[key] = max(0, brute - leaves - run)
    return net_capacity

# =========================
# CALCUL DES ETA
# =========================
def calculate_eta():
    """Calcule l'ETA avec gestion des tâches détaillées par projet"""
    net_capacity = calculate_net_capacity()
    remaining_capacity = net_capacity.copy()
    planning = []
    
    for p in sorted(projects, key=lambda x: x["Priorité"]):
        # Pour chaque projet, traiter toutes ses tâches dans l'ordre
        for task in sorted(catalogue_tasks_template, key=lambda t: t["Ordre"]):
            key_assignment = (p["Projet"], task["Tâche"])
            assigned_team = st.session_state.task_assignments.get(key_assignment, "Product Owner")
            
            placed = False
            for it in iterations:
                key_capacity = (assigned_team, it["name"])
                capacity_available = remaining_capacity.get(key_capacity, 0)
                
                if capacity_available >= task["Charge"]:
                    remaining_capacity[key_capacity] -= task["Charge"]
                    planning.append({
                        "Projet": p["Projet"],
                        "Tâche": task["Tâche"],
                        "Équipe": assigned_team,
                        "Début": it["start"],
                        "Fin": it["end"],
                        "Itération": it["name"],
                        "ETA": it["end"],
                        "Statut": p["Statut"],
                        "Priorité": p["Priorité"],
                        "Ordre": task["Ordre"]
                    })
                    placed = True
                    break
            
            if not placed:
                # Tâche hors capacité
                planning.append({
                    "Projet": p["Projet"],
                    "Tâche": task["Tâche"],
                    "Équipe": assigned_team,
                    "Début": None,
                    "Fin": None,
                    "Itération": "Hors capacité",
                    "ETA": "Dépassement",
                    "Statut": "Bloqué",
                    "Priorité": p["Priorité"],
                    "Ordre": task["Ordre"]
                })
    
    return planning, remaining_capacity
# =========================
# ONGLETS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Capacités", "🗓️ Congés & Run", "📝 Affectation Tâches", "📈 Gantt & ETA", "✅ Tâches en cours"])
# =========================================================
# ONGLET 1 – CAPACITÉS
# =========================================================
with tab1:
    st.subheader("Capacité par équipe et par itération (jours)")
    st.info("💡 Saisir la capacité brute de chaque équipe par itération")
    
    rows = []
    for team in default_teams:
        row = {"Équipe": team}
        cols = st.columns(len(iterations) + 1)
        cols[0].markdown(f"**{team}**")
        
        for idx, it in enumerate(iterations):
            key = (team, it["name"])
            with cols[idx + 1]:
                value = st.number_input(
                    it["name"],
                    min_value=0.0,
                    step=0.5,
                    value=st.session_state.capacity[key],
                    key=f"cap_{team}_{it['name']}",
                    label_visibility="collapsed"
                )
                st.session_state.capacity[key] = value
                row[it["name"]] = value
        rows.append(row)
    
    st.divider()
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# =========================================================
# ONGLET 2 – CONGÉS & RUN DAYS
# =========================================================
with tab2:
    st.subheader("Congés et jours de run par équipe et itération")
    st.info("💡 Déclarer les congés et jours de run pour chaque équipe")
    
    col_leave, col_run = st.columns(2)
    
    with col_leave:
        st.markdown("### 🏖️ Congés (jours)")
        leave_rows = []
        for team in default_teams:
            row = {"Équipe": team}
            for it in iterations:
                key = (team, it["name"])
                row[it["name"]] = st.number_input(
                    f"{team} – {it['name']} congés",
                    min_value=0.0,
                    step=0.5,
                    value=st.session_state.leaves[key],
                    key=f"leave_{team}_{it['name']}"
                )
                st.session_state.leaves[key] = row[it["name"]]
            leave_rows.append(row)
        st.dataframe(pd.DataFrame(leave_rows), use_container_width=True, hide_index=True)
    
    with col_run:
        st.markdown("### 🔧 Run days (jours)")
        run_rows = []
        for team in default_teams:
            row = {"Équipe": team}
            for it in iterations:
                key = (team, it["name"])
                row[it["name"]] = st.number_input(
                    f"{team} – {it['name']} run",
                    min_value=0.0,
                    step=0.5,
                    value=st.session_state.run_days[key],
                    key=f"run_{team}_{it['name']}"
                )
                st.session_state.run_days[key] = row[it["name"]]
            run_rows.append(row)
        st.dataframe(pd.DataFrame(run_rows), use_container_width=True, hide_index=True)
    
    # Afficher la capacité nette
    st.divider()
    st.markdown("### 📊 Capacité nette (Capacité - Congés - Run)")
    net_capacity = calculate_net_capacity()
    net_rows = []
    for team in default_teams:
        row = {"Équipe": team}
        for it in iterations:
            key = (team, it["name"])
            row[it["name"]] = net_capacity[key]
        net_rows.append(row)
    st.dataframe(pd.DataFrame(net_rows), use_container_width=True, hide_index=True)

# =========================================================
# ONGLET 3 – GANTT & ETA
# =========================================================
with tab3:
    st.subheader("Gantt PI Planning avec ETA")
    
    planning, remaining = calculate_eta()
    
    if planning:
        df_gantt = pd.DataFrame(planning)
        
        # Afficher tableau avec ETA
        st.markdown("### 📋 Planning des projets avec ETA")
        display_cols = ["Priorité", "Projet", "Équipe", "Itération", "ETA", "Statut"]
        st.dataframe(df_gantt[display_cols].sort_values("Priorité"), use_container_width=True, hide_index=True)
        
        # Gantt chart
        st.markdown("### 📊 Visualisation Gantt")
        fig = px.timeline(
            df_gantt,
            x_start="Début",
            x_end="Fin",
            y="Équipe",
            color="Projet",
            hover_data=["Itération", "ETA", "Priorité"]
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
        
        # Capacité restante
        st.markdown("### 📉 Capacité restante après planification")
        remaining_rows = []
        for team in default_teams:
            row = {"Équipe": team}
            for it in iterations:
                key = (team, it["name"])
                row[it["name"]] = remaining[key]
            remaining_rows.append(row)
        st.dataframe(pd.DataFrame(remaining_rows), use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Aucun projet planifié. Vérifie les capacités.")

# =========================================================
# ONGLET 4 – TÂCHES EN COURS
# =========================================================
with tab4:
    st.subheader("Suivi des tâches en cours")
    st.info("💡 Basé sur la date du jour et les ETA calculés")
    
    planning, _ = calculate_eta()
    
    if planning:
        df_planning = pd.DataFrame(planning)
        today = pd.Timestamp.now().normalize()
        
        # Filtrer les tâches en cours
        # Filtrer les tâches en cours (ignorer les erreurs de conversion de date)
        df_planning["Début_dt"] = pd.to_datetime(df_planning["Début"], errors='coerce').dt.date
        df_planning["ETA_dt"] = pd.to_datetime(df_planning["ETA"], errors='coerce').dt.date        
        # Filtrer uniquement les tâches avec des dates valides
        in_progress = df_planning[
            (df_planning["Début_dt"].notna()) &
            (df_planning["ETA_dt"].notna()) &
            (df_planning["Début_dt"] <= today) & 
            (df_planning["ETA_dt"] >= today)
        ]        
        if not in_progress.empty:
            st.markdown(f"### ✅ Tâches actives au {today.strftime('%d/%m/%Y')}")
            display_cols = ["Priorité", "Projet", "Équipe", "Itération", "Début", "ETA", "Statut"]
            st.dataframe(in_progress[display_cols].sort_values("Priorité"), use_container_width=True, hide_index=True)
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tâches en cours", len(in_progress))
            with col2:
                st.metric("Équipes actives", in_progress["Équipe"].nunique())
            with col3:
                st.metric("Itérations actives", in_progress["Itération"].nunique())
        else:
            st.info("Aucune tâche en cours pour la date du jour.")
    else:
        st.warning("Aucun planning disponible.")









