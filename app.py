import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="PI Planning", layout="wide")
st.title("PI Planning - Capacity Planning avec ETA")

# =========================
# ITÉRATIONS
# =========================
iterations = [
    {"name": "Itération #1", "start": "2025-12-22", "end": "2026-01-09"},
    {"name": "Itération #2", "start": "2026-01-12", "end": "2026-01-30"},
    {"name": "Itération #3", "start": "2026-02-02", "end": "2026-02-20"},
    {"name": "Itération #4", "start": "2026-02-23", "end": "2026-03-13"},
]

# =========================
# ÉQUIPES PAR DÉFAUT
# =========================
default_teams = [
    "Product Owner",
    "Marketing",
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
# BACKLOG (tes projets)
# =========================
projects = [
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Équipe": "Product unit", "Charge": 6, "Priorité": 1, "Statut": "To Do"},
    {"Projet": "Website Revamp - homepage telephony", "Équipe": "Dev Web Front", "Charge": 8, "Priorité": 2, "Statut": "To Do"},
    {"Projet": "VPS - Add more choice on Disk options", "Équipe": "Dev Web Back", "Charge": 5, "Priorité": 3, "Statut": "To Do"},
    {"Projet": "Zimbra add yearly commitment prod", "Équipe": "Product unit", "Charge": 4, "Priorité": 4, "Statut": "To Do"},
    {"Projet": "Telco - Create new plans for Trunk product", "Équipe": "Dev Order", "Charge": 7, "Priorité": 5, "Statut": "To Do"},
    {"Projet": "Funnel order improvement - Pre-select OS APP", "Équipe": "Dev Web Front", "Charge": 6, "Priorité": 6, "Statut": "To Do"},
]

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
    """Calcule l'ETA de chaque projet basé sur la capacité nette"""
    net_capacity = calculate_net_capacity()
    remaining_capacity = net_capacity.copy()
    planning = []
    
    for p in sorted(projects, key=lambda x: x["Priorité"]):
        for it in iterations:
            key = (p["Équipe"], it["name"])
            capacity_available = remaining_capacity.get(key, 0)
            
            if capacity_available >= p["Charge"]:
                remaining_capacity[key] -= p["Charge"]
                planning.append({
                    "Projet": p["Projet"],
                    "Équipe": p["Équipe"],
                    "Début": it["start"],
                    "Fin": it["end"],
                    "Itération": it["name"],
                    "ETA": it["end"],
                    "Statut": p["Statut"],
                    "Priorité": p["Priorité"]
                })
                break
    
    return planning, remaining_capacity

# =========================
# ONGLETS
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Capacités", "🗓️ Congés & Run", "📈 Gantt & ETA", "✅ Tâches en cours"])

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
        today = datetime.now().date()
        
        # Filtrer les tâches en cours
        df_planning["Début_dt"] = pd.to_datetime(df_planning["Début"]).dt.date
        df_planning["ETA_dt"] = pd.to_datetime(df_planning["ETA"]).dt.date
        
        in_progress = df_planning[
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
