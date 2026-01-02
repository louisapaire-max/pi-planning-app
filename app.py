import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json

st.set_page_config(page_title="PI Planning - Capacity Tool v8.0", layout="wide")
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
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

def is_weekend(date_obj):
    """Vérifie si une date est un weekend"""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
    return date_obj.weekday() in [5, 6]  # 5 = samedi, 6 = dimanche

def get_next_weekday(date_obj):
    """Retourne le prochain jour ouvrable si la date est un weekend"""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
    
    while date_obj.weekday() in [5, 6]:
        date_obj += timedelta(days=1)
    
    return date_obj

def get_previous_weekday(date_obj):
    """Retourne le jour ouvrable précédent si la date est un weekend"""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
    
    while date_obj.weekday() in [5, 6]:
        date_obj -= timedelta(days=1)
    
    return date_obj

def auto_correct_weekend_dates(project_name):
    """Corrige automatiquement toutes les dates de weekend pour un projet"""
    corrections_made = []
    
    for task_name in get_all_tasks_for_project(project_name):
        override_key = f"{project_name}_{task_name}"
        
        if override_key in st.session_state.project_task_overrides:
            start_date = st.session_state.project_task_overrides[override_key].get("start_date")
            end_date = st.session_state.project_task_overrides[override_key].get("end_date")
            
            corrected = False
            
            if start_date and is_weekend(start_date):
                new_start = get_next_weekday(start_date)
                st.session_state.project_task_overrides[override_key]["start_date"] = new_start
                corrections_made.append(f"**{task_name}** : Début {start_date.strftime('%d/%m')} → {new_start.strftime('%d/%m')}")
                corrected = True
            
            if end_date and is_weekend(end_date):
                new_end = get_previous_weekday(end_date)
                st.session_state.project_task_overrides[override_key]["end_date"] = new_end
                corrections_made.append(f"**{task_name}** : Fin {end_date.strftime('%d/%m')} → {new_end.strftime('%d/%m')}")
                corrected = True
    
    return corrections_made

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
        "version": "8.0",
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
    st.caption(f"Version 8.0 | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

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
    
    if weekday in [5, 6]:
        return "🔴 Pas de weekend"
    
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
        
        task_charge = get_task_charge_for_project(project_name, task["name"])
        task_depends = get_task_depends_for_project(project_name, task["name"])
        
        # Si dépendance, on FORCE le calcul automatique
        if task_depends:
            if task_depends in task_dates:
                _, parent_end_date = task_dates[task_depends]
                start_date = parent_end_date + timedelta(days=1)
                # S'assurer que c'est un jour ouvrable
                start_date = pd.to_datetime(get_next_weekday(start_date.date()))
            else:
                start_date = first_iter_start
            
            end_date = start_date + timedelta(days=task_charge)
        # Si dates manuelles ET pas de dépendance, on les utilise
        elif manual_start and manual_end:
            start_date = pd.to_datetime(manual_start)
            end_date = pd.to_datetime(manual_end)
        else:
            start_date = first_iter_start
            end_date = start_date + timedelta(days=task_charge)
        
        task_dates[task["name"]] = (start_date, end_date)
    
    for custom_task_name in st.session_state.projects_tasks.get(project_name, {}).get("custom", []):
        if custom_task_name in st.session_state.custom_tasks:
            custom_task = st.session_state.custom_tasks[custom_task_name]
            
            manual_start, manual_end = get_task_manual_dates(project_name, custom_task_name)
            task_depends = custom_task.get("depends_on")
            
            # Même logique pour les tâches custom
            if task_depends:
                if task_depends in task_dates:
                    _, parent_end_date = task_dates[task_depends]
                    start_date = parent_end_date + timedelta(days=1)
                    start_date = pd.to_datetime(get_next_weekday(start_date.date()))
                else:
                    start_date = pd.to_datetime(ITERATIONS[0]["start"])
                
                end_date = start_date + timedelta(days=custom_task.get("charge", 1))
            elif manual_start and manual_end:
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

def create_gantt_chart(df_gantt, title="Gantt Chart"):
    """Crée un Gantt chart uniformisé (utilisé partout)"""
    if df_gantt.empty:
        return None
    
    # Créer le graphique avec px.timeline
    fig = px.timeline(
        df_gantt, 
        x_start="Start Date", 
        x_end="End Date", 
        y="Tâche",
        color="Équipe",
        color_discrete_map=TEAM_COLORS,
        hover_data=["Équipe", "Charge", "Dépendance"],
        title=title,
        height=max(600, len(df_gantt) * 40)
    )
    
    # Bandes de couleur pour les itérations
    colors_bg = ["rgba(230, 230, 230, 0.3)", "rgba(200, 230, 255, 0.3)", "rgba(220, 255, 220, 0.3)", "rgba(255, 220, 220, 0.3)", "rgba(220, 255, 255, 0.3)"]
    for i, it in enumerate(ITERATIONS):
        fig.add_vrect(
            x0=it["start"], x1=it["end"],
            fillcolor=colors_bg[i % len(colors_bg)], 
            layer="below", line_width=0,
            annotation_text=f"<b>{it['name']}</b>", 
            annotation_position="top left",
            annotation_font
