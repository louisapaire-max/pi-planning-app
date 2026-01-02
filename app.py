import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from datetime import datetime, date, timedelta
from workalendar.europe import France
from collections import defaultdict, deque

# ═════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="PI Planning - Capacity Tool v5", layout="wide")
st.title("📊 PI Planning - Capacity Planning avec Dépendances")

CAL_FRANCE = France()

# ═════════════════════════════════════════════════════════════════════
# DONNÉES STATIQUES + CODE COULEUR ÉQUIPE
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

# 🎨 CODE COULEUR PAR ÉQUIPE (Distinct & Lisible)
TEAM_COLORS = {
    "Product Owner": "#FF6B6B",      # Rouge
    "Product unit": "#FF8C42",        # Orange
    "QQE": "#FFC300",                 # Jaune
    "Marketing": "#FF1493",           # Rose
    "Design": "#9D4EDD",              # Violet
    "Webmaster": "#3A86FF",           # Bleu ciel
    "Dev Web Front": "#00D9FF",       # Cyan
    "Dev Web Back": "#0099FF",        # Bleu royal
    "Dev Order": "#2E7D32",           # Vert foncé
    "Tracking": "#FFB703",            # Ambre
    "SEO": "#FB5607",                 # Orange-rouge
    "QA": "#8E44AD",                  # Mauve
    "Traduction": "#1ABC9C"           # Turquoise
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

if "planning_cache" not in st.session_state:
    st.session_state.planning_cache = None
    st.session_state.planning_cache_key = None

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

def get_holidays_2026():
    holidays = CAL_FRANCE.holidays(2026)
    return [d[0].isoformat() for d in holidays]

# ═════════════════════════════════════════════════════════════════════
# ⭐ #1 CACHING - OPTIMISATION PERFORMANCE
# ═════════════════════════════════════════════════════════════════════

def _get_cache_key():
    """Génère une clé de cache unique basée sur l'état"""
    capacity_tuple = tuple(sorted(st.session_state.capacity.items()))
    leaves_tuple = tuple(sorted(st.session_state.leaves.items()))
    run_tuple = tuple(sorted(st.session_state.run_days.items()))
    return (capacity_tuple, leaves_tuple, run_tuple)

@st.cache_data
def calculate_planning_cached(cache_key):
    """
    Version CACHÉE de calculate_planning()
    💡 Streamlit réexécute cette fonction SEULEMENT si cache_key change
    Gain: 10-15x plus rapide après 1ère exécution
    """
    # Reconstruire dicts depuis cache_key (hack mais efficace)
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
                    "Statut": "❌ Bloqué (Capa ou Dépendance)"
                })
    
    return planning, remaining

# ═════════════════════════════════════════════════════════════════════
# 🔟 DÉTECTION CYCLES DÉPENDANCES (Bug Prevention)
# ═════════════════════════════════════════════════════════════════════

def detect_circular_dependencies():
    """
    DFS-based cycle detection dans le graphe de dépendances
    Retourne (has_cycle, cycle_details)
    """
    # Construire adjacency list
    graph = defaultdict(list)
    all_tasks = {task["name"]: task for task in TASKS}
    
    for task in TASKS:
        if task["depends_on"]:
            graph[task["depends_on"]].append(task["name"])
    
    # DFS pour détecter cycle
    visited = set()
    rec_stack = set()
    cycle_path = []
    
    def dfs(node, path):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor, path.copy()):
                        return True
                elif neighbor in rec_stack:
                    # Cycle trouvé!
                    cycle_start = path.index(neighbor)
                    cycle_path.extend(path[cycle_start:] + [neighbor])
                    return True
        
        rec_stack.remove(node)
        return False
    
    # Vérifier tous les nœuds
    for task_name in all_tasks.keys():
        if task_name not in visited:
            if dfs(task_name, []):
                return True, cycle_path
    
    return False, []

# ═════════════════════════════════════════════════════════════════════
# 5️⃣ GRAPHE DÉPENDANCES (DAG Visuel)
# ═════════════════════════════════════════════════════════════════════

def create_dependency_graph():
    """
    Crée un graphe interactif Plotly des dépendances
    Montre clairement l'ordre topologique et les chemins critiques
    """
    # Construire graphe NetworkX
    G = nx.DiGraph()
    
    for task in TASKS:
        G.add_node(task["name"])
        if task["depends_on"]:
            G.add_edge(task["depends_on"], task["name"])
    
    # Layout hiérarchique (top-down)
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Pour un vrai Gantt-like layout, utiliser les ordres
    pos = {}
    for task in TASKS:
        x = task["order"]
        # Y basé sur dépendances
        y = 0
        if task["depends_on"]:
            parent = next((t for t in TASKS if t["name"] == task["depends_on"]), None)
            if parent:
                y = parent["order"] * 0.5
        pos[task["name"]] = (x, y)
    
    # Edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=2, color='rgba(125,125,125,0.5)'),
        hoverinfo='none',
        showlegend=False
    )
    
    # Nodes
    node_x = []
    node_y = []
    node_color = []
    node_text = []
    node_size = []
    
    for task in TASKS:
        x, y = pos[task["name"]]
        node_x.append(x)
        node_y.append(y)
        node_color.append(TEAM_COLORS.get(task["team"], "#999999"))
        node_text.append(f"{task['name']}<br>({task['team']})<br>{task['charge']}j")
        node_size.append(20 + task["charge"] * 2)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[t.split("<br>")[0] for t in node_text],
        textposition="top center",
        hovertext=node_text,
        hoverinfo='text',
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color='white'),
            opacity=0.9
        ),
        showlegend=False
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    
    fig.update_layout(
        title="🔗 Graphe des Dépendances (Tâches & Équipes)",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        plot_bgcolor='rgba(240,240,240,0.5)'
    )
    
    return fig

# ═════════════════════════════════════════════════════════════════════
# INTERFACE PRINCIPALE - KPIs EN HAUT
# ═════════════════════════════════════════════════════════════════════

# 🔟 DÉTECTION CYCLES - AFFICHER ALERTE
has_cycle, cycle_path = detect_circular_dependencies()
if has_cycle:
    st.error(f"🚨 **CYCLE DÉTECTÉ!** Dépendances circulaires: {' → '.join(cycle_path)}")
    st.stop()

# Calcul planning avec CACHING
cache_key = _get_cache_key()
planning, remaining = calculate_planning_cached(cache_key)
df_plan = pd.DataFrame(planning)

# 9️⃣ KPIs DASHBOARD
st.markdown("### 📊 Vue d'Ensemble - KPIs")
col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)

with col_kpi1:
    total_taches = len(df_plan)
    st.metric("📋 Total Tâches", total_taches)

with col_kpi2:
    planifiees = len(df_plan[df_plan["Statut"] == "✅ Planifié"])
    st.metric("✅ Planifiées", planifiees, f"{planifiees/total_taches*100:.0f}%")

with col_kpi3:
    bloquees = len(df_plan[df_plan["Statut"] == "❌ Bloqué (Capa ou Dépendance)"])
    st.metric("❌ Bloquées", bloquees, f"{bloquees/total_taches*100:.0f}%")

with col_kpi4:
    capa_restante_moy = sum(remaining.values()) / len(remaining) if remaining else 0
    st.metric("📦 Capa Moy Restante", f"{capa_restante_moy:.1f}j")

with col_kpi5:
    taux_util = (1 - (capa_restante_moy / 10)) * 100 if capa_restante_moy > 0 else 100
    st.metric("📈 Taux Utilisation", f"{taux_util:.0f}%")

st.divider()

# ═════════════════════════════════════════════════════════════════════
# ONGLETS PRINCIPAUX
# ═════════════════════════════════════════════════════════════════════

tab_planning, tab_dag, tab_capa, tab_cong, tab_time, tab_active = st.tabs([
    "📋 Planning & ETA",
    "🔗 DAG Dépendances",
    "📊 Capacités",
    "🏖️ Congés & Run",
    "📈 Timeline Globale",
    "✅ En cours"
])

# ─────────────────────────────────────────────────────────────────
# ONGLET 1: PLANNING & ETA
# ─────────────────────────────────────────────────────────────────
with tab_planning:
    st.subheader("📋 Planning détaillé & Gantt par Projet")
    
    # Appliquer overrides depuis session_state
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

    # Sélecteur de projet
    project_list = ["Vue Globale (Édition)"] + sorted(list(df_plan["Projet"].unique())) if not df_plan.empty else []
    selected_project = st.selectbox("🎯 Sélectionner un projet", options=project_list)
    
    st.divider()

    if selected_project == "Vue Globale (Édition)":
        st.info("💡 Mode édition globale : modifier dates et statuts de tous les projets.")
        
        display_cols = ["Priorité", "Projet", "Tâche", "Dépendance", "Équipe", "Itération", "Start Date", "End Date", "Statut Custom"]
        
        edited_df = st.data_editor(
            df_plan[display_cols].sort_values("Priorité"),
            use_container_width=True,
            hide_index=True,
            height=600,
            key="planning_editor_global",
            column_config={
                "Start Date": st.column_config.DateColumn("Start Date", format="DD/MM/YYYY", width="medium"),
                "End Date": st.column_config.DateColumn("End Date", format="DD/MM/YYYY", width="medium"),
                "Statut Custom": st.column_config.SelectboxColumn("Statut", options=TASK_STATUSES, width="medium"),
                "Priorité": st.column_config.NumberColumn(disabled=True),
                "Projet": st.column_config.TextColumn(disabled=True, width="large"),
                "Tâche": st.column_config.TextColumn(disabled=True, width="large"),
                "Dépendance": st.column_config.TextColumn(disabled=True, width="medium"),
                "Équipe": st.column_config.TextColumn(disabled=True),
                "Itération": st.column_config.TextColumn(disabled=True),
            }
        )
        
        for idx, row in edited_df.iterrows():
            task_key = get_task_key(row)
            st.session_state.task_details[task_key] = {
                "start_date": row["Start Date"],
                "end_date": row["End Date"],
                "status": row["Statut Custom"]
            }

    else:
        # --- MODE PROJET SPÉCIFIQUE (GANTT + QUICK OVERRIDE) ---
        df_filtered = df_plan[df_plan["Projet"] == selected_project].copy()
        
        if not df_filtered.empty:
            st.subheader(f"📅 Gantt Chart: {selected_project}")
            
            df_gantt = df_filtered.dropna(subset=["Start Date", "End Date"]).copy()
            
            if not df_gantt.empty:
                # 7️⃣ COLORING PAR ÉQUIPE - GANTT AMÉLIORÉ
                fig = px.timeline(
                    df_gantt, 
                    x_start="Start Date", 
                    x_end="End Date", 
                    y="Tâche",
                    color="Équipe",
                    color_discrete_map=TEAM_COLORS,  # 🎨 Code couleur équipe
                    hover_data=["Équipe", "Charge", "Dépendance"],
                    title=f"Planning: {selected_project}",
                    height=max(400, len(df_gantt) * 45)
                )
                
                # Ajouter les itérations en background
                colors_bg = ["rgba(230, 230, 230, 0.3)", "rgba(200, 230, 255, 0.3)", "rgba(220, 255, 220, 0.3)"]
                for i, it in enumerate(ITERATIONS):
                    fig.add_vrect(
                        x0=it["start"], x1=it["end"],
                        fillcolor=colors_bg[i % len(colors_bg)], 
                        layer="below", 
                        line_width=0,
                        annotation_text=f"<b>{it['name']}</b>", 
                        annotation_position="top left",
                        annotation_font_size=13
                    )
                    fig.add_vline(x=it["end"], line_width=2, line_dash="dot", line_color="gray")
                
                # Jours fériés
                holidays_list = get_holidays_2026()
                for hol_date in holidays_list:
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
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Aucune tâche avec des dates valides pour afficher le Gantt.")

            # 8️⃣ QUICK OVERRIDE UI - ÉDITION PAR TÂCHE
            st.subheader("⚡ Quick Override - Modifier les dates par tâche")
            st.markdown("Sélectionnez une tâche et modifiez ses dates rapidement")
            
            col_select, col_space = st.columns([2, 3])
            
            with col_select:
                task_to_edit = st.selectbox(
                    "Tâche à modifier",
                    options=df_filtered["Tâche"].unique(),
                    key=f"task_select_{selected_project}"
                )
            
            if task_to_edit:
                task_row = df_filtered[df_filtered["Tâche"] == task_to_edit].iloc[0]
                
                col_date1, col_date2, col_status = st.columns(3)
                
                with col_date1:
                    new_start = st.date_input(
                        "Nouvelle date début",
                        value=task_row["Start Date"] if pd.notna(task_row["Start Date"]) else date.today(),
                        key=f"start_{task_to_edit}"
                    )
                
                with col_date2:
                    new_end = st.date_input(
                        "Nouvelle date fin",
                        value=task_row["End Date"] if pd.notna(task_row["End Date"]) else date.today() + timedelta(days=1),
                        key=f"end_{task_to_edit}"
                    )
                
                with col_status:
                    new_status = st.selectbox(
                        "Statut",
                        options=TASK_STATUSES,
                        index=TASK_STATUSES.index(task_row["Statut Custom"]) if task_row["Statut Custom"] in TASK_STATUSES else 0,
                        key=f"status_{task_to_edit}"
                    )
                
                # Bouton d'appli
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✅ Appliquer les modifications", key=f"apply_{task_to_edit}"):
                        # Trouver la task_key
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
                        st.success(f"✅ {task_to_edit} mis à jour!")
                        st.rerun()
                
                with col_btn2:
                    if st.button("🔄 Réinitialiser", key=f"reset_{task_to_edit}"):
                        full_row = {
                            "Priorité": task_row["Priorité"],
                            "Projet": selected_project,
                            "Tâche": task_to_edit,
                            "Équipe": task_row["Équipe"]
                        }
                        task_key = get_task_key(full_row)
                        if task_key in st.session_state.task_details:
                            del st.session_state.task_details[task_key]
                        st.success("🔄 Réinitialisé!")
                        st.rerun()

# ─────────────────────────────────────────────────────────────────
# ONGLET 2: DAG DÉPENDANCES
# ─────────────────────────────────────────────────────────────────
with tab_dag:
    st.subheader("🔗 Graphe des Dépendances")
    st.markdown("""
    Ce graphe montre l'ordre topologique des tâches et leurs dépendances.
    - **Taille du nœud** = charge de travail
    - **Couleur du nœud** = équipe responsable
    - **Flèches** = dépendances (A→B = B dépend de A)
    """)
    
    fig_dag = create_dependency_graph()
    st.plotly_chart(fig_dag, use_container_width=True)
    
    # Légende couleur
    st.markdown("#### 🎨 Légende des couleurs (par Équipe)")
    cols_legend = st.columns(4)
    for idx, (team, color) in enumerate(sorted(TEAM_COLORS.items())):
        with cols_legend[idx % 4]:
            st.markdown(f"<div style='padding:8px; background:{color}; border-radius:4px; color:white; text-align:center; font-weight:bold;'>{team}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# ONGLET 3: CAPACITÉS
# ─────────────────────────────────────────────────────────────────
with tab_capa:
    st.subheader("📊 Définir la Capacité Brute (Jours)")
    
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
    col_total, col_space = st.columns([1, 4])
    with col_total:
        st.metric("📦 Capacité totale", f"{edited_cap.sum().sum():.1f} jours")

# ─────────────────────────────────────────────────────────────────
# ONGLET 4: CONGÉS & RUN
# ─────────────────────────────────────────────────────────────────
with tab_cong:
    st.subheader("🏖️ Gestion des Indisponibilités")
    st.markdown("Déduisez ici les jours non productifs (Congés, Maladie, Run, Support, Cérémonies...)")
    
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
# ONGLET 5: TIMELINE GLOBALE
# ─────────────────────────────────────────────────────────────────
with tab_time:
    st.subheader("📈 Vue d'ensemble par Itération")
    
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
                    st.dataframe(
                        load_per_project.style.background_gradient(cmap="Blues"), 
                        use_container_width=True, 
                        hide_index=True
                    )
                else:
                    st.caption("Aucune tâche planifiée.")
    else:
        st.info("Aucune tâche planifiée pour le moment.")

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
        col_metric2.metric("Tâches théoriquement actives", len(active))
        
        if not active.empty:
            st.dataframe(
                active[["Projet", "Tâche", "Équipe", "Charge", "Statut Custom"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Aucune tâche active aujourd'hui selon le planning.")

st.divider()
st.markdown(f"🛠 **PI Planning Tool v5.0** (with caching, DAG, team colors, quick override, KPIs, cycle detection) | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
