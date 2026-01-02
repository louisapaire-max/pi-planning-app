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
    
    # Sélecteur de projet
    selected_proj = st.selectbox("📂 Sélectionner un projet", options=[p["name"] for p in PROJECTS], key="project_selector")
    
    if selected_proj:
        st.markdown(f"#### Projet: **{selected_proj}**")
        st.divider()
        
        all_project_tasks = get_all_tasks_for_project(selected_proj)
        task_dates_dict = calculate_dates_for_project(selected_proj)
        
        # GANTT EN HAUT
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
            fig_gantt = create_gantt_chart_project(df_project_gantt, title=f"📅 Gantt: {selected_proj}")
            if fig_gantt:
                st.plotly_chart(fig_gantt, use_container_width=True)
        else:
            st.info("Aucune tâche à afficher dans le Gantt")
        
        st.divider()
        
        # TABLEAU ÉDITABLE
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
        
        df_gantt_global = df_plan.dropna(subset=["Start Date", "End Date"]).copy()
        df_gantt_global["Tâche_Projet"] = df_gantt_global["Tâche"] + " [" + df_gantt_global["Projet"].str[:30] + "]"
        
        if not df_gantt_global.empty:
            fig_global = create_gantt_chart_global(df_gantt_global, title="📅 Gantt Global - Tous les Projets")
            if fig_global:
                st.plotly_chart(fig_global, use_container_width=True)
        
        st.divider()
        
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
st.markdown(f"🛠 **PI Planning Tool v7.4** | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
