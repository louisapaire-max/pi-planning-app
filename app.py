import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="PI Planning", layout="wide")
st.title("PI Planning")

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
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Équipe": "Product unit", "Charge": 6, "Priorité": 1},
    {"Projet": "Website Revamp - homepage telephony", "Équipe": "Dev Web Front", "Charge": 8, "Priorité": 2},
    {"Projet": "VPS - Add more choice on Disk options", "Équipe": "Dev Web Back", "Charge": 5, "Priorité": 3},
    {"Projet": "Zimbra add yearly commitment prod", "Équipe": "Product unit", "Charge": 4, "Priorité": 4},
    {"Projet": "Telco - Create new plans for Trunk product", "Équipe": "Dev Order", "Charge": 7, "Priorité": 5},
    {"Projet": "Funnel order improvement - Pre-select OS APP", "Équipe": "Dev Web Front", "Charge": 6, "Priorité": 6},
]

# =========================
# SESSION STATE – CAPACITÉS
# =========================
if "capacity" not in st.session_state:
    st.session_state.capacity = {}
    for team in default_teams:
        for it in iterations:
            st.session_state.capacity[(team, it["name"])] = 0.0

# =========================
# ONGLETS
# =========================
tab1, tab2 = st.tabs(["Capacités équipes", "Gantt PI Planning"])

# =========================================================
# ONGLET 1 – CAPACITÉS
# =========================================================
with tab1:
    st.subheader("Capacité par équipe et par itération")

    rows = []
    for team in default_teams:
        row = {"Équipe": team}
        for it in iterations:
            key = (team, it["name"])
            row[it["name"]] = st.number_input(
                f"{team} – {it['name']}",
                min_value=0.0,
                step=0.5,
                value=st.session_state.capacity[key],
                key=f"{team}_{it['name']}"
            )
            st.session_state.capacity[key] = row[it["name"]]
        rows.append(row)

    st.divider()
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

# =========================================================
# ONGLET 2 – GANTT
# =========================================================
with tab2:
    st.subheader("Gantt PI Planning")

    planning = []
    remaining_capacity = st.session_state.capacity.copy()

    for p in sorted(projects, key=lambda x: x["Priorité"]):
        for it in iterations:
            key = (p["Équipe"], it["name"])
            if remaining_capacity.get(key, 0) >= p["Charge"]:
                remaining_capacity[key] -= p["Charge"]
                planning.append({
                    "Projet": p["Projet"],
                    "Équipe": p["Équipe"],
                    "Début": it["start"],
                    "Fin": it["end"],
                    "Itération": it["name"]
                })
                break

    if planning:
        df_gantt = pd.DataFrame(planning)
        fig = px.timeline(
            df_gantt,
            x_start="Début",
            x_end="Fin",
            y="Équipe",
            color="Projet",
            hover_data=["Itération"]
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucun projet planifié. Vérifie les capacités.")
