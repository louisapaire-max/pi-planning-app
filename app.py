import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from workalendar.europe import France
import json

st.set_page_config(page_title="PI Planning - Capacity Tool", layout="wide")
st.title("📊 PI Planning - Advanced Capacity Planning")

# Color palette for teams
TEAM_COLORS = {
    "Product Owner": "#FF6B6B",
    "Product unit": "#4ECDC4",
    "QQE": "#45B7D1",
    "Marketing": "#FFA07A",
    "Design": "#98D8C8",
    "Webmaster": "#F7DC6F",
    "Dev Web Front": "#BB8FCE",
    "Dev Web Back": "#85C1E2",
    "Dev Order": "#F8B88B",
    "Tracking": "#82E0AA",
    "SEO": "#F1948A",
    "QA": "#AED6F1",
    "Traduction": "#D7BDE2"
}

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
    {"name": "Brief requester Delivery", "team": "Product Owner", "order": 1, "charge": 1, "dependencies": []},
    {"name": "Catalogue Delivery", "team": "Product unit", "order": 2, "charge": 2, "dependencies": []},
    {"name": "Control d'interface", "team": "QQE", "order": 3, "charge": 1, "dependencies": ["Brief requester Delivery"]},
    {"name": "Content", "team": "Marketing", "order": 4, "charge": 2, "dependencies": ["Brief requester Delivery"]},
    {"name": "Documentation Project", "team": "Product Owner", "order": 5, "charge": 1, "dependencies": ["Brief requester Delivery"]},
    {"name": "Kick-off Digital", "team": "Product Owner", "order": 6, "charge": 0.5, "dependencies": []},
    {"name": "Etude d'impact", "team": "Product Owner", "order": 7, "charge": 2, "dependencies": ["Brief requester Delivery"]},
    {"name": "Maquettes/Wireframe", "team": "Design", "order": 8, "charge": 3, "dependencies": ["Brief requester Delivery", "Content"]},
    {"name": "Redaction US / Jira", "team": "Product Owner", "order": 9, "charge": 2, "dependencies": ["Maquettes/Wireframe"]},
    {"name": "Refinement", "team": "Product Owner", "order": 10, "charge": 1, "dependencies": ["Redaction US / Jira"]},
    {"name": "Integration OCMS", "team": "Webmaster", "order": 11, "charge": 2, "dependencies": ["Maquettes/Wireframe"]},
    {"name": "Dev Website Front", "team": "Dev Web Front", "order": 12, "charge": 5, "dependencies": ["Refinement", "Maquettes/Wireframe"]},
    {"name": "Dev Website Back", "team": "Dev Web Back", "order": 13, "charge": 5, "dependencies": ["Refinement"]},
    {"name": "Dev Order", "team": "Dev Order", "order": 14, "charge": 3, "dependencies": ["Dev Website Back"]},
    {"name": "Tracking", "team": "Tracking", "order": 15, "charge": 2, "dependencies": ["Dev Website Front", "Dev Website Back"]},
    {"name": "check SEO", "team": "SEO", "order": 16, "charge": 1, "dependencies": ["Dev Website Front"]},
    {"name": "QA & UAT (langue source)", "team": "QA", "order": 17, "charge": 3, "dependencies": ["Dev Website Front", "Dev Website Back", "Dev Order"]},
    {"name": "Traduction", "team": "Traduction", "order": 18, "charge": 2, "dependencies": ["QA & UAT (langue source)"]},
    {"name": "QA WW", "team": "QA", "order": 19, "charge": 2, "dependencies": ["Traduction"]},
    {"name": "Plan de Production", "team": "Product Owner", "order": 20, "charge": 1, "dependencies": ["QA WW"]},
    {"name": "PROD", "team": "Product Owner", "order": 21, "charge": 1, "dependencies": ["Plan de Production"]}
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

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "light"

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
                        "Statut": "✅ Planifié",
                        "Dependencies": task.get("dependencies", [])
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
                    "Statut": "❌ Bloqué",
                    "Dependencies": task.get("dependencies", [])
                })
    
    return planning, remaining

def get_task_key(row):
    """Génère une clé unique pour une tâche"""
    return f"{row['Priorité']}_{row['Projet']}_{row['Tâche']}_{row['Équipe']}"

def create_gantt_chart(df_plan):
    """Crée un Gantt chart interactif avec Plotly"""
    df_gantt = df_plan[df_plan["Statut"] == "✅ Planifié"].copy()
    
    if df_gantt.empty:
        return None
    
    df_gantt["Start"] = pd.to_datetime(df_gantt["Début"])
    df_gantt["End"] = pd.to_datetime(df_gantt["Fin"])
    df_gantt["Duration"] = (df_gantt["End"] - df_gantt["Start"]).dt.days
    
    fig = go.Figure()
    
    for team in df_gantt["Équipe"].unique():
        team_data = df_gantt[df_gantt["Équipe"] == team]
        
        for _, row in team_data.iterrows():
            fig.add_trace(go.Bar(
                y=[row["Équipe"]],
                x=[row["Duration"]],
                base=row["Start"],
                name=row["Tâche"],
                marker=dict(color=TEAM_COLORS.get(team, "#808080")),
                customdata=[f"{row['Projet']}<br>{row['Tâche']}<br>Charge: {row['Charge']}j"],
                hovertemplate="<b>%{customdata}</b><br>%{x} jours<extra></extra>",
                orientation="h",
                showlegend=False,
            ))
    
    fig.update_layout(
        title="📊 Gantt Chart du Planning",
        barmode="overlay",
        height=600,
        xaxis_title="Timeline",
        yaxis_title="Équipes",
        hovermode="closest",
        template="plotly_white",
        font=dict(size=11)
    )
    
    return fig

def detect_dependencies_issues(planning):
    """Détecte les problèmes de dépendances"""
    issues = []
    task_iterations = {}
    
    # Créer un mapping task -> itération
    for item in planning:
        task_iterations[item["Tâche"]] = item["Itération"]
    
    # Vérifier chaque tâche et ses dépendances
    for item in planning:
        if item["Dependencies"]:
            current_iter = ITERATIONS.index(next((it for it in ITERATIONS if it["name"] == item["Itération"]), None)) if item["Itération"] != "⚠️ Dépassement" else -1
            
            for dep in item["Dependencies"]:
                if dep in task_iterations:
                    dep_iter = ITERATIONS.index(next((it for it in ITERATIONS if it["name"] == task_iterations[dep]), None)) if task_iterations[dep] != "⚠️ Dépassement" else -1
                    
                    if dep_iter >= current_iter and current_iter != -1:
                        issues.append({
                            "type": "⚠️ Chaîne de dépendance cassée",
                            "task": item["Tâche"],
                            "dependency": dep,
                            "severity": "HIGH"
                        })
    
    return issues

def optimize_team_allocation(planning, remaining):
    """Propose des optimisations d'assignation"""
    suggestions = []
    
    blocked_tasks = [p for p in planning if p["Statut"] == "❌ Bloqué"]
    
    for blocked in blocked_tasks:
        team = blocked["Équipe"]
        charge = blocked["Charge"]
        
        # Chercher une équipe alternative avec capacité
        for iteration in ITERATIONS:
            key = (team, iteration["name"])
            available = remaining.get(key, 0)
            
            if available >= charge:
                suggestions.append({
                    "task": blocked["Tâche"],
                    "current_team": team,
                    "available_iteration": iteration["name"],
                    "capacity": available,
                    "gain": "Débloque la tâche"
                })
                break
    
    return suggestions

# ═════════════════════════════════════════════════════════════════════
# SIDEBAR - FILTRES & CONTRÔLES
# ═════════════════════════════════════════════════════════════════════

st.sidebar.markdown("## 🎛️ Contrôles")

# View mode
st.session_state.view_mode = st.sidebar.radio(
    "🎨 Thème",
    ["light", "dark"],
    index=0
)

# Filtres
st.sidebar.markdown("### 🔍 Filtres")
selected_teams = st.sidebar.multiselect(
    "Équipes",
    TEAMS,
    default=TEAMS,
    key="filter_teams"
)

selected_statuses = st.sidebar.multiselect(
    "Statuts",
    TASK_STATUSES,
    default=["À faire", "En cours"],
    key="filter_statuses"
)

selected_iterations = st.sidebar.multiselect(
    "Itérations",
    [it["name"] for it in ITERATIONS],
    default=[it["name"] for it in ITERATIONS],
    key="filter_iterations"
)

# ═════════════════════════════════════════════════════════════════════
# ONGLETS PRINCIPAUX
# ═════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Capacités",
    "🏖️ Congés & Run",
    "📋 Planning & ETA",
    "📈 Gantt",
    "🔗 Dépendances",
    "✅ En cours"
])

# ═════════════════════════════════════════════════════════════════════
# TAB 1: CAPACITÉS
# ═════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("📊 Capacité brute par équipe")
    st.markdown("Saisissez la capacité totale disponible (en jours) pour chaque équipe par itération")
    
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
    avg_per_team = edited_cap.mean(axis=1).mean()
    max_team = edited_cap.sum(axis=1).idxmax()
    min_team = edited_cap.sum(axis=1).idxmin()
    
    with col1:
        st.metric("📦 Capacité totale", f"{total_cap:.0f}j")
    with col2:
        st.metric("👥 Moyenne/équipe", f"{avg_per_team:.1f}j")
    with col3:
        st.metric("🔥 Équipe max", f"{max_team[:20]}", f"{edited_cap.loc[max_team].sum():.1f}j")
    with col4:
        st.metric("📉 Équipe min", f"{min_team[:20]}", f"{edited_cap.loc[min_team].sum():.1f}j")

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
        edited_leave = st.data_editor(
            df_leave,
            use_container_width=True,
            key="leaves_editor",
            column_config={
                it["name"]: st.column_config.NumberColumn(
                    it["name"], min_value=0, max_value=20, step=0.5, format="%.1f j"
                ) for it in ITERATIONS
            }
        )
        
        for idx, team in enumerate(TEAMS):
            for jdx, it in enumerate(ITERATIONS):
                key = (team, it["name"])
                st.session_state.leaves[key] = edited_leave.iloc[idx, jdx]
    
    with col_run:
        st.markdown("#### Run Days (jours)")
        run_data = {}
        for team in TEAMS:
            run_data[team] = []
            for it in ITERATIONS:
                key = (team, it["name"])
                run_data[team].append(st.session_state.run_days[key])
        
        df_run = pd.DataFrame(run_data, index=[it["name"] for it in ITERATIONS]).T
        edited_run = st.data_editor(
            df_run,
            use_container_width=True,
            key="run_days_editor",
            column_config={
                it["name"]: st.column_config.NumberColumn(
                    it["name"], min_value=0, max_value=20, step=0.5, format="%.1f j"
                ) for it in ITERATIONS
            }
        )
        
        for idx, team in enumerate(TEAMS):
            for jdx, it in enumerate(ITERATIONS):
                key = (team, it["name"])
                st.session_state.run_days[key] = edited_run.iloc[idx, jdx]
    
    st.divider()
    
    st.markdown("#### 📊 Capacité nette (après déductions)")
    net_data = {}
    for team in TEAMS:
        net_data[team] = [get_net_capacity(team, it) for it in ITERATIONS]
    
    df_net = pd.DataFrame(net_data, index=[it["name"] for it in ITERATIONS]).T
    
    def highlight_low(val):
        if val < 2:
            return "background-color: #ffcccc"
        elif val < 5:
            return "background-color: #ffffcc"
        return ""
    
    st.dataframe(df_net.style.applymap(highlight_low), use_container_width=True)
    
    low_teams = df_net[(df_net < 5).any(axis=1)].index.tolist()
    if low_teams:
        st.warning(f"⚠️ **Équipes en capacité faible:** {', '.join(low_teams[:5])}")

# ═════════════════════════════════════════════════════════════════════
# TAB 3: PLANNING & ETA
# ═════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📋 Planning détaillé avec ETA")
    
    planning, remaining = calculate_planning()
    df_plan = pd.DataFrame(planning)
    
    # Appliquer les filtres
    df_plan_filtered = df_plan[
        (df_plan["Équipe"].isin(selected_teams)) &
        (df_plan["Itération"].isin(selected_iterations))
    ].copy()
    
    placed = df_plan_filtered[df_plan_filtered["Statut"] == "✅ Planifié"]
    blocked = df_plan_filtered[df_plan_filtered["Statut"] == "❌ Bloqué"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("✅ Tâches planifiées", len(placed))
    with col2:
        st.metric("❌ Tâches bloquées", len(blocked))
    with col3:
        st.metric("📦 Charge planifiée", f"{placed['Charge'].sum():.1f}j")
    with col4:
        coverage = (len(placed) / len(df_plan_filtered) * 100) if len(df_plan_filtered) > 0 else 0
        st.metric("📊 Couverture", f"{coverage:.0f}%")
    
    st.divider()
    
    st.markdown("**Détail du planning (modifiable)**")
    st.info("💡 Vous pouvez éditer les dates de début/fin et le statut pour chaque tâche")
    
    # Créer une copie du dataframe avec colonnes additionnelles
    df_editable = df_plan_filtered.copy()
    
    # Ajouter les colonnes de dates et statut
    df_editable["Start Date"] = df_editable.apply(
        lambda row: st.session_state.task_details.get(get_task_key(row), {}).get("start_date", row["Début"]),
        axis=1
    )
    df_editable["End Date"] = df_editable.apply(
        lambda row: st.session_state.task_details.get(get_task_key(row), {}).get("end_date", row["Fin"]),
        axis=1
    )
    df_editable["Statut Custom"] = df_editable.apply(
        lambda row: st.session_state.task_details.get(get_task_key(row), {}).get("status", "À faire"),
        axis=1
    )
    
    # Colonnes à afficher
    display_cols = ["Priorité", "Projet", "Tâche", "Équipe", "Itération", "Charge", "Start Date", "End Date", "Statut Custom"]
    
    # Editor avec colonnes modifiables
    edited_df = st.data_editor(
        df_editable[display_cols].sort_values("Priorité"),
        use_container_width=True,
        hide_index=True,
        height=500,
        key="planning_editor",
        column_config={
            "Start Date": st.column_config.DateColumn(
                "Start Date",
                format="DD/MM/YYYY",
                width="medium"
            ),
            "End Date": st.column_config.DateColumn(
                "End Date",
                format="DD/MM/YYYY",
                width="medium"
            ),
            "Statut Custom": st.column_config.SelectboxColumn(
                "Statut",
                options=TASK_STATUSES,
                width="medium"
            ),
            "Priorité": st.column_config.NumberColumn(disabled=True),
            "Projet": st.column_config.TextColumn(disabled=True, width="large"),
            "Tâche": st.column_config.TextColumn(disabled=True, width="large"),
            "Équipe": st.column_config.TextColumn(disabled=True),
            "Itération": st.column_config.TextColumn(disabled=True),
            "Charge": st.column_config.NumberColumn(disabled=True),
        }
    )
    
    # Sauvegarder les modifications
    for idx, row in edited_df.iterrows():
        task_key = f"{row['Priorité']}_{row['Projet']}_{row['Tâche']}_{row['Équipe']}"
        st.session_state.task_details[task_key] = {
            "start_date": row["Start Date"],
            "end_date": row["End Date"],
            "status": row["Statut Custom"]
        }
    
    st.divider()
    
    # Afficher les tâches bloquées
    if not blocked.empty:
        st.warning(f"⚠️ **{len(blocked)} tâches en dépassement de capacité**")
        st.dataframe(
            blocked[["Priorité", "Projet", "Tâche", "Équipe", "Charge"]].sort_values("Priorité"),
            use_container_width=True,
            hide_index=True
        )
    
    st.divider()
    
    st.markdown("**📉 Capacité restante après planification**")
    remaining_data = {}
    for team in TEAMS:
        remaining_data[team] = [remaining[(team, it["name"])] for it in ITERATIONS]
    
    df_remaining = pd.DataFrame(remaining_data, index=[it["name"] for it in ITERATIONS]).T
    
    def highlight_low(val):
        if val < 2:
            return "background-color: #ffcccc"
        elif val < 5:
            return "background-color: #ffffcc"
        return ""
    
    st.dataframe(df_remaining.style.applymap(highlight_low), use_container_width=True)

# ═════════════════════════════════════════════════════════════════════
# TAB 4: GANTT INTERACTIF
# ═════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📈 Gantt Chart Interactif")
    st.info("📅 Visualisation dynamique avec timeline et dépendances")
    
    gantt_fig = create_gantt_chart(df_plan_filtered)
    
    if gantt_fig:
        st.plotly_chart(gantt_fig, use_container_width=True)
    else:
        st.warning("❌ Aucune tâche planifiée à afficher")

# ═════════════════════════════════════════════════════════════════════
# TAB 5: GESTION DÉPENDANCES & AUTO-ASSIGNATION
# ═════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("🔗 Gestion des Dépendances & Auto-Assignation")
    
    col_dep, col_opt = st.columns(2)
    
    with col_dep:
        st.markdown("### 🔗 Chaîne de Dépendances")
        
        # Détection des problèmes
        dependency_issues = detect_dependencies_issues(planning)
        
        if dependency_issues:
            st.error(f"⚠️ **{len(dependency_issues)} problèmes détectés**")
            for issue in dependency_issues:
                st.error(f"- {issue['task']} dépend de {issue['dependency']} (chronologie inversée)")
        else:
            st.success("✅ Toutes les dépendances sont respectées!")
        
        st.divider()
        
        # Afficher le graphe de dépendances
        st.markdown("#### 📊 Chaîne critique:")
        for task in TASKS:
            if task.get("dependencies"):
                deps_str = ", ".join(task["dependencies"])
                st.write(f"📌 **{task['name']}** ← {deps_str}")
    
    with col_opt:
        st.markdown("### 🤖 Optimisation Intelligente")
        
        # Suggestions d'assignation
        suggestions = optimize_team_allocation(planning, remaining)
        
        if suggestions:
            st.warning(f"💡 **{len(suggestions)} opportunités d'optimisation**")
            
            for idx, suggestion in enumerate(suggestions, 1):
                with st.expander(f"💡 Opportunité {idx}: {suggestion['task']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Tâche", suggestion['task'][:30])
                    with col_b:
                        st.metric("Itération disponible", suggestion['available_iteration'])
                    
                    st.info(f"🎯 {suggestion['gain']}")
                    
                    if st.button(f"✅ Appliquer", key=f"apply_{idx}"):
                        st.success(f"✅ {suggestion['task']} optimisée!")
        else:
            st.success("✅ Aucune opportunité d'optimisation - Planning optimal!")

# ═════════════════════════════════════════════════════════════════════
# TAB 6: EN COURS
# ═════════════════════════════════════════════════════════════════════
with tab6:
    st.subheader("✅ Suivi des tâches actives")
    
    planning, _ = calculate_planning()
    
    if planning:
        df_plan = pd.DataFrame(planning)
        today = pd.Timestamp.now().normalize()
        
        df_plan["start_dt"] = pd.to_datetime(df_plan["Début"], errors='coerce')
        df_plan["end_dt"] = pd.to_datetime(df_plan["Fin"], errors='coerce')
        
        active = df_plan[
            (df_plan["start_dt"].notna()) &
            (df_plan["end_dt"].notna()) &
            (df_plan["start_dt"] <= today) &
            (df_plan["end_dt"] >= today)
        ]
        
        upcoming = df_plan[
            (df_plan["start_dt"] > today) &
            (df_plan["start_dt"] <= today + pd.Timedelta(days=7))
        ]
        
        if not active.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("⏳ Tâches actives", len(active))
            with col2:
                st.metric("👥 Équipes", active["Équipe"].nunique())
            with col3:
                st.metric("🎯 Projets", active["Projet"].nunique())
            with col4:
                st.metric("📦 Charge/jour", f"{active['Charge'].sum():.1f}j")
            
            st.divider()
            st.markdown("**Tâches actives aujourd'hui**")
            display_cols = ["Priorité", "Projet", "Tâche", "Équipe", "Début", "Fin", "Charge"]
            st.dataframe(
                active[display_cols].sort_values("Priorité"),
                use_container_width=True,
                hide_index=True,
                height=300
            )
        else:
            st.info("ℹ️ Aucune tâche active pour aujourd'hui")
        
        st.divider()
        
        if not upcoming.empty:
            st.markdown("### 🔜 Prochaines tâches (7 jours)")
            st.dataframe(
                upcoming[["Début", "Projet", "Tâche", "Équipe", "Charge"]].sort_values("Début"),
                use_container_width=True,
                hide_index=True,
                height=300
            )
        else:
            st.info("Aucune tâche prévue dans les 7 prochains jours")

# ═════════════════════════════════════════════════════════════════════
# FOOTER
# ═════════════════════════════════════════════════════════════════════
st.divider()

col_footer_1, col_footer_2, col_footer_3 = st.columns(3)

with col_footer_1:
    if st.button("📥 Exporter JSON"):
        json_str = json.dumps(st.session_state.task_details, indent=2, default=str)
        st.download_button(
            label="Télécharger JSON",
            data=json_str,
            file_name="planning_export.json",
            mime="application/json"
        )

with col_footer_2:
    if st.button("📊 Exporter Excel"):
        df_export = df_plan[["Priorité", "Projet", "Tâche", "Équipe", "Itération", "Charge"]].sort_values("Priorité")
        csv = df_export.to_csv(index=False)
        st.download_button(
            label="Télécharger CSV",
            data=csv,
            file_name="planning_export.csv",
            mime="text/csv"
        )

with col_footer_3:
    st.write("")

st.markdown(f"🛠 **PI Planning Tool v3.0** | Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
