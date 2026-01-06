import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="PI Planning Editor v10.1", layout="wide")
st.title("📊 PI Planning - Éditeur Excel Interactif")

# CONFIGURATION
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

TEAM_COLORS = {
    "PO": "#FF6B6B", "Design": "#9D4EDD", "Webmaster": "#3A86FF",
    "Dev Front/Back": "#00D9FF", "Dev Order": "#2E7D32",
    "Dev Manager": "#4CAF50", "QA": "#8E44AD", "Traduction": "#1ABC9C",
    "Marketing": "#FF1493", "SEO": "#FB5607"
}

# DONNÉES PAR DÉFAUT CORRIGÉES
DEFAULT_DATA = [
    {"Projet": "Email - Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DESIGN", "Tâche": "Documentation", "Équipe": "PO", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Email - Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "Email - Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "11/02/2026", "Fin": "11/02/2026"},
    {"Projet": "Email - Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Email - Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/03/2026 09:00", "Fin": "12/03/2026 18:00"},
    {"Projet": "Website - Homepage Tel", "Jira": "LVL2-18282", "Phase": "DESIGN", "Tâche": "Documentation", "Équipe": "PO", "Début": "12/01/2026", "Fin": "30/01/2026"},
    {"Projet": "Website - Homepage Tel", "Jira": "LVL2-18282", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "14/01/2026", "Fin": "14/01/2026"},
    {"Projet": "Website - Homepage Tel", "Jira": "LVL2-18282", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "21/01/2026", "Fin": "21/01/2026"},
    {"Projet": "Website - Homepage Tel", "Jira": "LVL2-18282", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Website - Homepage Tel", "Jira": "LVL2-18282", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/02/2026 09:00", "Fin": "19/02/2026 18:00"},
    {"Projet": "VPS - RBX7", "Jira": "LVL2-18432", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "VPS - RBX7", "Jira": "LVL2-18432", "Phase": "DEV", "Tâche": "Dev Order", "Équipe": "Dev Order", "Début": "09/02/2026", "Fin": "10/02/2026"},
    {"Projet": "VPS - RBX7", "Jira": "LVL2-18432", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/02/2026 09:00", "Fin": "12/02/2026 18:00"},
]

# SESSION STATE
if "df_planning" not in st.session_state:
    st.session_state.df_planning = pd.DataFrame(DEFAULT_DATA)

# FONCTIONS
def parse_date_safe(date_str):
    """Parse une date avec gestion d'erreur robuste"""
    if pd.isna(date_str):
        return pd.NaT
    date_str = str(date_str).strip()
    for fmt in ['%d/%m/%Y %H:%M', '%d/%m/%Y']:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except:
            continue
    return pd.NaT

def create_gantt_chart(df_source):
    """Crée un Gantt avec toutes les fonctionnalités"""
    if df_source.empty:
        return None
    
    df = df_source.copy()
    df['Start_Date'] = df['Début'].apply(parse_date_safe)
    df['End_Date'] = df['Fin'].apply(parse_date_safe)
    
    # Filtrer dates invalides
    df = df.dropna(subset=['Start_Date', 'End_Date'])
    if df.empty:
        return None
    
    # Correction tâches d'un jour sans heures (09:00-18:00)
    same_day = df['Start_Date'].dt.date == df['End_Date'].dt.date
    no_hours = (df['Start_Date'].dt.hour == 0) & (df['End_Date'].dt.hour == 0)
    mask = same_day & no_hours
    
    df.loc[mask, 'Start_Date'] = df.loc[mask, 'Start_Date'] + pd.Timedelta(hours=9)
    df.loc[mask, 'End_Date'] = df.loc[mask, 'End_Date'] + pd.Timedelta(hours=18)
    
    # Label pour le Gantt
    df['Label'] = df['Projet'] + ' - ' + df['Tâche']
    
    # Créer le Gantt
    fig = px.timeline(
        df,
        x_start='Start_Date',
        x_end='End_Date',
        y='Label',
        color='Équipe',
        color_discrete_map=TEAM_COLORS,
        hover_data=['Projet', 'Jira', 'Phase'],
        title='📊 Gantt Planning Q2 2026',
        height=max(600, len(df) * 35)
    )
    
    # Ajouter les itérations en arrière-plan
    colors_bg = ["rgba(230, 230, 230, 0.3)", "rgba(200, 230, 255, 0.3)", 
                 "rgba(220, 255, 220, 0.3)", "rgba(255, 220, 220, 0.3)", 
                 "rgba(220, 255, 255, 0.3)"]
    
    for i, it in enumerate(ITERATIONS):
        fig.add_vrect(
            x0=it["start"], x1=it["end"],
            fillcolor=colors_bg[i % len(colors_bg)],
            layer="below", line_width=0,
            annotation_text=f"<b>{it['name']}</b>",
            annotation_position="top left",
            annotation_font_size=10
        )
        fig.add_vline(x=it["end"], line_width=1, line_dash="dot", line_color="gray")
    
    # Ligne "Aujourd'hui"
    today = datetime.now().date().isoformat()
    fig.add_shape(
        type="line", x0=today, x1=today, y0=0, y1=1,
        yref="paper", line=dict(color="red", width=3)
    )
    fig.add_annotation(
        x=today, y=1, yref="paper",
        text="📍 AUJOURD'HUI", showarrow=False,
        yshift=10, font=dict(size=12, color="red", family="Arial Black")
    )
    
    # Mise en forme des axes
    fig.update_xaxes(
        tickformat="%d/%m",
        dtick=86400000.0,
        side="top",
        tickfont=dict(size=9),
        tickangle=-90,
        rangebreaks=[dict(bounds=["sat", "mon"])]  # Masquer week-ends
    )
    
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=10))
    fig.update_layout(
        showlegend=True,
        margin=dict(t=120, b=50, l=400, r=150),
        plot_bgcolor='white'
    )
    
    return fig

# INTERFACE UTILISATEUR
tab1, tab2, tab3 = st.tabs(["📝 Édition Excel", "📊 Gantt Chart", "📈 Statistiques"])

# ═══════════════════════════════════════════════════════════
# TAB 1: ÉDITEUR EXCEL
# ═══════════════════════════════════════════════════════════
with tab1:
    st.subheader("📝 Édition Interactive du Planning")
    
    with st.expander("💡 Mode d'emploi", expanded=False):
        st.markdown("""
        - **Modifier une cellule** : Cliquez dessus et tapez
        - **Ajouter une ligne** : Cliquez sur "+" en bas du tableau
        - **Supprimer une ligne** : Cochez la case à gauche puis supprimez
        - **Copier-Coller depuis Excel** : Sélectionnez des cellules Excel → Ctrl+C → Cliquez dans le tableau → Ctrl+V
        - **Format dates** : `DD/MM/YYYY` ou `DD/MM/YYYY HH:MM` pour les tâches avec horaires
        """)
    
    # Éditeur de données style Excel
    edited_df = st.data_editor(
        st.session_state.df_planning,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Projet": st.column_config.TextColumn("Projet", width="medium"),
            "Jira": st.column_config.TextColumn("Jira", width="small"),
            "Phase": st.column_config.SelectboxColumn("Phase", options=["DESIGN", "DEV"], required=True),
            "Tâche": st.column_config.TextColumn("Tâche", width="medium"),
            "Équipe": st.column_config.SelectboxColumn("Équipe", options=list(TEAM_COLORS.keys()), required=True),
            "Début": st.column_config.TextColumn("Début (DD/MM/YYYY)", help="Format: 12/01/2026 ou 12/01/2026 09:00"),
            "Fin": st.column_config.TextColumn("Fin (DD/MM/YYYY)", help="Format: 30/01/2026 ou 12/02/2026 18:00"),
        },
        hide_index=False,
        key="data_editor"
    )
    
    col1, col2, col3 = st.columns([2, 2, 6])
    
    with col1:
        if st.button("💾 Enregistrer les modifications", type="primary", use_container_width=True):
            st.session_state.df_planning = edited_df.copy()
            st.success("✅ Planning sauvegardé !")
            st.rerun()
    
    with col2:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            st.session_state.df_planning = pd.DataFrame(DEFAULT_DATA)
            st.rerun()

# ═══════════════════════════════════════════════════════════
# TAB 2: GANTT CHART
# ═══════════════════════════════════════════════════════════
with tab2:
    st.subheader("📊 Visualisation Gantt")
    
    if not st.session_state.df_planning.empty:
        # Statistiques rapides
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📁 Projets", st.session_state.df_planning['Projet'].nunique())
        with col2:
            st.metric("📝 Tâches", len(st.session_state.df_planning))
        with col3:
            st.metric("👥 Équipes", st.session_state.df_planning['Équipe'].nunique())
        with col4:
            prod_count = st.session_state.df_planning[st.session_state.df_planning['Tâche'].str.contains('PROD', case=False, na=False)].shape[0]
            st.metric("🚀 Mises en PROD", prod_count)
        
        st.divider()
        
        # Filtres
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            all_projects = sorted(st.session_state.df_planning['Projet'].unique())
            selected_projects = st.multiselect("Filtrer par Projets", all_projects, default=all_projects)
        with col_f2:
            all_teams = sorted(st.session_state.df_planning['Équipe'].unique())
            selected_teams = st.multiselect("Filtrer par Équipes", all_teams, default=all_teams)
        with col_f3:
            all_phases = sorted(st.session_state.df_planning['Phase'].unique())
            selected_phases = st.multiselect("Filtrer par Phases", all_phases, default=all_phases)
        
        # Appliquer filtres
        df_filtered = st.session_state.df_planning[
            (st.session_state.df_planning['Projet'].isin(selected_projects)) &
            (st.session_state.df_planning['Équipe'].isin(selected_teams)) &
            (st.session_state.df_planning['Phase'].isin(selected_phases))
        ]
        
        st.info(f"📊 **{len(df_filtered)}** tâches affichées sur **{len(st.session_state.df_planning)}** au total")
        
        # Générer le Gantt
        fig = create_gantt_chart(df_filtered)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Aucune donnée valide à afficher (vérifiez le format des dates)")
        
        # Export CSV
        st.divider()
        csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Télécharger en CSV",
            data=csv,
            file_name=f"planning_Q2_2026_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Aucune donnée à afficher")

# ═══════════════════════════════════════════════════════════
# TAB 3: STATISTIQUES
# ═══════════════════════════════════════════════════════════
with tab3:
    st.subheader("📈 Statistiques du Planning")
    
    if not st.session_state.df_planning.empty:
        df = st.session_state.df_planning
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("### 📁 Tâches par Projet")
            project_stats = df.groupby('Projet').size().reset_index(name='Nombre')
            fig_proj = px.bar(project_stats, x='Projet', y='Nombre', color='Nombre', color_continuous_scale='Blues')
            st.plotly_chart(fig_proj, use_container_width=True)
        
        with col_chart2:
            st.markdown("### 👥 Tâches par Équipe")
            team_stats = df.groupby('Équipe').size().reset_index(name='Nombre')
            fig_team = px.bar(team_stats, x='Équipe', y='Nombre', color='Équipe', color_discrete_map=TEAM_COLORS)
            st.plotly_chart(fig_team, use_container_width=True)
        
        st.divider()
        
        # Tableau détaillé
        st.markdown("### 📋 Répartition Détaillée")
        pivot = df.groupby(['Projet', 'Phase']).size().unstack(fill_value=0)
        st.dataframe(pivot, use_container_width=True)
        
    else:
        st.info("Aucune statistique disponible")

st.divider()
st.caption(f"PI Planning Tool v10.1 | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
