import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from collections import defaultdict

# ═════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="PI Planning - Capacity Tool v6", layout="wide")
st.title("📊 PI Planning - Capacity Planning avec Dépendances")

# JOURS FÉRIÉS 2026
HOLIDAYS_2026 = [
    "2026-01-01", "2026-04-06", "2026-05-01", "2026-05-08", 
    "2026-05-14", "2026-05-25", "2026-07-14", "2026-08-15", 
    "2026-11-01", "2026-11-11", "2026-12-25"
]

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

TEAM_COLORS = {
    "Product Owner": "#FF6B6B",
    "Product unit": "#FF8C42",
    "QQE": "#FFC300",
    "Marketing": "#FF1493",
    "Design": "#9D4EDD",
    "Webmaster": "#3A86FF",
    "Dev Web Front": "#00D9FF",
    "Dev Web Back": "#0099FF",
    "Dev Order": "#2E7D32",
    "Tracking": "#FFB703",
    "SEO": "#FB5607",
    "QA": "#8E44AD",
    "Traduction": "#1ABC9C"
}

TASKS = [
    {"name": "Brief requester Delivery", "team": "Product Owner", "order": 1, "charge": 1, "depends_on": None},
    {"name": "Catalogue Delivery", "team": "Product unit", "order": 2, "charge": 2, "depends_on": "Brief requester Delivery"},
    {"name": "Control d'interface", "team": "QQE", "order": 3, "charge": 1, "depends_on": "Catalogue Delivery"},
    {"name": "Content", "team": "Marketing", "order": 4, "charge": 2, "depends_on": "Brief requester Delivery"},
    {"name": "Documentation Project", "team": "Product Owner", "order": 5, "charge": 1, "depends_on": "Brief requester Delivery"},
    {"name": "Kick-off Digital", "team": "Product Owner", "order": 6, "charge": 0.5, "depends_on": "Brief requester Delivery"},
    {"name": "Etude d'impact", "team": "Product Owner", "order": 7, "charge": 2, "depends_on": "Kick-off Digital"},
    {"name": "Maquettes/Wireframe", "team": "Design", "order": 8, "charge": 3, "depends_on": "Etude d'impact"},
    {"name": "Redaction US / Jira", "team": "Product Owner", "order": 9, "charge": 2, "depends_on": "Maquettes/Wireframe"},
    {"name": "Refinement", "team": "Product Owner", "order": 10, "charge": 1, "depends_on": "Redaction US / Jira"},
    {"name": "Integration OCMS", "team": "Webmaster", "order": 11, "charge": 2, "depends_on": "Content"},
    {"name": "Dev Website Front", "team": "Dev Web Front", "order": 12, "charge": 5, "depends_on": "Refinement"},
    {"name": "Dev Website Back", "team": "Dev Web Back", "order": 13, "charge": 5, "depends_on": "Refinement"},
    {"name": "Dev Order", "team": "Dev Order", "order": 14, "charge": 3, "depends_on": "Refinement"},
    {"name": "Tracking", "team": "Tracking", "order": 15, "charge": 2, "depends_on": "Dev Website Front"},
    {"name": "check SEO", "team": "SEO", "order": 16, "charge": 1, "depends_on": "Dev Website Front"},
    {"name": "QA & UAT (langue source)", "team": "QA", "order": 17, "charge": 3, "depends_on": "Dev Website Front"},
    {"name": "Traduction", "team": "Traduction", "order": 18, "charge": 2, "depends_on": "QA & UAT (langue source)"},
    {"name": "QA WW", "team": "QA", "order": 19, "charge": 2, "depends_on": "Traduction"},
    {"name": "Plan de Production", "team": "Product Owner", "order": 20, "charge": 1, "depends_on": "QA WW"},
    {"name": "PROD", "team": "Product Owner", "order": 21, "charge": 1, "depends_on": "Plan de Production"}
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
# SESSION STATE
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

if "show_blocked_details" not in st.session_state:
    st.session_state.show_blocked_details = False

# ═════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═════════════════════════════════════════════════════════════════════

def get_net_capacity(team: str, iteration: dict) -> float:
    key = (team, iteration["name"])
    brute = st.session_state.capacity.get(key, 0)
    leaves = st.session_state.leaves.get(key, 0)
    run = st.session_state.run_days.get(key, 0)
    return max(0, brute - leaves - run)

def get_task_key(row):
    prio = row.get('Priorité')
    proj = row.get('Projet')
    tache = row.get('Tâche')
    equipe = row.get('Équipe')
    return f"{prio}_{proj}_{tache}_{equipe}"

# 8️⃣ FONCTION: Déterminer status dépendance
def get_dependency_status(df_plan, task_name):
    """
    Retourne le statut de la dépendance:
    - "✅ Finie" si la dépendance est terminée
    - "🔴 Pas finie" si la dépendance n'est pas terminée
    - "➖ Aucune" si pas de dépendance
    """
    # Chercher la tâche
    tasks_with_name = df_plan[df_plan["Tâche"] == task_name]
    if tasks_with_name.empty:
        return "➖ Aucune"
    
    task = tasks_with_name.iloc[0]
    if pd.isna(task["Dépendance"]) or task["Dépendance"] is None:
        return "➖ Aucune"
    
    # Chercher la dépendance
    parent_tasks = df_plan[df_plan["Tâche"] == task["Dépendance"]]
    if parent_tasks.empty:
        return "⚠️ Dépendance inconnue"
    
    parent_status = parent_tasks.iloc[0]["Statut Custom"]
    if parent_status == "Terminé":
        return "✅ Finie"
    else:
        return f"🔴 En attente ({parent_status})"

@st.cache_data
def calculate_planning_cached():
    """Calcul du planning avec gestion des dépendances (CACHED)"""
    remaining = {}
    for team in TEAMS:
        for it in ITERATIONS:
            remaining[(team, it["name"])] = get_net_capacity(team, it)
    
    planning = []
    task_completion_index = {}

    for project in sorted(PROJECTS, key=lambda x: x["priority"]):
        for task in sorted(TASKS, key=lambda t: t["order"]):
            placed = False
            
            start_search_index = 0
            if task["depends_on"]:
                parent_key = f"{project['name']}_{task['depends_on']}"
                if parent_key in task_completion_index:
                    start_search_index = task_completion_index[parent_key]
                else:
                    start_search_index = 999 

            if start_search_index < len(ITERATIONS):
                for idx in range(start_search_index, len(ITERATIONS)):
                    it = ITERATIONS[idx]
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
                            "Dépendance": task["depends_on"],
                            "Statut": "✅ Planifié"
                        })
                        task_completion_index[f"{project['name']}_{task['name']}"] = idx
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
                    "Dépendance": task["depends_on"],
                    "Statut": "❌ Bloqué"
                })
    
    return planning, remaining

# ═════════════════════════════════════════════════════════════════════
# INTERFACE PRINCIPALE
# ═════════════════════════════════════════════════════════════════════

# Calcul planning
planning, remaining = calculate_planning_cached()
df_plan = pd.DataFrame(planning)

# KPIs Dashboard (Interactif)
st.markdown("### 📊 Vue d'Ensemble - KPIs")
col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)

with col_kpi1:
    total_taches = len(df_plan)
    st.metric("📋 Total Tâches", total_taches)

with col_kpi2:
    planifiees = len(df_plan[df_plan["Statut"] == "✅ Planifié"])
    st.metric("✅ Planifiées", planifiees, f"{planifiees/total_taches*100:.0f}%" if total_taches > 0 else "0%")

with col_kpi3:
    bloquees = len(df_plan[df_plan["Statut"] == "❌ Bloqué"])
    if st.button(f"❌ Bloquées\n{bloquees}", key="kpi_blocked", use_container_width=True):
        st.session_state.show_blocked_details = not st.session_state.show_blocked_details

with col_kpi4:
    capa_restante_moy = sum(remaining.values()) / len(remaining) if remaining else 0
    st.metric("📦 Capa Moy Restante", f"{capa_restante_moy:.1f}j")

with col_kpi5:
    taux_util = (1 - (capa_restante_moy / 10)) * 100 if capa_restante_moy >= 0 else 0
    st.metric("📈 Taux Utilisation", f"{min(100, taux_util):.0f}%")

# Afficher tâches bloquées si cliquées
if st.session_state.show_blocked_details:
    st.warning("### ❌ Tâches Bloquées Détaillées")
    blocked_tasks = df_plan[df_plan["Statut"] == "❌ Bloqué"]
    if not blocked_tasks.empty:
        st.dataframe(
            blocked_tasks[["Priorité", "Projet", "Tâche", "Équipe", "Dépendance"]],
            use_container_width=True,
            hide_index=True
        )

st.divider()

# 1️⃣ ONGLETS: 2 onglets distincts (Planning Gantt vs Édition Globale)
tab_planning_gantt, tab_planning_edit, tab_capa, tab_cong, tab_time, tab_active = st.tabs([
    "📋 Planning & Gantt",
    "✏️ Édition Globale",
    "📊 Capacités",
    "🏖️ Congés & Run",
    "📈 Timeline Globale",
    "✅ En cours"
])

# ─────────────────────────────────────────────────────────────────
# ONGLET 1: PLANNING & GANTT (avec Layout 2 colonnes)
# ─────────────────────────────────────────────────────────────────
with tab_planning_gantt:
    st.subheader("📋 Planning & Gantt par Projet")
    
    if not df_plan.empty:
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
        
        df_plan["Start Date"] = pd.to_datetime(df_plan["Start Date"], errors='coerce')
        df_plan["End Date"] = pd.to_datetime(df_plan["End Date"], errors='coerce')

    # 🔟 SEARCH/FILTER dans selectbox
    project_list = sorted(list(df_plan["Projet"].unique())) if not df_plan.empty else []
    selected_project = st.selectbox(
        "🎯 Sélectionner un projet",
        options=project_list,
        placeholder="Chercher un projet..."
    )
    
    st.divider()

    if selected_project:
        df_filtered = df_plan[df_plan["Projet"] == selected_project].copy()
        
        if not df_filtered.empty:
            # 2️⃣ LAYOUT 2 COLONNES: Gantt + Quick Override
            col_gantt, col_override = st.columns([0.6, 0.4])
            
            with col_gantt:
                st.subheader(f"📅 Gantt: {selected_project}")
                
                df_gantt = df_filtered.dropna(subset=["Start Date", "End Date"]).copy()
                
                if not df_gantt.empty:
                    fig = px.timeline(
                        df_gantt, 
                        x_start="Start Date", 
                        x_end="End Date", 
                        y="Tâche",
                        color="Équipe",
                        color_discrete_map=TEAM_COLORS,
                        hover_data=["Équipe", "Charge", "Dépendance"],
                        title=f"Planning",
                        height=max(400, len(df_gantt) * 45)
                    )
                    
                    # Itérations avec styling amélioré (bordures épaisses)
                    colors_bg = [
                        "rgba(100, 150, 200, 0.15)",
                        "rgba(100, 200, 100, 0.15)",
                        "rgba(200, 150, 100, 0.15)"
                    ]
                    
                    for i, it in enumerate(ITERATIONS):
                        fig.add_vrect(
                            x0=it["start"], x1=it["end"],
                            fillcolor=colors_bg[i % len(colors_bg)],
                            line=dict(color=colors_bg[i].replace("0.15", "0.8"), width=3),
                            layer="below",
                            annotation_text=f"<b>{it['name'].upper()}</b>",
                            annotation_position="top left",
                            annotation_font_size=14,
                            annotation_font_color="rgba(0,0,0,0.7)"
                        )
                        fig.add_vline(x=it["end"], line_width=2, line_dash="dot", line_color="gray")
                    
                    # Jours fériés
                    for hol_date in HOLIDAYS_2026:
                        start_hol = pd.to_datetime(hol_date)
                        end_hol = start_hol + timedelta(days=1)
                        fig.add_vrect(
                            x0=start_hol, x1=end_hol,
                            fillcolor="rgba(255, 0, 0, 0.2)",
                            line_width=0,
                            annotation_text="Férié",
                            annotation_position="bottom right",
                            annotation_font_color="red",
                            annotation_font_size=10
                        )

                    fig.update_xaxes(
                        tickformat="%a %d/%m",
                        dtick=86400000.0,
                        side="top",
                        tickfont=dict(size=11),
                        rangebreaks=[dict(bounds=["sat", "mon"])]
                    )
                    fig.update_yaxes(autorange="reversed")
                    
                    st.plotly_chart(fig, use_container_width=True, key=f"gantt_{selected_project}")
                else:
                    st.warning("⚠️ Aucune tâche avec dates valides.")
            
            # 2️⃣ COLONNE 2: Quick Override (Panel latéral)
            with col_override:
                st.subheader("⚡ Quick Override")
                st.markdown("Modifier une tâche rapidement")
                
                task_to_edit = st.selectbox(
                    "Tâche",
                    options=df_filtered["Tâche"].unique(),
                    key=f"task_select_{selected_project}"
                )
                
                if task_to_edit:
                    task_row = df_filtered[df_filtered["Tâche"] == task_to_edit].iloc[0]
                    
                    new_start = st.date_input(
                        "Début",
                        value=task_row["Start Date"] if pd.notna(task_row["Start Date"]) else date.today(),
                        key=f"start_{task_to_edit}"
                    )
                    
                    new_end = st.date_input(
                        "Fin",
                        value=task_row["End Date"] if pd.notna(task_row["End Date"]) else date.today() + timedelta(days=1),
                        key=f"end_{task_to_edit}"
                    )
                    
                    new_status = st.selectbox(
                        "Statut",
                        options=TASK_STATUSES,
                        index=TASK_STATUSES.index(task_row["Statut Custom"]) if task_row["Statut Custom"] in TASK_STATUSES else 0,
                        key=f"status_{task_to_edit}"
                    )
                    
                    # 8️⃣ AFFICHER STATUS DÉPENDANCE
                    dep_status = get_dependency_status(df_plan, task_to_edit)
                    st.markdown(f"**Dépendance:** {dep_status}")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✅ Appliquer", key=f"apply_{task_to_edit}", use_container_width=True):
                            original_row = df_filtered[df_filtered["Tâche"] == task_to_edit].iloc[0]
                            full_row = {
                                "Priorité": original_row["Priorité"],
                                "Projet": selected_project,
                                "Tâche": task_to_edit,
                                "Équipe": original_row["Équipe"]
                            }
                            task_key = get_task_key(full_row)
                            
                            st.session_state.task_details[task_key] = {
                                "start_date": new_start,
                                "end_date": new_end,
                                "status": new_status
                            }
                            st.toast(f"✅ {task_to_edit} mis à jour!", icon="✅")
                    
                    with col_btn2:
                        if st.button("🔄 Reset", key=f"reset_{task_to_edit}", use_container_width=True):
                            full_row = {
                                "Priorité": task_row["Priorité"],
                                "Projet": selected_project,
                                "Tâche": task_to_edit,
                                "Équipe": task_row["Équipe"]
                            }
                            task_key = get_task_key(full_row)
                            if task_key in st.session_state.task_details:
                                del st.session_state.task_details[task_key]
                            st.toast("🔄 Réinitialisé!", icon="✅")

# ─────────────────────────────────────────────────────────────────
# ONGLET 2: ÉDITION GLOBALE
# ─────────────────────────────────────────────────────────────────
with tab_planning_edit:
    st.info("💡 Mode édition globale - Modifiez tous les projets en une seule vue")
    
    display_cols = ["Priorité", "Projet", "Tâche", "Équipe", "Itération", "Statut"]
    
    st.dataframe(
        df_plan[display_cols].sort_values("Priorité"),
        use_container_width=True,
        hide_index=True,
        height=600
    )

# ─────────────────────────────────────────────────────────────────
# ONGLET 3: CAPACITÉS
# ─────────────────────────────────────────────────────────────────
with tab_capa:
    st.subheader("📊 Capacités Brutes (Jours)")
    
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
    st.metric("📦 Capacité totale", f"{edited_cap.sum().sum():.1f} jours")

# ─────────────────────────────────────────────────────────────────
# ONGLET 4: CONGÉS & RUN
# ─────────────────────────────────────────────────────────────────
with tab_cong:
    st.subheader("🏖️ Congés & Support")
    
    col_leave, col_run = st.columns(2)
    
    with col_leave:
        st.markdown("#### 🏖️ Congés (jours)")
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
        st.markdown("#### 🛠️ Run & Support (jours)")
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

# ─────────────────────────────────────────────────────────────────
# ONGLET 5: TIMELINE GLOBALE (Cliquable)
# ─────────────────────────────────────────────────────────────────
with tab_time:
    st.subheader("📈 Vue par Itération (Cliquable)")
    
    df_gantt_global = df_plan[df_plan["Statut"] == "✅ Planifié"]
    
    if not df_gantt_global.empty:
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        
        for idx, it in enumerate(ITERATIONS):
            with cols[idx % 3]:
                st.markdown(f"#### {it['name']}")
                tasks_it = df_gantt_global[df_gantt_global["Itération"] == it["name"]]
                
                if not tasks_it.empty:
                    load_per_project = tasks_it.groupby("Projet")["Charge"].sum().reset_index()
                    
                    # Créer chart interactif cliquable
                    fig_it = px.bar(
                        load_per_project,
                        x="Charge",
                        y="Projet",
                        orientation="h",
                        title=f"{it['name']}",
                        color="Charge",
                        color_continuous_scale="Blues",
                        height=400
                    )
                    
                    fig_it.update_yaxes(autorange="reversed")
                    st.plotly_chart(fig_it, use_container_width=True, key=f"iter_{it['name']}")
                else:
                    st.caption("Aucune tâche.")
    else:
        st.info("Aucune tâche planifiée.")

# ─────────────────────────────────────────────────────────────────
# ONGLET 6: EN COURS
# ─────────────────────────────────────────────────────────────────
with tab_active:
    st.subheader("✅ Suivi Opérationnel")
    
    if not df_plan.empty:
        today = pd.Timestamp.now().normalize()
        active = df_plan[
            (df_plan["Start Date"] <= today) & 
            (df_plan["End Date"] >= today)
        ].copy()
        
        col_metric1, col_metric2 = st.columns(2)
        col_metric1.metric("Date du jour", today.strftime("%d/%m/%Y"))
        col_metric2.metric("Tâches actives", len(active))
        
        if not active.empty:
            st.dataframe(
                active[["Projet", "Tâche", "Équipe", "Charge"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Aucune tâche active aujourd'hui.")

# ═════════════════════════════════════════════════════════════════════
# ANIMATIONS & SCROLL SMOOTH (CSS)
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
/* Smooth scroll */
html {
    scroll-behavior: smooth;
}

/* Animation de transition entre onglets */
[data-testid="stTabs"] {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Hover effect sur les boutons */
button {
    transition: all 0.2s ease;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Smooth input focus */
input, select {
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
</style>
""", unsafe_allow_html=True)

st.divider()
st.markdown(f"🛠 **PI Planning Tool v6.0** ✨ Enhanced UX | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
