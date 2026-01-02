import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

st.set_page_config(page_title="PI Planning - Capacity Tool v6.4", layout="wide")
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
        st.session_state.projects_tasks[proj["name"]] = {
            "default": [t["name"] for t in TASKS_DEFAULT],
            "custom": []
        }

if "custom_tasks" not in st.session_state:
    st.session_state.custom_tasks = {}

if "project_task_overrides" not in st.session_state:
    st.session_state.project_task_overrides = {}

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

def get_tasks_list():
    return list(st.session_state.tasks_config.values())

def get_all_tasks_for_project(project_name):
    """Récupère TOUS les noms de tâches (default + custom) pour un projet"""
    default_tasks = st.session_state.projects_tasks.get(project_name, {}).get("default", [])
    custom_tasks = st.session_state.projects_tasks.get(project_name, {}).get("custom", [])
    return default_tasks + custom_tasks

def get_task_charge_for_project(project_name, task_name):
    """Récupère la charge d'une tâche pour un projet (override ou default)"""
    override_key = f"{project_name}_{task_name}"
    if override_key in st.session_state.project_task_overrides:
        return st.session_state.project_task_overrides[override_key].get("charge", st.session_state.tasks_config.get(task_name, {}).get("charge", 1))
    return st.session_state.tasks_config.get(task_name, {}).get("charge", 1)

def get_task_depends_for_project(project_name, task_name):
    """Récupère la dépendance d'une tâche pour un projet (override ou default)"""
    override_key = f"{project_name}_{task_name}"
    if override_key in st.session_state.project_task_overrides:
        return st.session_state.project_task_overrides[override_key].get("depends_on", st.session_state.tasks_config.get(task_name, {}).get("depends_on"))
    return st.session_state.tasks_config.get(task_name, {}).get("depends_on")

def get_task_manual_dates(project_name, task_name):
    """Récupère les dates manuelles si elles existent"""
    override_key = f"{project_name}_{task_name}"
    if override_key in st.session_state.project_task_overrides:
        start_date = st.session_state.project_task_overrides[override_key].get("start_date")
        end_date = st.session_state.project_task_overrides[override_key].get("end_date")
        return start_date, end_date
    return None, None

def calculate_dates_for_project(project_name):
    """Calcule les dates de début et fin pour chaque tâche d'un projet"""
    TASKS = get_tasks_list()
    project_task_names = get_all_tasks_for_project(project_name)
    
    task_dates = {}
    first_iter_start = pd.to_datetime(ITERATIONS[0]["start"])
    
    for task in sorted(TASKS, key=lambda t: t["order"]):
        if task["name"] not in project_task_names:
            continue
        
        # Vérifier si des dates manuelles existent
        manual_start, manual_end = get_task_manual_dates(project_name, task["name"])
        
        if manual_start and manual_end:
            # Utiliser les dates manuelles
            start_date = pd.to_datetime(manual_start)
            end_date = pd.to_datetime(manual_end)
        else:
            # Calculer automatiquement
            start_date = first_iter_start
            
            task_charge = get_task_charge_for_project(project_name, task["name"])
            task_depends = get_task_depends_for_project(project_name, task["name"])
            
            if task_depends:
                if task_depends in task_dates:
                    _, parent_end_date = task_dates[task_depends]
                    start_date = parent_end_date + timedelta(days=1)
                else:
                    start_date = first_iter_start
            
            end_date = start_date + timedelta(days=task_charge)
        
        task_dates[task["name"]] = (start_date, end_date)
    
    # Ajouter les tâches custom
    for custom_task_name in st.session_state.projects_tasks.get(project_name, {}).get("custom", []):
        if custom_task_name in st.session_state.custom_tasks:
            custom_task = st.session_state.custom_tasks[custom_task_name]
            
            manual_start, manual_end = get_task_manual_dates(project_name, custom_task_name)
            
            if manual_start and manual_end:
                start_date = pd.to_datetime(manual_start)
                end_date = pd.to_datetime(manual_end)
            else:
                start_date = pd.to_datetime(custom_task.get("start_date", ITERATIONS[0]["start"]))
                end_date = start_date + timedelta(days=custom_task.get("charge", 1))
            
            task_dates[custom_task_name] = (start_date, end_date)
    
    return task_dates

def calculate_planning():
    """Calcul du planning global"""
    TASKS = get_tasks_list()
    planning = []
    task_dates = {}
    
    first_iter_start = pd.to_datetime(ITERATIONS[0]["start"])
    
    for project in sorted(PROJECTS, key=lambda x: x["priority"]):
        default_tasks = st.session_state.projects_tasks.get(project["name"], {}).get("default", [])
        custom_tasks = st.session_state.projects_tasks.get(project["name"], {}).get("custom", [])
        project_task_names = default_tasks + custom_tasks
        
        for task in sorted(TASKS, key=lambda t: t["order"]):
            if task["name"] not in project_task_names:
                continue
            
            start_date = first_iter_start
            
            task_charge = get_task_charge_for_project(project["name"], task["name"])
            task_depends = get_task_depends_for_project(project["name"], task["name"])
            
            # Vérifier dates manuelles
            manual_start, manual_end = get_task_manual_dates(project["name"], task["name"])
            
            if manual_start and manual_end:
                start_date = pd.to_datetime(manual_start)
                end_date = pd.to_datetime(manual_end)
            else:
                if task_depends:
                    parent_key = f"{project['name']}_{task_depends}"
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
                            "Charge": task_charge,
                            "Dépendance": task_depends,
                            "Statut": "❌ Bloqué"
                        })
                        continue
                
                end_date = start_date + timedelta(days=task_charge)
            
            task_key = f"{project['name']}_{task['name']}"
            task_dates[task_key] = (start_date, end_date)
            
            planning.append({
                "Priorité": project["priority"],
                "Projet": project["name"],
                "Tâche": task["name"],
                "Équipe": task["team"],
                "Début": start_date.strftime("%Y-%m-%d"),
                "Fin": end_date.strftime("%Y-%m-%d"),
                "Charge": task_charge,
                "Dépendance": task_depends,
                "Statut": "✅ Planifié"
            })
        
        for custom_task_name in custom_tasks:
            if custom_task_name not in st.session_state.tasks_config:
                if custom_task_name in st.session_state.custom_tasks:
                    custom_task = st.session_state.custom_tasks[custom_task_name]
                    
                    manual_start, manual_end = get_task_manual_dates(project["name"], custom_task_name)
                    
                    if manual_start and manual_end:
                        start_date = pd.to_datetime(manual_start)
                        end_date = pd.to_datetime(manual_end)
                    else:
                        start_date = pd.to_datetime(custom_task.get("start_date", ITERATIONS[0]["start"]))
                        end_date = start_date + timedelta(days=custom_task.get("charge", 1))
                    
                    task_key = f"{project['name']}_{custom_task_name}"
                    task_dates[task_key] = (start_date, end_date)
                    
                    planning.append({
                        "Priorité": project["priority"],
                        "Projet": project["name"],
                        "Tâche": custom_task_name,
                        "Équipe": custom_task.get("team", "N/A"),
                        "Début": start_date.strftime("%Y-%m-%d"),
                        "Fin": end_date.strftime("%Y-%m-%d"),
                        "Charge": custom_task.get("charge", 1),
                        "Dépendance": custom_task.get("depends_on", None),
                        "Statut": "✅ Planifié"
                    })
    
    return planning, task_dates

def create_gantt_with_dependencies(df_gantt, project_name):
    """Crée un Gantt avec flèches de dépendances"""
    if df_gantt.empty:
        return None
    
    fig = px.timeline(
        df_gantt, 
        x_start="Start Date", 
        x_end="End Date", 
        y="Tâche",
        color="Équipe",
        color_discrete_map=TEAM_COLORS,
        hover_data=["Équipe", "Charge", "Dépendance"],
        title=f"📅 Gantt: {project_name}",
        height=max(400, len(df_gantt) * 45)
    )
    
    # Ajouter les itérations
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
    
    # Ajouter les jours fériés
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
    
    # Créer un mapping tâche -> position Y
    task_list = df_gantt["Tâche"].tolist()
    task_y_positions = {task: len(task_list) - 1 - idx for idx, task in enumerate(task_list)}
    
    # Ajouter les flèches de dépendances
    for idx, row in df_gantt.iterrows():
        if row["Dépendance"] and row["Dépendance"] in task_y_positions:
            parent_task = row["Dépendance"]
            parent_y = task_y_positions[parent_task]
            
            current_task = row["Tâche"]
            current_y = task_y_positions[current_task]
            
            parent_row = df_gantt[df_gantt["Tâche"] == parent_task]
            if not parent_row.empty:
                parent_end = parent_row.iloc[0]["End Date"]
                current_start = row["Start Date"]
                
                fig.add_annotation(
                    x=parent_end,
                    y=parent_y,
                    ax=current_start,
                    ay=current_y,
                    xref="x",
                    yref="y",
                    axref="x",
                    ayref="y",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="rgba(100, 100, 100, 0.6)",
                    standoff=5,
                    startstandoff=5
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
    
    return fig

# Calcul planning
planning, task_dates = calculate_planning()
df_plan = pd.DataFrame(planning)

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLETS
# ═══════════════════════════════════════════════════════════════════════════════

tab_projects, tab_planning, tab_capa, tab_cong = st.tabs([
    "🎯 Gérer les Tâches par Projet",
    "📋 Vue Globale Planning",
    "📊 Capacités",
    "🏖️ Congés & Run"
])

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 0: PROJETS & TÂCHES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_projects:
    st.subheader("🎯 Gérer les Tâches par Projet")
    
    # Sélecteur de projet
    selected_proj = st.selectbox("📂 Sélectionner un projet", options=[p["name"] for p in PROJECTS], key="project_selector")
    
    if selected_proj:
        st.markdown(f"#### Projet: **{selected_proj}**")
        st.divider()
        
        all_project_tasks = get_all_tasks_for_project(selected_proj)
        task_dates_dict = calculate_dates_for_project(selected_proj)
        
        # ═════════════════════════════════════════════════════════════════════════
        # GANTT EN HAUT
        # ═════════════════════════════════════════════════════════════════════════
        
        # Préparer les données pour le Gantt du projet
        project_gantt_data = []
        for task in sorted(get_tasks_list(), key=lambda t: t["order"]):
            if task["name"] not in all_project_tasks:
                continue
            
            charge = get_task_charge_for_project(selected_proj, task["name"])
            depends = get_task_depends_for_project(selected_proj, task["name"])
            
            if task["name"] in task_dates_dict:
                start_dt, end_dt = task_dates_dict[task["name"]]
                
                project_gantt_data.append({
                    "Tâche": task["name"],
                    "Équipe": task["team"],
                    "Charge": charge,
                    "Dépendance": depends,
                    "Start Date": start_dt,
                    "End Date": end_dt
                })
        
        # Ajouter les tâches custom
        for custom_task_name in st.session_state.projects_tasks.get(selected_proj, {}).get("custom", []):
            if custom_task_name in st.session_state.custom_tasks:
                custom_task = st.session_state.custom_tasks[custom_task_name]
                
                if custom_task_name in task_dates_dict:
                    start_dt, end_dt = task_dates_dict[custom_task_name]
                    
                    project_gantt_data.append({
                        "Tâche": custom_task_name,
                        "Équipe": custom_task.get("team", "N/A"),
                        "Charge": custom_task.get("charge", 1),
                        "Dépendance": custom_task.get("depends_on", None),
                        "Start Date": start_dt,
                        "End Date": end_dt
                    })
        
        df_project_gantt = pd.DataFrame(project_gantt_data)
        
        if not df_project_gantt.empty:
            fig_gantt = create_gantt_with_dependencies(df_project_gantt, selected_proj)
            if fig_gantt:
                st.plotly_chart(fig_gantt, use_container_width=True)
        else:
            st.info("Aucune tâche à afficher dans le Gantt")
        
        st.divider()
        
        # ═════════════════════════════════════════════════════════════════════════
        # TABLEAU ÉDITABLE - AVEC DATES ÉDITABLES, DÉPENDANCES, SUPPRESSION
        # ═════════════════════════════════════════════════════════════════════════
        st.markdown("**📋 Configuration des Tâches**")
        
        # Construire le tableau éditable
        config_data = []
        task_order = []
        
        for task in sorted(get_tasks_list(), key=lambda t: t["order"]):
            if task["name"] not in all_project_tasks:
                continue
            
            charge = get_task_charge_for_project(selected_proj, task["name"])
            depends = get_task_depends_for_project(selected_proj, task["name"])
            
            # Calculer les dates
            if task["name"] in task_dates_dict:
                start_dt, end_dt = task_dates_dict[task["name"]]
                start_date = start_dt.date()
                end_date = end_dt.date()
            else:
                start_date = date(2026, 1, 12)
                end_date = date(2026, 1, 12)
            
            config_data.append({
                "🗑️": False,
                "Tâche": task["name"],
                "Équipe": task["team"],
                "Charge (j)": charge,
                "Début": start_date,
                "Fin": end_date,
                "Dépend de": depends if depends else "(Aucune)"
            })
            task_order.append(task["name"])
        
        # Ajouter les tâches custom
        for custom_task_name in st.session_state.projects_tasks.get(selected_proj, {}).get("custom", []):
            if custom_task_name in st.session_state.custom_tasks:
                custom_task = st.session_state.custom_tasks[custom_task_name]
                
                if custom_task_name in task_dates_dict:
                    start_dt, end_dt = task_dates_dict[custom_task_name]
                    start_date = start_dt.date()
                    end_date = end_dt.date()
                else:
                    start_date = date(2026, 1, 12)
                    end_date = date(2026, 1, 12)
                
                config_data.append({
                    "🗑️": False,
                    "Tâche": custom_task_name,
                    "Équipe": custom_task.get("team", "N/A"),
                    "Charge (j)": custom_task.get("charge", 1),
                    "Début": start_date,
                    "Fin": end_date,
                    "Dépend de": custom_task.get("depends_on", "(Aucune)") if custom_task.get("depends_on") else "(Aucune)"
                })
                task_order.append(custom_task_name)
        
        df_config = pd.DataFrame(config_data)
        
        # Éditeur de données
        all_project_tasks_for_selector = get_all_tasks_for_project(selected_proj)
        
        edited_config = st.data_editor(
            df_config,
            use_container_width=True,
            hide_index=True,
            key=f"config_editor_{selected_proj}",
            column_config={
                "🗑️": st.column_config.CheckboxColumn("🗑️", help="Cocher pour supprimer", width="small"),
                "Tâche": st.column_config.TextColumn(disabled=True, width="large"),
                "Équipe": st.column_config.TextColumn(disabled=True, width="medium"),
                "Charge (j)": st.column_config.NumberColumn("Charge (j)", min_value=0.5, max_value=20, step=0.5, width="small"),
                "Début": st.column_config.DateColumn("Début", format="DD/MM/YYYY", width="small"),
                "Fin": st.column_config.DateColumn("Fin", format="DD/MM/YYYY", width="small"),
                "Dépend de": st.column_config.SelectboxColumn(
                    "Dépend de",
                    options=["(Aucune)"] + all_project_tasks_for_selector,
                    width="medium"
                )
            }
        )
        
        # Traiter les changements
        dates_changed = False
        for idx, row in edited_config.iterrows():
            task_name = row["Tâche"]
            
            if task_name in task_order:
                override_key = f"{selected_proj}_{task_name}"
                
                # Récupérer les valeurs originales
                if task_name in task_dates_dict:
                    original_start_dt, original_end_dt = task_dates_dict[task_name]
                    original_start = original_start_dt.date()
                    original_end = original_end_dt.date()
                else:
                    original_start = date(2026, 1, 12)
                    original_end = date(2026, 1, 12)
                
                if task_name in st.session_state.tasks_config:
                    original_task = st.session_state.tasks_config[task_name]
                    original_charge = original_task["charge"]
                    original_depends = original_task["depends_on"]
                else:
                    if task_name in st.session_state.custom_tasks:
                        original_charge = st.session_state.custom_tasks[task_name]["charge"]
                        original_depends = st.session_state.custom_tasks[task_name].get("depends_on")
                    else:
                        original_charge = 1
                        original_depends = None
                
                new_charge = row["Charge (j)"]
                new_depends = None if row["Dépend de"] == "(Aucune)" else row["Dépend de"]
                new_start = row["Début"]
                new_end = row["Fin"]
                
                # Créer l'override si nécessaire
                if override_key not in st.session_state.project_task_overrides:
                    st.session_state.project_task_overrides[override_key] = {}
                
                # Détecter les changements
                if new_charge != original_charge or new_depends != original_depends:
                    st.session_state.project_task_overrides[override_key]["charge"] = new_charge
                    st.session_state.project_task_overrides[override_key]["depends_on"] = new_depends
                
                # Détecter les changements de dates
                if new_start != original_start or new_end != original_end:
                    st.session_state.project_task_overrides[override_key]["start_date"] = new_start
                    st.session_state.project_task_overrides[override_key]["end_date"] = new_end
                    dates_changed = True
        
        # Si des dates ont changé, recalculer et rerun
        if dates_changed:
            st.rerun()
        
        # Bouton pour supprimer les tâches cochées
        tasks_to_delete = edited_config[edited_config["🗑️"] == True]["Tâche"].tolist()
        
        if tasks_to_delete:
            st.warning(f"⚠️ {len(tasks_to_delete)} tâche(s) sélectionnée(s) pour suppression : {', '.join(tasks_to_delete)}")
            
            if st.button("🗑️ Supprimer les tâches cochées", type="primary", key=f"btn_delete_checked_{selected_proj}"):
                for task_name in tasks_to_delete:
                    custom_tasks = st.session_state.projects_tasks[selected_proj].get("custom", [])
                    default_tasks = st.session_state.projects_tasks[selected_proj].get("default", [])
                    
                    if task_name in custom_tasks:
                        st.session_state.projects_tasks[selected_proj]["custom"].remove(task_name)
                    elif task_name in default_tasks:
                        st.session_state.projects_tasks[selected_proj]["default"].remove(task_name)
                
                st.success(f"✅ {len(tasks_to_delete)} tâche(s) supprimée(s) !")
                st.rerun()
        
        st.divider()
        
        # ═════════════════════════════════════════════════════════════════════════
        # AJOUTER UNE TÂCHE TEMPLATE
        # ═════════════════════════════════════════════════════════════════════════
        st.markdown("**➕ Ajouter une Tâche Template**")
        
        all_task_names = [t["name"] for t in get_tasks_list()]
        available_tasks = [t for t in all_task_names if t not in all_project_tasks]
        
        if available_tasks:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_task = st.selectbox("Sélectionner une tâche template", options=available_tasks, key=f"add_default_task_{selected_proj}")
            
            with col2:
                if st.button("➕ Ajouter", key=f"btn_add_default_{selected_proj}"):
                    st.session_state.projects_tasks[selected_proj]["default"].append(new_task)
                    st.success(f"✅ Tâche '{new_task}' ajoutée !")
                    st.rerun()
        else:
            st.info("✅ Toutes les tâches template sont déjà assignées à ce projet.")
        
        st.divider()
        
        # ═════════════════════════════════════════════════════════════════════════
        # CRÉER UNE TÂCHE PERSONNALISÉE
        # ═════════════════════════════════════════════════════════════════════════
        st.markdown("**➕ Créer une Tâche Personnalisée**")
        
        col_name, col_team, col_charge = st.columns(3)
        
        with col_name:
            new_task_name = st.text_input("📝 Nom de la tâche", placeholder="Ex: Migration BDD", key=f"new_task_name_{selected_proj}")
        
        with col_team:
            new_task_team = st.selectbox("👥 Équipe responsable", options=TEAMS, key=f"new_task_team_{selected_proj}")
        
        with col_charge:
            new_task_charge = st.number_input("📅 Charge (jours)", min_value=0.5, max_value=20.0, step=0.5, value=1.0, key=f"new_task_charge_{selected_proj}")
        
        col_dep = st.columns(1)[0]
        
        with col_dep:
            dep_options = ["(Aucune)"] + get_all_tasks_for_project(selected_proj)
            new_task_dep = st.selectbox("🔗 Dépendance", options=dep_options, key=f"new_task_dep_{selected_proj}")
        
        if st.button("➕ Créer la tâche personnalisée", key=f"btn_create_custom_{selected_proj}"):
            if new_task_name:
                st.session_state.custom_tasks[new_task_name] = {
                    "team": new_task_team,
                    "charge": new_task_charge,
                    "start_date": ITERATIONS[0]["start"],
                    "depends_on": None if new_task_dep == "(Aucune)" else new_task_dep
                }
                
                st.session_state.projects_tasks[selected_proj]["custom"].append(new_task_name)
                st.success(f"✅ Tâche personnalisée '{new_task_name}' créée !")
                st.rerun()
            else:
                st.error("❌ Veuillez entrer un nom de tâche")

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 1: VUE GLOBALE PLANNING
# ═══════════════════════════════════════════════════════════════════════════════
with tab_planning:
    st.subheader("📋 Vue Globale du Planning")
    st.info("📊 Vue d'ensemble de toutes les tâches de tous les projets")
    
    if not df_plan.empty:
        display_cols = ["Priorité", "Projet", "Tâche", "Équipe", "Début", "Fin", "Charge", "Dépendance", "Statut"]
        
        st.dataframe(
            df_plan[display_cols].sort_values("Priorité"),
            use_container_width=True,
            hide_index=True,
            height=600
        )
    else:
        st.warning("Aucune donnée de planning disponible")

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 2: CAPACITÉS
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
# ONGLET 3: CONGÉS & RUN
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
st.markdown(f"🛠 **PI Planning Tool v6.4** | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
