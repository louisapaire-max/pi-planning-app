import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json

st.set_page_config(page_title="PI Planning - Capacity Tool v7.6", layout="wide")
st.title("📊 PI Planning - Capacity Planning avec Dépendances & Sizing")

HOLIDAYS_2026 = [
    "2026-01-01", "2026-04-06", "2026-05-01", "2026-05-08", 
    "2026-05-14", "2026-05-25", "2026-07-14", "2026-08-15", 
    "2026-11-01", "2026-11-11", "2026-12-25"
]

ITERATIONS = [
    {"name": "Itération #1", "start": "2025-12-22", "end": "2026-01-09"},
    {"name": "Itération #2", "start": "2026-01-12", "end": "2026-01-30"},
    {"name": "Itération #3", "start": "2026-02-02", "end": "2026-02-20"},
    {"name": "Itération #4", "start": "2026-02-23", "end": "2026-03-13"},
    {"name": "Itération #5", "start": "2026-03-16", "end": "2026-03-20"},
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
# FONCTIONS EXPORT/IMPORT
# ═══════════════════════════════════════════════════════════════════════════════

def export_data():
    """Exporte toutes les données en JSON"""
    capacity_export = {f"{k[0]}||{k[1]}": v for k, v in st.session_state.capacity.items()}
    leaves_export = {f"{k[0]}||{k[1]}": v for k, v in st.session_state.leaves.items()}
    run_days_export = {f"{k[0]}||{k[1]}": v for k, v in st.session_state.run_days.items()}
    
    overrides_export = {}
    for key, value in st.session_state.project_task_overrides.items():
        overrides_export[key] = {}
        for k, v in value.items():
            if isinstance(v, date):
                overrides_export[key][k] = v.isoformat()
            else:
                overrides_export[key][k] = v
    
    data = {
        "version": "7.6",
        "export_date": datetime.now().isoformat(),
        "tasks_config": st.session_state.tasks_config,
        "projects_tasks": st.session_state.projects_tasks,
        "custom_tasks": st.session_state.custom_tasks,
        "project_task_overrides": overrides_export,
        "capacity": capacity_export,
        "leaves": leaves_export,
        "run_days": run_days_export
    }
    
    return json.dumps(data, indent=2, ensure_ascii=False)

def import_data(json_str):
    """Importe les données depuis un JSON"""
    try:
        data = json.loads(json_str)
        
        st.session_state.tasks_config = data.get("tasks_config", {})
        st.session_state.projects_tasks = data.get("projects_tasks", {})
        st.session_state.custom_tasks = data.get("custom_tasks", {})
        
        overrides_import = data.get("project_task_overrides", {})
        st.session_state.project_task_overrides = {}
        for key, value in overrides_import.items():
            st.session_state.project_task_overrides[key] = {}
            for k, v in value.items():
                if k in ["start_date", "end_date"] and v:
                    st.session_state.project_task_overrides[key][k] = date.fromisoformat(v)
                else:
                    st.session_state.project_task_overrides[key][k] = v
        
        capacity_import = data.get("capacity", {})
        st.session_state.capacity = {tuple(k.split("||")): v for k, v in capacity_import.items()}
        
        leaves_import = data.get("leaves", {})
        st.session_state.leaves = {tuple(k.split("||")): v for k, v in leaves_import.items()}
        
        run_days_import = data.get("run_days", {})
        st.session_state.run_days = {tuple(k.split("||")): v for k, v in run_days_import.items()}
        
        return True, f"✅ Données importées avec succès (version {data.get('version', 'inconnue')})"
    except Exception as e:
        return False, f"❌ Erreur lors de l'import : {str(e)}"

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - EXPORT/IMPORT
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.header("💾 Sauvegarde & Import")
    
    st.markdown("### 📤 Exporter les données")
    
    if st.button("📥 Télécharger la configuration", type="primary", use_container_width=True):
        json_data = export_data()
        st.download_button(
            label="💾 Enregistrer le fichier JSON",
            data=json_data,
            file_name=f"pi_planning_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.divider()
    
    st.markdown("### 📥 Importer les données")
    uploaded_file = st.file_uploader("Charger un fichier de sauvegarde", type=["json"])
    
    if uploaded_file is not None:
        json_content = uploaded_file.read().decode("utf-8")
        success, message = import_data(json_content)
        
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
    
    st.divider()
    st.caption(f"Version 7.6 | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

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

def validate_task_day(task_name, start_date):
    """Valide si la date de début correspond aux contraintes métier"""
    if not start_date:
        return "✅"
    
    if isinstance(start_date, date) and not isinstance(start_date, datetime):
        start_dt = datetime.combine(start_date, datetime.min.time())
    else:
        start_dt = pd.to_datetime(start_date)
    
    weekday = start_dt.weekday()
    
    if task_name in ["Refinement", "Etude d'impact"]:
        if weekday != 2:
            return "🔴 Mercredi requis"
        return "✅"
    
    if task_name == "PROD":
        if weekday == 4:
            return "🔴 Pas de vendredi"
        return "✅"
    
    return "✅"

def calculate_dates_for_project(project_name):
    """Calcule les dates de début et fin pour chaque tâche d'un projet"""
    TASKS = get_tasks_list()
    project_task_names = get_all_tasks_for_project(project_name)
    
    task_dates = {}
    first_iter_start = pd.to_datetime(ITERATIONS[0]["start"])
    
    for task in sorted(TASKS, key=lambda t: t["order"]):
        if task["name"] not in project_task_names:
            continue
        
        manual_start, manual_end = get_task_manual_dates(project_name, task["name"])
        
        if manual_start and manual_end:
            start_date = pd.to_datetime(manual_start)
            end_date = pd.to_datetime(manual_end)
        else:
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

def get_current_week_range():
    """Retourne le début et fin de la semaine actuelle (lundi à dimanche)"""
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def get_tasks_for_period(start_date, end_date):
    """Récupère toutes les tâches dans une période donnée"""
    planning, _ = calculate_planning()
    df_plan = pd.DataFrame(planning)
    
    if df_plan.empty:
        return pd.DataFrame()
    
    df_plan["Start Date"] = pd.to_datetime(df_plan["Début"], errors='coerce')
    df_plan["End Date"] = pd.to_datetime(df_plan["Fin"], errors='coerce')
    
    mask = (
        ((df_plan["Start Date"] <= pd.to_datetime(end_date)) & 
         (df_plan["End Date"] >= pd.to_datetime(start_date)))
    )
    
    return df_plan[mask].copy()

def create_gantt_chart_project(df_gantt, title="Gantt Chart"):
    """Crée un Gantt pour un projet individuel avec tâches terminées en vert"""
    if df_gantt.empty:
        return None
    
    today = pd.to_datetime(datetime.now().date())
    df_gantt["Statut_Tâche"] = df_gantt["End Date"].apply(
        lambda x: "✅ Terminée" if pd.to_datetime(x) < today else "⏳ En cours / À venir"
    )
    
    fig = go.Figure()
    
    for idx, row in df_gantt.iterrows():
        if row["Statut_Tâche"] == "✅ Terminée":
            color = "#28A745"
        else:
            color = TEAM_COLORS.get(row["Équipe"], "#999999")
        
        duration = row["End Date"] - row["Start Date"]
        
        fig.add_trace(go.Bar(
            x=[duration],
            y=[row["Tâche"]],
            base=row["Start Date"],
            orientation='h',
            marker=dict(color=color),
            name=row["Équipe"],
            showlegend=False,
            hovertemplate=(
                f"<b>{row['Tâche']}</b><br>" +
                f"Équipe: {row['Équipe']}<br>" +
                f"Charge: {row['Charge']}j<br>" +
                f"Dépendance: {row.get('Dépendance', 'Aucune')}<br>" +
                f"Statut: {row['Statut_Tâche']}<extra></extra>"
            )
        ))
    
    colors_bg = ["rgba(230, 230, 230, 0.3)", "rgba(200, 230, 255, 0.3)", "rgba(220, 255, 220, 0.3)", "rgba(255, 220, 220, 0.3)", "rgba(220, 255, 255, 0.3)"]
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
    
    today_str = datetime.now().date().isoformat()
    fig.add_shape(
        type="line",
        x0=today_str,
        x1=today_str,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="red", width=3, dash="solid")
    )
    
    fig.add_annotation(
        x=today_str,
        y=1,
        yref="paper",
        text="📍 AUJOURD'HUI",
        showarrow=False,
        yshift=10,
        font=dict(size=12, color="red")
    )

    first_iteration_start = ITERATIONS[0]["start"]
    last_iteration_end = ITERATIONS[-1]["end"]
    
    fig.update_xaxes(
        range=[first_iteration_start, last_iteration_end],
        tickformat="%d/%m/%Y",
        dtick=86400000.0 * 2,
        side="top",
        tickfont=dict(size=10),
        tickangle=-45,
        showgrid=True,
        gridwidth=1,
        gridcolor='LightGray'
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        title=title,
        height=max(500, len(df_gantt) * 50),
        showlegend=False,
        margin=dict(t=100, b=50)
    )
    
    return fig

def create_gantt_chart_global(df_gantt, title="Gantt Chart"):
    """Crée un Gantt global avec toutes les tâches"""
    if df_gantt.empty:
        return None
    
    fig = px.timeline(
        df_gantt, 
        x_start="Start Date", 
        x_end="End Date", 
        y="Tâche_Projet",
        color="Équipe",
        color_discrete_map=TEAM_COLORS,
        hover_data=["Projet", "Équipe", "Charge", "Dépendance"],
        title=title,
        height=max(600, len(df_gantt) * 30)
    )
    
    colors_bg = ["rgba(230, 230, 230, 0.3)", "rgba(200, 230, 255, 0.3)", "rgba(220, 255, 220, 0.3)", "rgba(255, 220, 220, 0.3)", "rgba(220, 255, 255, 0.3)"]
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
    
    today_str = datetime.now().date().isoformat()
    fig.add_shape(
        type="line",
        x0=today_str,
        x1=today_str,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="red", width=3, dash="solid")
    )
    
    fig.add_annotation(
        x=today_str,
        y=1,
        yref="paper",
        text="📍 AUJOURD'HUI",
        showarrow=False,
        yshift=10,
        font=dict(size=12, color="red")
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

tab_projects, tab_planning, tab_today, tab_capa = st.tabs([
    "🎯 Gérer les Tâches par Projet",
    "📋 Vue Globale Planning",
    "📅 Aujourd'hui & Cette semaine",
    "📊 Capacités & Ressources"
])

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 0: PROJETS & TÂCHES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_projects:
    st.subheader("🎯 Gérer les Tâches par Projet")
    
    selected_proj = st.selectbox("📂 Sélectionner un projet", options=[p["name"] for p in PROJECTS], key="project_selector")
    
    if selected_proj:
        st.markdown(f"#### Projet: **{selected_proj}**")
        st.divider()
        
        all_project_tasks = get_all_tasks_for_project(selected_proj)
        task_dates_dict = calculate_dates_for_project(selected_proj)
        
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
            fig_gantt = create_gantt_chart_project(df_project_gantt, title=f"📅 Gantt: {selected_proj}")
            if fig_gantt:
                st.plotly_chart(fig_gantt, use_container_width=True)
        else:
            st.info("Aucune tâche à afficher dans le Gantt")
        
        st.divider()
        
        st.markdown("**📋 Configuration des Tâches**")
        st.info("📌 **Contraintes métier** : Refinement & Etude d'impact → Mercredi uniquement | PROD → Pas de vendredi")
        
        config_data = []
        task_order = []
        
        for task in sorted(get_tasks_list(), key=lambda t: t["order"]):
            if task["name"] not in all_project_tasks:
                continue
            
            charge = get_task_charge_for_project(selected_proj, task["name"])
            depends = get_task_depends_for_project(selected_proj, task["name"])
            
            if task["name"] in task_dates_dict:
                start_dt, end_dt = task_dates_dict[task["name"]]
                start_date = start_dt.date()
                end_date = end_dt.date()
            else:
                start_date = date(2026, 1, 12)
                end_date = date(2026, 1, 12)
            
            validation = validate_task_day(task["name"], start_date)
            
            config_data.append({
                "⚠️": validation,
                "🗑️": False,
                "Tâche": task["name"],
                "Équipe": task["team"],
                "Charge (j)": charge,
                "Début": start_date,
                "Fin": end_date,
                "Dépend de": depends if depends else "(Aucune)"
            })
            task_order.append(task["name"])
        
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
                
                validation = validate_task_day(custom_task_name, start_date)
                
                config_data.append({
                    "⚠️": validation,
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
        
        all_project_tasks_for_selector = get_all_tasks_for_project(selected_proj)
        
        edited_config = st.data_editor(
            df_config,
            use_container_width=True,
            hide_index=True,
            key=f"config_editor_{selected_proj}",
            column_config={
                "⚠️": st.column_config.TextColumn("⚠️", help="Validation des contraintes métier", width="small", disabled=True),
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
        
        dates_changed = False
        for idx, row in edited_config.iterrows():
            task_name = row["Tâche"]
            
            if task_name in task_order:
                override_key = f"{selected_proj}_{task_name}"
                
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
                
                if override_key not in st.session_state.project_task_overrides:
                    st.session_state.project_task_overrides[override_key] = {}
                
                if new_charge != original_charge or new_depends != original_depends:
                    st.session_state.project_task_overrides[override_key]["charge"] = new_charge
                    st.session_state.project_task_overrides[override_key]["depends_on"] = new_depends
                
                if new_start != original_start or new_end != original_end:
                    st.session_state.project_task_overrides[override_key]["start_date"] = new_start
                    st.session_state.project_task_overrides[override_key]["end_date"] = new_end
                    dates_changed = True
        
        if dates_changed:
            st.rerun()
        
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
        df_plan["Start Date"] = pd.to_datetime(df_plan["Début"], errors='coerce')
        df_plan["End Date"] = pd.to_datetime(df_plan["Fin"], errors='coerce')
        
        st.markdown("### 🔍 Filtres")
        
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            all_projects = ["Tous"] + sorted(df_plan["Projet"].unique().tolist())
            selected_projects = st.multiselect(
                "📂 Projets",
                options=all_projects,
                default=["Tous"],
                key="filter_projects"
            )
        
        with col_filter2:
            all_teams = ["Toutes"] + sorted(df_plan["Équipe"].unique().tolist())
            selected_teams = st.multiselect(
                "👥 Équipes",
                options=all_teams,
                default=["Toutes"],
                key="filter_teams"
            )
        
        with col_filter3:
            all_tasks = ["Toutes"] + sorted(df_plan["Tâche"].unique().tolist())
            selected_tasks = st.multiselect(
                "📋 Tâches",
                options=all_tasks,
                default=["Toutes"],
                key="filter_tasks"
            )
        
        if st.button("🔄 Réinitialiser les filtres", key="reset_filters"):
            st.session_state.filter_projects = ["Tous"]
            st.session_state.filter_teams = ["Toutes"]
            st.session_state.filter_tasks = ["Toutes"]
            st.rerun()
        
        st.divider()
        
        df_filtered = df_plan.copy()
        
        if "Tous" not in selected_projects and len(selected_projects) > 0:
            df_filtered = df_filtered[df_filtered["Projet"].isin(selected_projects)]
        
        if "Toutes" not in selected_teams and len(selected_teams) > 0:
            df_filtered = df_filtered[df_filtered["Équipe"].isin(selected_teams)]
        
        if "Toutes" not in selected_tasks and len(selected_tasks) > 0:
            df_filtered = df_filtered[df_filtered["Tâche"].isin(selected_tasks)]
        
        if not df_filtered.empty:
            st.divider()
            
            df_gantt_global = df_filtered.dropna(subset=["Start Date", "End Date"]).copy()
            df_gantt_global["Tâche_Projet"] = df_gantt_global["Tâche"] + " [" + df_gantt_global["Projet"].str[:30] + "]"
            
            if not df_gantt_global.empty:
                fig_global = create_gantt_chart_global(df_gantt_global, title="📅 Gantt Global - Vue Filtrée")
                if fig_global:
                    st.plotly_chart(fig_global, use_container_width=True)
            else:
                st.warning("Aucune tâche à afficher dans le Gantt avec ces filtres")
            
            st.divider()
            
            st.markdown("### 📊 Tableau détaillé")
            
            display_cols = ["Priorité", "Projet", "Tâche", "Équipe", "Début", "Fin", "Charge", "Dépendance", "Statut"]
            
            col_sort1, col_sort2 = st.columns([2, 1])
            
            with col_sort1:
                sort_by = st.selectbox(
                    "Trier par",
                    options=["Priorité", "Projet", "Équipe", "Début", "Charge"],
                    index=0,
                    key="sort_by_global"
                )
            
            with col_sort2:
                sort_order = st.selectbox(
                    "Ordre",
                    options=["Croissant", "Décroissant"],
                    index=0,
                    key="sort_order_global"
                )
            
            ascending = True if sort_order == "Croissant" else False
            df_sorted = df_filtered.sort_values(by=sort_by, ascending=ascending)
            
            st.dataframe(
                df_sorted[display_cols],
                use_container_width=True,
                hide_index=True,
                height=600
            )
            
            st.divider()
            
            csv_data = df_sorted[display_cols].to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Télécharger le planning filtré (CSV)",
                data=csv_data,
                file_name=f"planning_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        else:
            st.warning("❌ Aucune donnée ne correspond aux filtres sélectionnés")
            st.info("💡 Astuce : Essayez de réinitialiser les filtres ou de sélectionner d'autres critères")
    
    else:
        st.warning("Aucune donnée de planning disponible")

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 2: AUJOURD'HUI & CETTE SEMAINE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_today:
    st.subheader("📅 Aujourd'hui & Cette semaine")
    
    today = datetime.now().date()
    week_start, week_end = get_current_week_range()
    
    st.info(f"📆 **Aujourd'hui** : {today.strftime('%A %d %B %Y')} | **Semaine** : {week_start.strftime('%d/%m')} → {week_end.strftime('%d/%m/%Y')}")
    
    st.markdown("## 🔥 Tâches en cours aujourd'hui")
    
    df_today = get_tasks_for_period(today, today)
    
    if not df_today.empty:
        projects_today = df_today.groupby("Projet")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Projets actifs", len(projects_today))
        with col2:
            st.metric("📋 Tâches en cours", len(df_today))
        with col3:
            teams_active = df_today["Équipe"].nunique()
            st.metric("👥 Équipes mobilisées", teams_active)
        
        st.divider()
        
        for project_name, tasks in projects_today:
            with st.expander(f"**{project_name}**", expanded=True):
                for idx, task in tasks.iterrows():
                    team_color = TEAM_COLORS.get(task["Équipe"], "#999999")
                    
                    col_task, col_team, col_dates = st.columns([3, 2, 2])
                    
                    with col_task:
                        st.markdown(f"**{task['Tâche']}**")
                    
                    with col_team:
                        st.markdown(f"<span style='background-color: {team_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>{task['Équipe']}</span>", unsafe_allow_html=True)
                    
                    with col_dates:
                        st.caption(f"📅 {task['Début']} → {task['Fin']}")
                
                st.divider()
    else:
        st.warning("🎉 Aucune tâche en cours aujourd'hui !")
    
    st.divider()
    
    st.markdown("## 📆 Planning de la semaine")
    
    df_week = get_tasks_for_period(week_start, week_end)
    
    if not df_week.empty:
        df_week = df_week.sort_values(["Priorité", "Start Date"])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Projets actifs", df_week["Projet"].nunique())
        with col2:
            st.metric("📋 Tâches totales", len(df_week))
        with col3:
            charge_totale = df_week["Charge"].sum()
            st.metric("⏱️ Charge totale", f"{charge_totale:.1f}j")
        with col4:
            teams_week = df_week["Équipe"].nunique()
            st.metric("👥 Équipes", teams_week)
        
        st.divider()
        
        st.markdown("### 📋 Détail par projet")
        
        projects_week = df_week.groupby("Projet")
        
        for project_name, tasks in projects_week:
            project_priority = tasks.iloc[0]["Priorité"]
            
            with st.expander(f"**[P{project_priority}] {project_name}** ({len(tasks)} tâche{'s' if len(tasks) > 1 else ''})", expanded=False):
                tasks_sorted = tasks.sort_values("Start Date")
                
                table_data = []
                for idx, task in tasks_sorted.iterrows():
                    task_start = task["Start Date"].date()
                    task_end = task["End Date"].date()
                    
                    if task_end < today:
                        status = "✅ Terminée"
                    elif task_start <= today <= task_end:
                        status = "🔵 En cours"
                    else:
                        status = "⏳ À venir"
                    
                    table_data.append({
                        "Statut": status,
                        "Tâche": task["Tâche"],
                        "Équipe": task["Équipe"],
                        "Début": task_start.strftime("%d/%m"),
                        "Fin": task_end.strftime("%d/%m"),
                        "Charge": f"{task['Charge']}j"
                    })
                
                df_table = pd.DataFrame(table_data)
                
                st.dataframe(
                    df_table,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Statut": st.column_config.TextColumn("Statut", width="small"),
                        "Tâche": st.column_config.TextColumn("Tâche", width="large"),
                        "Équipe": st.column_config.TextColumn("Équipe", width="medium"),
                        "Début": st.column_config.TextColumn("Début", width="small"),
                        "Fin": st.column_config.TextColumn("Fin", width="small"),
                        "Charge": st.column_config.TextColumn("Charge", width="small"),
                    }
                )
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    terminées = len([t for t in table_data if t["Statut"] == "✅ Terminée"])
                    st.caption(f"✅ Terminées : {terminées}")
                with col_b:
                    en_cours = len([t for t in table_data if t["Statut"] == "🔵 En cours"])
                    st.caption(f"🔵 En cours : {en_cours}")
                with col_c:
                    a_venir = len([t for t in table_data if t["Statut"] == "⏳ À venir"])
                    st.caption(f"⏳ À venir : {a_venir}")
        
        st.divider()
        
        st.markdown("### 👥 Charge par équipe cette semaine")
        
        team_workload = df_week.groupby("Équipe")["Charge"].sum().sort_values(ascending=False)
        
        col_teams = st.columns(min(4, len(team_workload)))
        
        for idx, (team, charge) in enumerate(team_workload.items()):
            with col_teams[idx % len(col_teams)]:
                team_color = TEAM_COLORS.get(team, "#999999")
                st.markdown(
                    f"<div style='background-color: {team_color}; color: white; padding: 10px; border-radius: 8px; text-align: center;'>"
                    f"<strong>{team}</strong><br>{charge:.1f} jours</div>",
                    unsafe_allow_html=True
                )
        
    else:
        st.warning("📭 Aucune tâche planifiée cette semaine")

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 3: CAPACITÉS & RESSOURCES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_capa:
    st.subheader("📊 Capacités & Ressources")
    
    st.markdown("### 💼 Capacités Brutes (Jours)")
    
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
    
    st.divider()
    
    col_leave, col_run = st.columns(2)
    
    with col_leave:
        st.markdown("### 🏖️ Congés (jours)")
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
        st.markdown("### 🛠️ Run & Support (jours)")
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
st.markdown(f"🛠 **PI Planning Tool v7.6** | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
