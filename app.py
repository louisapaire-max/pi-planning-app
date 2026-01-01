import streamlit as st
import pandas as pd

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="PI Planning", layout="wide")
st.title("PI Planning – Outil interactif")

# =============================
# SPRINTS / ITÉRATIONS
# =============================
sprints = [
    {"name": "Itération #1", "start": "2025-12-22", "end": "2026-01-09"},
    {"name": "Itération #2", "start": "2026-01-12", "end": "2026-01-30"},
    {"name": "Itération #3", "start": "2026-02-02", "end": "2026-02-20"},
    {"name": "Itération #4", "start": "2026-02-23", "end": "2026-03-13"},
    {"name": "Itération #5", "start": "2026-03-16", "end": "2026-03-20"},
]

# =============================
# SESSION STATE
# =============================
if "teams" not in st.session_state:
    st.session_state.teams = {}
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# =============================
# SIDEBAR – GESTION DES ÉQUIPES
# =============================
st.sidebar.header("Équipes")

new_team = st.sidebar.text_input("Nouvelle équipe")
if st.sidebar.button("Ajouter l'équipe"):
    if new_team and new_team not in st.session_state.teams:
        st.session_state.teams[new_team] = []

# =============================
# SIDEBAR – AJOUT DÉVELOPPEUR
# =============================
st.sidebar.header("Ajouter un développeur")

if st.session_state.teams:
    team_selected = st.sidebar.selectbox(
        "Équipe",
        list(st.session_state.teams.keys())
    )

    dev_name = st.sidebar.text_input("Nom du développeur")
    dev_capacity = st.sidebar.number_input("Capacité / itération (jours)", 0.0, 30.0, 5.0)
    dev_run = st.sidebar.number_input("Jours de run", 0.0, 10.0, 0.0)
    dev_off = st.sidebar.number_input("Jours de congés", 0.0, 10.0, 0.0)

    if st.sidebar.button("Ajouter le développeur"):
        st.session_state.teams[team_selected].append({
            "name": dev_name,
            "capacity": dev_capacity,
            "run": dev_run,
            "off": dev_off
        })

# =============================
# CALCUL DES CAPACITÉS
# =============================
capacity = {}

for team, devs in st.session_state.teams.items():
    for sprint in sprints:
        total = 0
        for dev in devs:
            total += dev["capacity"] - dev["run"] - dev["off"]
        capacity[(team, sprint["name"])] = round(max(total, 0), 1)

# =============================
# AFFICHAGE CAPACITÉS
# =============================
st.header("Capacité par équipe et itération")

cap_rows = []
for (team, sprint), cap in capacity.items():
    cap_rows.append({
        "Équipe": team,
        "Itération": sprint,
        "Capacité disponible": cap
    })

if cap_rows:
    st.dataframe(pd.DataFrame(cap_rows), use_container_width=True)
else:
    st.info("Ajoute des équipes et des développeurs pour voir les capacités.")


st.header("Backlog – Ajouter un projet")

if st.session_state.teams:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        project_name = st.text_input("Nom du projet")

    with col2:
        project_team = st.selectbox(
            "Équipe",
            list(st.session_state.teams.keys())
        )

    with col3:
        project_load = st.number_input("Charge (jours)", 1.0, 100.0, 5.0)

    with col4:
        project_priority = st.number_input("Priorité", 1, 100, 1)

    if st.button("Ajouter le projet"):
        st.session_state.tasks.append({
            "Projet": project_name,
            "Équipe": project_team,
            "load": project_load,
            "priority": project_priority
        })
else:
    st.info("Ajoute d'abord des équipes pour créer des projets.")

st.header("Backlog actuel")

if st.session_state.tasks:
    df_backlog = pd.DataFrame(st.session_state.tasks).sort_values("priority")
    st.dataframe(df_backlog, use_container_width=True)
else:
    st.info("Aucun projet dans le backlog.")

# =============================
# BACKLOG
# =============================


# =============================
# PLANIFICATION AUTOMATIQUE
# =============================
planning = []
remaining_capacity = capacity.copy()

for task in sorted(st.session_state.tasks, key=lambda x: x["priority"]):
    for sprint in sprints:
        key = (task["Équipe"], sprint["name"])
        if remaining_capacity.get(key, 0) >= task["load"]:
            remaining_capacity[key] -= task["load"]
            planning.append({
                "Projet": task["Projet"],
                "Équipe": task["Équipe"],
                "Itération": sprint["name"],
                "ETA": sprint["end"]
            })
            break

# =============================
# AFFICHAGE PLANNING
# =============================
st.header("Planning PI (calculé automatiquement)")

if planning:
    st.dataframe(pd.DataFrame(planning), use_container_width=True)
else:
    st.warning("Impossible de planifier : capacités insuffisantes ou équipes manquantes.")

