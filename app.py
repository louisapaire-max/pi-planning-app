# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET 1: VUE GLOBALE PLANNING
# ═══════════════════════════════════════════════════════════════════════════════
with tab_planning:
    st.subheader("📋 Vue Globale du Planning")
    st.info("📊 Vue d'ensemble de toutes les tâches de tous les projets")
    
    if not df_plan.empty:
        df_plan["Start Date"] = pd.to_datetime(df_plan["Début"], errors='coerce')
        df_plan["End Date"] = pd.to_datetime(df_plan["Fin"], errors='coerce')
        
        # ═════════════════════════════════════════════════════════════════════════
        # FILTRES
        # ═════════════════════════════════════════════════════════════════════════
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
        
        # Bouton reset filtres
        if st.button("🔄 Réinitialiser les filtres", key="reset_filters"):
            st.session_state.filter_projects = ["Tous"]
            st.session_state.filter_teams = ["Toutes"]
            st.session_state.filter_tasks = ["Toutes"]
            st.rerun()
        
        st.divider()
        
        # ═════════════════════════════════════════════════════════════════════════
        # APPLIQUER LES FILTRES
        # ═════════════════════════════════════════════════════════════════════════
        df_filtered = df_plan.copy()
        
        # Filtre Projets
        if "Tous" not in selected_projects and len(selected_projects) > 0:
            df_filtered = df_filtered[df_filtered["Projet"].isin(selected_projects)]
        
        # Filtre Équipes
        if "Toutes" not in selected_teams and len(selected_teams) > 0:
            df_filtered = df_filtered[df_filtered["Équipe"].isin(selected_teams)]
        
        # Filtre Tâches
        if "Toutes" not in selected_tasks and len(selected_tasks) > 0:
            df_filtered = df_filtered[df_filtered["Tâche"].isin(selected_tasks)]
        
        # ═════════════════════════════════════════════════════════════════════════
        # MÉTRIQUES APRÈS FILTRAGE
        # ═════════════════════════════════════════════════════════════════════════
        if not df_filtered.empty:
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                st.metric("📊 Projets", df_filtered["Projet"].nunique())
            with col_m2:
                st.metric("📋 Tâches", len(df_filtered))
            with col_m3:
                charge_filtered = df_filtered["Charge"].sum()
                st.metric("⏱️ Charge totale", f"{charge_filtered:.1f}j")
            with col_m4:
                st.metric("👥 Équipes", df_filtered["Équipe"].nunique())
            
            st.divider()
            
            # ═════════════════════════════════════════════════════════════════════
            # GANTT FILTRÉ
            # ═════════════════════════════════════════════════════════════════════
            df_gantt_global = df_filtered.dropna(subset=["Start Date", "End Date"]).copy()
            df_gantt_global["Tâche_Projet"] = df_gantt_global["Tâche"] + " [" + df_gantt_global["Projet"].str[:30] + "]"
            
            if not df_gantt_global.empty:
                fig_global = create_gantt_chart_global(df_gantt_global, title="📅 Gantt Global - Vue Filtrée")
                if fig_global:
                    st.plotly_chart(fig_global, use_container_width=True)
            else:
                st.warning("Aucune tâche à afficher dans le Gantt avec ces filtres")
            
            st.divider()
            
            # ═════════════════════════════════════════════════════════════════════
            # TABLEAU FILTRÉ
            # ═════════════════════════════════════════════════════════════════════
            st.markdown("### 📊 Tableau détaillé")
            
            display_cols = ["Priorité", "Projet", "Tâche", "Équipe", "Début", "Fin", "Charge", "Dépendance", "Statut"]
            
            # Options de tri
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
            
            # Appliquer le tri
            ascending = True if sort_order == "Croissant" else False
            df_sorted = df_filtered.sort_values(by=sort_by, ascending=ascending)
            
            st.dataframe(
                df_sorted[display_cols],
                use_container_width=True,
                hide_index=True,
                height=600
            )
            
            # ═════════════════════════════════════════════════════════════════════
            # EXPORT CSV
            # ═════════════════════════════════════════════════════════════════════
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
