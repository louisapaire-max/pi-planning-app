import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from workalendar.europe import France

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
if "capacity" not in st.session_state:
    st.session_state.capacity = {}
    for team in TEAMS:
        for it in ITERATIONS:
            st.session_state.capacity[(team, it["name"])] = 10.0

if "leaves" not in st.session_state:
    st.session_state.leaves = {}
    for team in TEAMS:
        for it in ITERATIONS:
            st.session_state.leaves[(team, it["name"])] = 0.0

if "run_days" not in st.session_state:
    st.session_state.run_days = {}
    for team in TEAMS:
        for it in ITERATIONS:
            st.session_state.run_days[(team, it["name"])] = 0.0

if "task_details" not in st.session_state:
    st.session_state.task_details = {}

# ═════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═════════════════════════════════════════════════════════════════════

def get_net_capacity(team: str, iteration: dict) -> float:
    """Capacité nette = brute - congés - run days"""
    key = (team, iteration["name"])
    brute = st.session_state.capacity.get(key, 0)
    leaves = st.session_state.leaves.get(key, 0)
    run = st.session_state.run_days.get(key, 0)
    return max(0, brute - leaves - run)

def get_task_key(row):
    """Génère une clé unique pour une tâche"""
    prio = row.get('Priorité')
    proj = row.get('Projet')
    tache = row.get('Tâche')
    equipe = row.get('Équipe')
    return f"{prio}_{proj}_{tache}_{equipe}"

def calculate_planning():
    """Calcule l'ETA pour toutes les tâches"""
    remaining = {}
    for team in TEAMS:
        for it in ITERATIONS:
            remaining[(team, it["name"])] = get_net_capacity(team, it)
    
    planning = []
    
    for project in sorted(PROJECTS, key=lambda x: x["priority"]):
        for task in sorted(TASKS, key=lambda t: t["order"]):
            placed = False
            
            for it in ITERATIONS:
                key = (task["team"], it["name"])
                if (remaining.get(key, 0) >= task["charge"]):
                    remaining[key] -= task["charge"]
                    planning.append({
                        "Priorité": project["priority"],
                        "Projet": project["name"],
                        "Tâche": task["name"],
                        "Équipe": task["team"],
                        "Itération": it["name"],
                        "Début": it["start"],
                        "Fin": it["end"],
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
# ONGLETS PRINCIPAUX
# ═════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Capacités",
    "🏖️ Congés & Run",
    "📋 Planning & ETA",
    "📈 Timeline Globale",
    "✅ En cours"
])

# ═════════════════════════════════════════════════════════════════════
# TAB 1: CAPACITÉS
# ═════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("📊 Capacité brute par équipe")
    
    capacity_data = {}
    for team in TEAMS:
        capacity_data[team] = []
        for it in ITERATIONS:
            key = (team, it["name"])
            capacity_data[team].append(st.session_state.capacity[key])
    
    df_cap = pd.DataFrame(capacity_data, index=[it["name"] for it in ITERATIONS]).T
    
    edited_cap = st.data_editor(
        df_cap,
        use_container_width=True,
        key="capacity_editor",
        column_config={
            it["name"]: st.column_config.NumberColumn(
                it["name"], min_value=0, max_value=100, step=0.5, format="%.1f j"
            ) for it in ITERATIONS
        }
    )
    
    for idx, team in enumerate(TEAMS):
        for jdx, it in enumerate(ITERATIONS):
            key = (team, it["name"])
            st.session_state.capacity[key] = edited_cap.iloc[idx, jdx]
    
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    total_cap = edited_cap.sum().sum()
    with col1: st.metric("📦 Capacité totale", f"{total_cap:.0f}j")

# ═════════════════════════════════════════════════════════════════════
# TAB 2: CONGÉS & RUN DAYS
# ═════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🏖️ Congés et Run Days")
    col_leave, col_run = st.columns(2)
    
    with col_leave:
        st.markdown("#### Congés (jours)")
        leave_data = {}
        for team in TEAMS:
            leave_data[team] = []
            for it in ITERATIONS:
                key = (team, it["name"])
                leave_data[team].append(st.session_state.leaves[key])
        
        df_leave = pd.DataFrame(leave_data, index=[it["name"] for it in ITERATIONS]).T
        edited_leave = st.data_editor(df_leave, use_container_width=True, key="leaves_editor")
        
        for idx, team in enumerate(TEAMS):
            for jdx, it in enumerate(ITERATIONS):
                st.session_state.leaves[(team, it["name"])] = edited_leave.iloc[idx, jdx]
    
    with col_run:
        st.markdown("#### Run Days (jours)")
        run_data = {}
        for team in TEAMS:
            run_data[team] = []
            for it in ITERATIONS:
                key = (team, it["name"])
                run_data[team].append(st.session_state.run_days[key])
        
        df_run = pd.DataFrame(run_data, index=[it["name"] for it in ITERATIONS]).T
        edited_run = st.data_editor(df_run, use_container_width=True, key="run_days_editor")
        
        for idx, team in enumerate(TEAMS):
            for jdx, it in enumerate(ITERATIONS):
                st.session_state.run_days[(team, it["name"])] = edited_run.iloc[idx, jdx]

# ═════════════════════════════════════════════════════════════════════
# TAB 3: PLANNING & ETA (CORRIGÉ)
# ═════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📋 Planning détaillé & Gantt par Projet")
    
    # 1. Calculer le planning de base
    planning, remaining = calculate_planning()
    df_plan = pd.DataFrame(planning)
    
    if not df_plan.empty:
        # 2. Appliquer les overrides
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
        
        # 🚨 CORRECTION CRITIQUE : CONVERSION DE TYPE OBLIGATOIRE POUR DATA_EDITOR
        # Convertit les strings et None en objets datetime uniformes
        df_plan["Start Date"] = pd.to_datetime(df_plan["Start Date"], errors='coerce')
        df_plan["End Date"] = pd.to_datetime(df_plan["End Date"], errors='coerce')

    # 3. Sélecteur de projet
    project_list = ["Vue Globale (Édition)"] + sorted(list(df_plan["Projet"].unique())) if not df_plan.empty else []
    selected_project = st.selectbox("🎯 Sélectionner un projet", options=project_list)
    
    st.divider()

    if selected_project == "Vue Globale (Édition)":
        # --- MODE GLOBAL ---
        st.info("💡 Mode édition globale : modifiez les dates et statuts ici.")
        
        display_cols = ["Priorité", "Projet", "Tâche", "Équipe", "Itération", "Charge", "Start Date", "End Date", "Statut Custom"]
        
        edited_df = st.data_editor(
            df_plan[display_cols].sort_values("Priorité"),
            use_container_width=True,
            hide_index=True,
            height=500,
            key="planning_editor_global",
            column_config={
                "Start Date": st.column_config.DateColumn("Start Date", format="DD/MM/YYYY", width="medium"),
                "End Date": st.column_config.DateColumn("End Date", format="DD/MM/YYYY", width="medium"),
                "Statut Custom": st.column_config.SelectboxColumn("Statut", options=TASK_STATUSES, width="medium"),
                "Priorité": st.column_config.NumberColumn(disabled=True),
                "Projet": st.column_config.TextColumn(disabled=True, width="large"),
                "Tâche": st.column_config.TextColumn(disabled=True, width="large"),
                "Équipe": st.column_config.TextColumn(disabled=True),
                "Itération": st.column_config.TextColumn(disabled=True),
                "Charge": st.column_config.NumberColumn(disabled=True),
            }
        )
        
        # Sauvegarde
        for idx, row in edited_df.iterrows():
            task_key = get_task_key(row)
            st.session_state.task_details[task_key] = {
                "start_date": row["Start Date"],
                "end_date": row["End Date"],
                "status": row["Statut Custom"]
            }

    else:
        # --- MODE PROJET SPÉCIFIQUE ---
        df_filtered = df_plan[df_plan["Projet"] == selected_project].copy()
        
        if not df_filtered.empty:
            st.subheader(f"📅 Gantt Chart: {selected_project}")
            
            # Pour le Gantt, on filtre les lignes avec des dates valides
            df_gantt = df_filtered.dropna(subset=["Start Date", "End Date"]).copy()
            
            if not df_gantt.empty:
                fig = px.timeline(
                    df_gantt, 
                    x_start="Start Date", 
                    x_end="End Date", 
                    y="Tâche",
                    color="Statut Custom",
                    hover_data=["Équipe", "Charge"],
                    title=f"Planning: {selected_project}",
                    height=300 + (len(df_gantt) * 20)
                )
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Aucune tâche avec des dates valides pour afficher le Gantt.")

            st.subheader("📝 Détail des tâches")
            cols_show = ["Tâche", "Start Date", "End Date", "Équipe", "Charge", "Statut Custom"]
            
            edited_project_df = st.data_editor(
                df_filtered[cols_show].sort_values("Start Date", na_position='last'),
                use_container_width=True,
                hide_index=True,
                key=f"editor_{selected_project}",
                column_config={
                    "Start Date": st.column_config.DateColumn("Début", format="DD/MM/YYYY"),
                    "End Date": st.column_config.DateColumn("Fin", format="DD/MM/YYYY"),
                    "Charge": st.column_config.NumberColumn("Capa (j)", format="%.1f"),
                    "Statut Custom": st.column_config.SelectboxColumn("Statut", options=TASK_STATUSES),
                    "Tâche": st.column_config.TextColumn(disabled=True),
                    "Équipe": st.column_config.TextColumn(disabled=True),
                }
            )
            
            for idx, row in edited_project_df.iterrows():
                original_row = df_filtered.loc[df_filtered["Tâche"] == row["Tâche"]].iloc[0]
                full_row_data = {
                    "Priorité": original_row["Priorité"],
                    "Projet": selected_project,
                    "Tâche": row["Tâche"],
                    "Équipe": row["Équipe"]
                }
                task_key = get_task_key(full_row_data)
                st.session_state.task_details[task_key] = {
                    "start_date": row["Start Date"],
                    "end_date": row["End Date"],
                    "status": row["Statut Custom"]
                }

# ═════════════════════════════════════════════════════════════════════
# TAB 4 & 5 (Simplifiés pour tenir dans la réponse, inchangés fonctionnellement)
# ═════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📈 Timeline Globale")
    df_gantt_global = df_plan[df_plan["Statut"] == "✅ Planifié"]
    if not df_gantt_global.empty:
        for it in ITERATIONS:
            st.markdown(f"#### {it['name']}")
            tasks_it = df_gantt_global[df_gantt_global["Itération"] == it["name"]]
            if not tasks_it.empty:
                st.dataframe(tasks_it[["Équipe", "Projet", "Tâche", "Charge"]], use_container_width=True, hide_index=True)

with tab5:
    st.subheader("✅ Suivi des tâches actives")
    if not df_plan.empty:
        today = pd.Timestamp.now().normalize()
        active = df_plan[(df_plan["Start Date"] <= today) & (df_plan["End Date"] >= today)]
        if not active.empty:
            st.metric("⏳ Tâches actives", len(active))
            st.dataframe(active[["Projet", "Tâche", "Équipe", "Start Date"]], use_container_width=True)
        else:
            st.info("Aucune tâche active aujourd'hui")
