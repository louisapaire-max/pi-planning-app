import streamlit as st
import pandas as pd
from datetime import datetime
from workalendar.europe import France

st.set_page_config(page_title="PI Planning - Capacity Tool", layout="wide")
st.title("📊 PI Planning - Capacity Planning avec ETA")

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
    "📈 Timeline",
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
    
    placed = df_plan[df_plan["Statut"] == "✅ Planifié"]
    blocked = df_plan[df_plan["Statut"] == "❌ Bloqué"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("✅ Tâches planifiées", len(placed))
    with col2:
        st.metric("❌ Tâches bloquées", len(blocked))
    with col3:
        st.metric("📦 Charge planifiée", f"{placed['Charge'].sum():.1f}j")
    with col4:
        coverage = (len(placed) / len(df_plan) * 100) if len(df_plan) > 0 else 0
        st.metric("📊 Couverture", f"{coverage:.0f}%")
    
    st.divider()
    
    st.markdown("**Détail du planning**")
    display_cols = ["Priorité", "Projet", "Tâche", "Équipe", "Itération", "Charge", "Statut"]
    st.dataframe(
        df_plan[display_cols].sort_values("Priorité"),
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    if not blocked.empty:
        st.divider()
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
    st.dataframe(df_remaining.style.applymap(highlight_low), use_container_width=True)

# ═════════════════════════════════════════════════════════════════════
# TAB 4: TIMELINE
# ═════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📈 Timeline du planning")
    st.info("📅 Visualisation simple des tâches planifiées par équipe et itération")
    
    planning, _ = calculate_planning()
    df_gantt = pd.DataFrame([p for p in planning if p["Statut"] == "✅ Planifié"])
    
    if not df_gantt.empty:
        st.markdown("**Tâches par itération:**")
        for it in ITERATIONS:
            st.markdown(f"#### {it['name']} ({it['start']} → {it['end']})")
            
            tasks_it = df_gantt[df_gantt["Itération"] == it["name"]]
            if not tasks_it.empty:
                display = tasks_it[["Équipe", "Projet", "Tâche", "Charge"]].sort_values("Équipe")
                st.dataframe(display, use_container_width=True, hide_index=True, height=200)
            else:
                st.markdown("_Aucune tâche planifiée_")
    else:
        st.info("Aucune tâche planifiée à afficher")

# ═════════════════════════════════════════════════════════════════════
# TAB 5: EN COURS
# ═════════════════════════════════════════════════════════════════════
with tab5:
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

st.divider()
st.markdown(f"🛠 **PI Planning Tool v2.3** | Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
