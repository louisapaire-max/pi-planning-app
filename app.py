import pandas as pd
import streamlit as st

# ===== SPRINTS / ITÉRATIONS =====
sprints = [
    {"name": "Itération #1", "start": "2025-12-22", "end": "2026-01-09"},
    {"name": "Itération #2", "start": "2026-01-12", "end": "2026-01-30"},
    {"name": "Itération #3", "start": "2026-02-02", "end": "2026-02-20"},
    {"name": "Itération #4", "start": "2025-02-23", "end": "2026-03-13"},
    {"name": "Itération #5", "start": "2026-03-16", "end": "2026-03-20"},
]

# ===== CAPACITÉS PAR ÉQUIPE / ITÉRATION =====
capacity = {
    # Itération #1
    ("Dev Web Back", "Itération #1"): 7.3,
    ("Dev Web Front", "Itération #1"): 9,
    ("InT", "Itération #1"): 15.5,
    ("Order React", "Itération #1"): 7.6,
    ("Order Angular", "Itération #1"): 1.8,
    ("QA", "Itération #1"): 3.7,
    # Itération #2
    ("Dev Web Back", "Itération #2"): 7.3,
    ("Dev Web Front", "Itération #2"): 9,
    ("InT", "Itération #2"): 15.5,
    ("Order React", "Itération #2"): 7.6,
    ("Order Angular", "Itération #2"): 1.8,
    ("QA", "Itération #2"): 3.7,
    # Itération #3
    ("Dev Web Back", "Itération #3"): 7.3,
    ("Dev Web Front", "Itération #3"): 9,
    ("InT", "Itération #3"): 15.5,
    ("Order React", "Itération #3"): 7.6,
    ("Order Angular", "Itération #3"): 1.8,
    ("QA", "Itération #3"): 3.7,
    # Itération #4
    ("Dev Web Back", "Itération #4"): 7.3,
    ("Dev Web Front", "Itération #4"): 9,
    ("InT", "Itération #4"): 15.5,
    ("Order React", "Itération #4"): 7.6,
    ("Order Angular", "Itération #4"): 1.8,
    ("QA", "Itération #4"): 3.7,
    # Itération #5
    ("Dev Web Back", "Itération #5"): 2.4,
    ("Dev Web Front", "Itération #5"): 3,
    ("InT", "Itération #5"): 5.1,
    ("Order React", "Itération #5"): 2.5,
    ("Order Angular", "Itération #5"): 0.6,
    ("QA", "Itération #5"): 1.2,
}

# ===== BACKLOG =====
tasks = [
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Équipe": "InT", "load": 6, "priority": 1},
    {"Projet": "Website Revamp - homepage telephony", "Équipe": "Dev Web Front", "load": 8, "priority": 2},
    {"Projet": "VPS - Add more choice on Disk options", "Équipe": "Dev Web Back", "load": 5, "priority": 3},
    {"Projet": "Zimbra add yearly commitment prod", "Équipe": "InT", "load": 4, "priority": 4},
    {"Projet": "Telco - Create new plans for Trunk product", "Équipe": "Order React", "load": 7, "priority": 5},
    {"Projet": "Funnel order improvement - Pre-select OS APP", "Équipe": "Dev Web Front", "load": 6, "priority": 6},
    {"Projet": "VPS 2026 RBX7 - Deploy RBX7 region", "Équipe": "Dev Web Back", "load": 12, "priority": 7},
    {"Projet": "lot 2 website page Phone Headset", "Équipe": "Order Angular", "load": 5, "priority": 8},
    {"Projet": "Website Revamp - numbers page", "Équipe": "InT", "load": 6, "priority": 9},
    {"Projet": "VOIP Offers - Update 40 Included Destinations", "Équipe": "Marketing", "load": 4, "priority": 10},
    {"Projet": "Email - Website Quick Wins - Zimbra Webmail", "Équipe": "Product Owner", "load": 3, "priority": 11},
    {"Projet": "Email - Website Quick Wins - New Exchange", "Équipe": "Product Owner", "load": 3, "priority": 12},
    {"Projet": "VPS - Website New pages Resellers Panels", "Équipe": "Dev Web Back", "load": 6, "priority": 13},
    {"Projet": "Email - Website Quick Wins", "Équipe": "InT", "load": 2, "priority": 14},
]

# ===== PLANIFICATION AUTOMATIQUE =====
planning = []
for task in tasks:
    # Cherche la première itération avec assez de capacité
    for sprint in sprints:
        key = (task["Équipe"], sprint["name"])
        if capacity.get(key, 0) >= task["load"]:
            capacity[key] -= task["load"]
            planning.append({
                "Projet": task["Projet"],
                "Équipe": task["Équipe"],
                "Itération": sprint["name"],
                "ETA": sprint["end"]
            })
            break

# ===== AFFICHAGE STREAMLIT =====
st.title("PI Planning – Planning par itération")
df_tasks = pd.DataFrame(planning)
st.dataframe(df_tasks, use_container_width=True)
