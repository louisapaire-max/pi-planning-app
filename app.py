import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

st.set_page_config(page_title="PI Planning - Capacity Tool v5.6", layout="wide")
st.title("📊 PI Planning - Capacity Planning avec Dépendances & Sizing")

HOLIDAYS_2026 = [
    "2026-01-01", "2026-04-06", "2026-05-01", "2026-05-08", 
    "2026-05-14", "2026-05-25", "2026-07-14", "2026-08-15", 
    "2026-11-01", "2026-11-11", "2026-12-25"
]

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
    "Product Owner": "#FF6B6B", "Product unit": "#FF8C42", "QQE": "#FFC300",
    "Marketing": "#FF1493", "Design": "#9D4EDD", "Webmaster": "#3A86FF",
    "Dev Web Front": "#00D9FF", "Dev Web Back": "#0099FF", "Dev Order": "#2E7D32",
    "Tracking": "#FFB703", "SEO": "#FB5607", "QA": "#8E44AD", "Traduction": "#1ABC9C"
}

TASKS_DEFAULT = [
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
    {"name": "Email - Add File Edition to Zimbra Pro", "priority": 1},
    {"name": "Website Revamp - homepage telephony", "priority": 2},
    {"name": "VPS - Add more choice on Disk options", "priority": 3},
    {"name": "Zimbra add yearly commitment prod", "priority": 4},
    {"name": "Telco - Create new plans for Trunk product", "priority": 5},
    {"name": "Funnel order improvement - Pre-select OS & APP", "priority": 6},
    {"name": "[VPS 2026 RBX7] - Deploy RBX7 region for VPS 2026", "priority": 7},
    {"name": "lot 2 website page Phone & Headset", "priority": 8},
    {"name": "Website Revamp - numbers page", "priority": 9},
    {"name": "VOIP Offers - Update 40 Included Destinations", "priority": 10},
    {"name": "Email - Website Quick Wins - Zimbra Webmail", "priority": 11},
    {"name": "Email - Website Quick Wins - New Exchange Product pages", "priority": 12},
    {"name": "VPS - Website New pages (Resellers & Panels)", "priority": 13},
    {"name": "Email - Website Quick Wins", "priority": 14},
    {"name": "Revamp Telephony", "priority": 15},
]

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

if "tasks_config" not in st.session_state:
    st.session_state.tasks_config = {task["name"]: task.copy() for task in TASKS_DEFAULT}

if "projects_tasks" not in st.session_state:
    st.session_state.projects_tasks = {}
    for proj in PROJECTS:
        st.session_state.projects_tasks[proj["name"]] = [t["name"] for t in TASKS_DEFAULT]

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

# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_net_capacity(team: str, iteration: dict) -> float:
    key = (team, iteration["name"])
    brute = st.session_state.capacity.get(key, 0)
    leaves = st.session_state.leaves.get(key, 0)
    run = st.session_state.run_days.get(key, 0)
    return max(0, brute - leaves - run)

def get_tasks_list():
    return list(st.session_state.tasks_config.values())

def calculate_planning():
    """
    Calcul du planning respectant VRAIMENT le sizing (en jours) et les dépendances.
    """
    TASKS = get_tasks_list()
    planning = []
    task_dates = {}
    
    first_iter_start = pd.to_datetime(ITERATIONS[0]["start"])
    current_date = first_iter_start
    
    for project in sorted(PROJECTS, key=lambda x: x["priority"]):
        project_tasks = st.session_state.projects_tasks.get(project["name"], [])
        
        for task in sorted(TASKS, key=lambda t: t["order"]):
            if task["name"] not in project_tasks:
                continue
            
            start_date = current_date
            
            if task["depends_on"]:
                parent_key = f"{project['name']}_{task['depends_on']}"
                if parent_key in task_dates:
                    _, parent_end_date = task_dates[parent_key]
                    start_date = parent_end_date + timedelta(days=1)
                else:
                    planning.append({
                        "Priorité": project["priority"],
                        "Projet": project["name"],
                        "Tâche": task["name"],
                        "Équipe": task["team"],
                        "Début": None,
                        "Fin": None,
                        "Charge": task["charge"],
                        "Dépendance": task["depends_on"],
                        "Statut": "❌ Bloqué"
                    })
                    continue
            
            end_date = start_date + timedelta(days=task["charge"])
            
            task_key = f"{project['name']}_{task['name']}"
            task_dates[task_key] = (start_date, end_date)
            
            planning.append({
                "Priorité": project["priority"],
                "Projet": project["name"],
                "Tâche": task["name"],
                "Équipe": task["team"],
                "Début": start_date.strftime("%Y-%m-%d"),
                "Fin": end_date.strftime("%Y-%m-%d"),
                "Charge": task["charge"],
                "Dépendance": task["depends_on"],
                "Statut": "✅ Planifié"
            })
    
    return planning, task_dates

# Calcul planning
planning, task_dates = calculate_planning()
df_plan = pd.DataFrame(planning)

# ═══════════════════════════════════════════════════════════════════════════════
# KPIs
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("### 📊 Vue d'Ensemble - KPIs")
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    total_taches = len(df_plan)
    st.metric("📋 Total Tâches", total_taches)

with col_kpi2:
    planifiees = len(df_plan[df_plan["Statut"] == "✅ Planifié"])
    st.metric("✅ Planifiées", planifiees, f"{planifiees/total_taches*100:.0f}%" if total_taches > 0 else "0%")

with col_kpi3:
    bloquees = len(df_plan[df_plan["Statut"] == "❌ Bloqué"])
    st.metric("❌ Bloquées", bloquees, f"{bloquees/total_taches*100:.0f}%" if total_taches > 0 else "0%")

with col_kpi4:
    if not df_plan.empty and not df_plan[df_plan["Début"].notna()].empty:
        duree_total = (pd.to_datetime(df_plan[df_plan["Début"].notna()]["Fin"].max()) - 
                       pd.to_datetime(df_plan[df_plan["Début"].notna()]["Début"].min())).days
        st.metric("📅 Durée Totale", f"{duree_total} jours")
    else:
        st.metric("📅 Durée Totale", "N/A")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLETS
# ═══════════════════════════════════════════════════════════════════════════════

tab_config, tab_projects, tab_planning, tab_capa, tab_cong = st.tabs([
    "⚙️ Configuration Tâches",
    "🎯 Projets & Tâches",
    "📋 Planning & Gantt",
    "📊 Capacités",
    "🏖️ Congés & Run"
])

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 0: CONFIGURATION TÂCHES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_config:
    st.subheader("⚙️ Configuration des Tâches - Sizing & Dépendances")
    st.markdown("""
    Modifiez ici :
    - **Sizing (Charge)** : Nombre de jours requis pour la tâche
    - **Dépendances** : Tâche(s) requise(s) avant de commencer celle-ci
    
    💡 Si une tâche dépend d'une autre, elle commencera automatiquement après la date de fin de sa dépendance.
    """)
    
    config_data = []
    for task in sorted(get_tasks_list(), key=lambda t: t["order"]):
        config_data.append({
            "# Ordre": task["order"],
            "Tâche": task["name"],
            "Équipe": task["team"],
            "Charge (j)": task["charge"],
            "Dépend de": task["depends_on"] if task["depends_on"] else "(Aucune)"
        })
    
    df_config = pd.DataFrame(config_data)
    
    st.markdown("#### 📝 Éditer le Sizing (Charge)")
    edited_config = st.data_editor(
        df_config[["# Ordre", "Tâche", "Équipe", "Charge (j)"]],
        use_container_width=True,
        hide_index=True,
        key="tasks_config_editor",
        column_config={
            "# Ordre": st.column_config.NumberColumn(disabled=True),
            "Tâche": st.column_config.TextColumn(disabled=True, width="large"),
            "Équipe": st.column_config.TextColumn(disabled=True),
            "Charge (j)": st.column_config.NumberColumn("Charge (j)", min_value=0.5, max_value=20, step=0.5)
        }
    )
    
    for idx, row in edited_config.iterrows():
        task_name = row["Tâche"]
        if task_name in st.session_state.tasks_config:
            st.session_state.tasks_config[task_name]["charge"] = row["Charge (j)"]
    
    st.divider()
    
    st.markdown("#### 🔗 Éditer les Dépendances")
    
    all_task_names = [t["name"] for t in get_tasks_list()]
    
    for task in sorted(get_tasks_list(), key=lambda t: t["order"]):
        col1, col2 = st.columns([2, 2])
        
        with col1:
            st.markdown(f"**{task['name']}** ({task['team']})")
        
        with col2:
            options = ["(Aucune)"] + [t for t in all_task_names if t != task["name"]]
            current_dep = task["depends_on"] if task["depends_on"] else "(Aucune)"
            
            new_dep = st.selectbox(
                "Dépend de",
                options=options,
                index=options.index(current_dep),
                key=f"dep_{task['name']}",
                label_visibility="collapsed"
            )
            
            if new_dep == "(Aucune)":
                st.session_state.tasks_config[task["name"]]["depends_on"] = None
            else:
                st.session_state.tasks_config[task["name"]]["depends_on"] = new_dep
    
    if st.button("💾 Sauvegarder Configuration", key="save_config"):
        st.success("✅ Configuration mise à jour !")
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 1: PROJETS & TÂCHES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_projects:
    st.subheader("🎯 Gérer les Tâches par Projet")
    
    all_task_names = [t["name"] for t in get_tasks_list()]
    
    selected_proj = st.selectbox("Sélectionner un projet", options=[p["name"] for p in PROJECTS])
    
    if selected_proj:
        current_tasks = st.session_state.projects_tasks.get(selected_proj, [])
        
        st.markdown(f"#### Tâches du projet: **{selected_proj}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Tâches actuelles ✅**")
            for task_name in current_tasks:
                col_task, col_remove = st.columns([4, 1])
                with col_task:
                    st.text(task_name)
                with col_remove:
                    if st.button("❌", key=f"remove_{task_name}", help="Supprimer"):
                        st.session_state.projects_tasks[selected_proj].remove(task_name)
                        st.rerun()
        
        with col2:
            st.markdown("**Ajouter une tâche ➕**")
            available_tasks = [t for t in all_task_names if t not in current_tasks]
            
            if available_tasks:
                new_task = st.selectbox("Sélectionner une tâche à ajouter", options=available_tasks)
                if st.button("➕ Ajouter", key="add_task"):
                    st.session_state.projects_tasks[selected_proj].append(new_task)
                    st.rerun()
            else:
                st.info("Toutes les tâches sont déjà assignées à ce projet.")

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 2: PLANNING & GANTT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_planning:
    st.subheader("📋 Planning détaillé & Gantt")
    
    if not df_plan.empty:
        df_plan["Start Date"] = pd.to_datetime(df_plan["Début"], errors='coerce')
        df_plan["End Date"] = pd.to_datetime(df_plan["Fin"], errors='coerce')

    project_list = ["Vue Globale"] + sorted(list(df_plan["Projet"].unique())) if not df_plan.empty else []
    selected_project = st.selectbox("🎯 Sélectionner un projet", options=project_list, key="gantt_project")
    
    st.divider()

    if selected_project == "Vue Globale":
        st.info("📊 Vue globale de toutes les tâches")
        
        display_cols = ["Priorité", "Projet", "Tâche", "Équipe", "Début", "Fin", "Charge", "Dépendance", "Statut"]
        
        st.dataframe(
            df_plan[display_cols].sort_values("Priorité"),
            use_container_width=True,
            hide_index=True,
            height=600
        )

    else:
        df_filtered = df_plan[df_plan["Projet"] == selected_project].copy()
        
        if not df_filtered.empty:
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
                    title=f"Planning: {selected_project}",
                    height=max(400, len(df_gantt) * 45)
                )
                
                colors_bg = ["rgba(230, 230, 230, 0.3)", "rgba(200, 230, 255, 0.3)", "rgba(220, 255, 220, 0.3)"]
                for i, it in enumerate(ITERATIONS):
                    fig.add_vrect(
                        x0=it["start"], x1=it["end"],
                        fillcolor=colors_bg[i % len(colors_bg)], 
                        layer="below", line_width=0,
                        annotation_text=f"<b>{it['name']}</b>", 
                        annotation_position="top left",
                        annotation_font_size=13
                    )
                    fig.add_vline(x=it["end"], line_width=2, line_dash="dot", line_color="gray")
                
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

                first_iteration_start = ITERATIONS[0]["start"]
                last_iteration_end = ITERATIONS[-1]["end"]
                
                fig.update_xaxes(
                    range=[first_iteration_start, last_iteration_end],
                    tickformat="%a %d/%m",
                    dtick=86400000.0,
                    side="top",
                    tickfont=dict(size=11),
                    rangebreaks=[dict(bounds=["sat", "mon"])]
                )
                fig.update_yaxes(autorange="reversed")
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Aucune tâche avec dates valides.")

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 3: CAPACITÉS
# ═══════════════════════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 4: CONGÉS & RUN
# ═══════════════════════════════════════════════════════════════════════════════
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

st.divider()
st.markdown(f"🛠 **PI Planning Tool v5.6** (Sizing & Dependencies Fixed) | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
