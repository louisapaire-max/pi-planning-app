import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import io

st.set_page_config(page_title="PI Planning - Capacity Tool v9.1", layout="wide")
st.title("📊 PI Planning - Capacity Planning avec Import Excel")

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
    "Product Owner": "#FF6B6B", "PO": "#FF6B6B",
    "Product Manager": "#E74C3C",
    "Project Manager": "#C0392B",
    "Product unit": "#FF8C42", 
    "COE (catalogue unifié)": "#FFC300",
    "Marketing": "#FF1493", 
    "Design": "#9D4EDD", 
    "Webmaster": "#3A86FF",
    "Dev Web Front": "#00D9FF", "Dev Front/Back": "#00D9FF",
    "Dev Web Back": "#0099FF", 
    "Dev Order": "#2E7D32",
    "Dev Manager": "#4CAF50",
    "Tracking": "#FFB703", 
    "SEO": "#FB5607", 
    "QA": "#8E44AD", 
    "Traduction": "#1ABC9C"
}

# SESSION STATE
if "imported_data" not in st.session_state:
    st.session_state.imported_data = None

# FONCTION PARSER AVEC GESTION DES HEURES
def parse_date_with_hours(date_str):
    """Parse une date avec ou sans heures"""
    date_str = str(date_str).strip()
    
    # Essayer d'abord avec heures (DD/MM/YYYY HH:MM)
    for fmt in ['%d/%m/%Y %H:%M', '%d/%m/%Y']:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except:
            continue
    
    return pd.NaT

def parse_excel_paste(text_data):
    """Parse le texte collé depuis Excel"""
    lines = text_data.strip().split('\n')

    all_data = []
    current_project = None
    current_jira = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Détecter le projet
        if 'PROJET' in line and ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                current_project = parts[1].strip()
                continue

        # Détecter le Jira
        if line.startswith('Jira:'):
            current_jira = line.replace('Jira:', '').strip()
            continue

        # Ignorer en-têtes
        if 'Phase' in line and 'Tâche' in line:
            continue

        # Parser données (tabulation ou |)
        if '\t' in line:
            parts = [p.strip() for p in line.split('\t') if p.strip()]
        elif '|' in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
        else:
            continue

        if len(parts) >= 5:
            all_data.append({
                'Projet': current_project if current_project else 'Projet inconnu',
                'Jira': current_jira if current_jira else 'N/A',
                'Phase': parts[0],
                'Tâche': parts[1],
                'Équipe': parts[2],
                'Début': parts[3],
                'Fin': parts[4]
            })

    return pd.DataFrame(all_data)

# FONCTION GANTT AVEC GESTION DES HEURES
def create_gantt_from_imported_data(df_data):
    """Crée un Gantt chart avec gestion des tâches d'une journée"""
    if df_data.empty:
        return None

    df_copy = df_data.copy()

    # Convertir dates avec gestion des heures
    df_copy['Start Date'] = df_copy['Début'].apply(parse_date_with_hours)
    df_copy['End Date'] = df_copy['Fin'].apply(parse_date_with_hours)

    # Pour les tâches d'une seule journée sans heures, ajouter une durée minimale
    same_day_mask = (df_copy['Start Date'].dt.date == df_copy['End Date'].dt.date)
    no_time_mask = (df_copy['Start Date'].dt.hour == 0) & (df_copy['End Date'].dt.hour == 0)
    
    # Ajouter 9 heures de durée pour les tâches d'un jour sans heures spécifiées
    df_copy.loc[same_day_mask & no_time_mask, 'Start Date'] = df_copy.loc[same_day_mask & no_time_mask, 'Start Date'] + pd.Timedelta(hours=9)
    df_copy.loc[same_day_mask & no_time_mask, 'End Date'] = df_copy.loc[same_day_mask & no_time_mask, 'End Date'] + pd.Timedelta(hours=18)

    # Label
    df_copy['Label'] = df_copy['Projet'] + ' - ' + df_copy['Tâche']

    # Supprimer les lignes sans date valide
    df_copy = df_copy.dropna(subset=['Start Date', 'End Date'])

    if df_copy.empty:
        return None

    fig = px.timeline(
        df_copy,
        x_start='Start Date',
        x_end='End Date',
        y='Label',
        color='Équipe',
        color_discrete_map=TEAM_COLORS,
        hover_data=['Projet', 'Phase', 'Jira'],
        title='📊 Gantt Chart - Planning Importé',
        height=max(800, len(df_copy) * 30)
    )

    # Ajouter itérations
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
            annotation_font_size=11
        )
        fig.add_vline(x=it["end"], line_width=1, line_dash="dot", line_color="gray")

    # Ligne aujourd'hui
    today_str = datetime.now().date().isoformat()
    fig.add_shape(
        type="line", x0=today_str, x1=today_str, y0=0, y1=1,
        yref="paper", line=dict(color="red", width=3)
    )
    fig.add_annotation(
        x=today_str, y=1, yref="paper",
        text="📍 AUJOURD'HUI", showarrow=False,
        yshift=10, font=dict(size=12, color="red", family="Arial Black")
    )

    fig.update_xaxes(
        tickformat="%d/%m",
        dtick=86400000.0,
        side="top",
        tickfont=dict(size=9),
        tickangle=-90,
        rangebreaks=[dict(bounds=["sat", "mon"])]
    )

    fig.update_yaxes(autorange="reversed", tickfont=dict(size=10))
    fig.update_layout(
        showlegend=True,
        margin=dict(t=120, b=50, l=450, r=200),
        plot_bgcolor='white'
    )

    return fig

# ONGLETS
tab_import, tab_stats = st.tabs([
    "📥 Import Excel & Gantt",
    "📊 Statistiques Projets"
])

# ═════════════════════════════════════════════════════════════════════
# ONGLET IMPORT EXCEL
# ═════════════════════════════════════════════════════════════════════
with tab_import:
    st.subheader("📥 Import de Planning depuis Excel")

    with st.expander("📖 Mode d'emploi", expanded=False):
        st.markdown("""
        ### Comment importer votre planning Excel ?

        1. **Ouvrez votre fichier Excel** contenant :
           - Nom du projet (ligne `PROJET X: ...`)
           - Référence Jira (ligne `Jira: ...`)
           - Tableau avec colonnes : `Phase | Tâche | Équipe | Début | Fin`

        2. **Sélectionnez toutes les données** (Ctrl+A ou Cmd+A)

        3. **Copiez** (Ctrl+C ou Cmd+C)

        4. **Collez** dans la zone ci-dessous (Ctrl+V ou Cmd+V)

        5. Cliquez sur **"📊 Générer le Gantt"**

        **Format attendu :**
        ```
        PROJET 1: Nom du projet
        Jira: LVL2-XXXXX
        Phase    Tâche              Équipe    Début              Fin
        DESIGN   Documentation      PO        12/01/2026         30/01/2026
        DEV      Dev Website        Dev       02/02/2026         20/02/2026
        DEV      PROD               PO        12/02/2026 09:00   12/02/2026 18:00
        ```
        
        **Note :** Les dates peuvent inclure des heures (HH:MM) pour les tâches d'une journée.
        """)

    # Données d'exemple
    example_data = """PROJET 1: Email - Add File Edition to Zimbra Pro
Jira: LVL2-18232
Phase	Tâche	Équipe	Début	Fin
DESIGN	Documentation Projet	PO	02/02/2026	20/02/2026
DESIGN	Kick-off Digital	PO	02/02/2026	20/02/2026
DESIGN	Etude d'impact	PO	02/02/2026	20/02/2026
DESIGN	Maquettes/Wireframe	Design	02/02/2026	20/02/2026
DEV	Integration OCMS	Webmaster	23/02/2026	13/03/2026
DEV	Dev Website	Dev Front/Back	23/02/2026	13/03/2026
DEV	QA & UAT (langue source)	QA	23/02/2026	13/03/2026
DEV	PROD	PO	23/02/2026	12/03/2026
PROJET 2: Website Revamp - homepage telephony
Jira: LVL2-18282
Phase	Tâche	Équipe	Début	Fin
DESIGN	Documentation Projet	PO	12/01/2026	30/01/2026
DESIGN	Maquettes/Wireframe	Design	12/01/2026	30/01/2026
DEV	Dev Website	Dev Front/Back	02/02/2026	20/02/2026
DEV	QA & UAT (langue source)	QA	02/02/2026	20/02/2026
DEV	PROD	PO	02/02/2026	19/02/2026"""

    # Zone de texte
    excel_text = st.text_area(
        "📋 Collez vos données Excel ici :",
        value=example_data if st.session_state.imported_data is None else "",
        height=450,
        key="excel_input",
        help="Copiez-collez directement depuis Excel (Ctrl+C puis Ctrl+V). Format dates accepté : DD/MM/YYYY ou DD/MM/YYYY HH:MM"
    )

    col1, col2, col3 = st.columns([2, 2, 6])

    with col1:
        if st.button("📊 Générer le Gantt", type="primary", use_container_width=True):
            if excel_text.strip():
                try:
                    df_parsed = parse_excel_paste(excel_text)
                    if not df_parsed.empty:
                        st.session_state.imported_data = df_parsed
                        st.success(f"✅ {len(df_parsed)} tâches importées depuis {df_parsed['Projet'].nunique()} projets")
                        st.rerun()
                    else:
                        st.error("❌ Aucune donnée valide détectée. Vérifiez le format.")
                except Exception as e:
                    st.error(f"❌ Erreur lors du parsing : {str(e)}")
            else:
                st.warning("⚠️ Veuillez coller des données")

    with col2:
        if st.button("🗑️ Effacer tout", use_container_width=True):
            st.session_state.imported_data = None
            st.rerun()

    # AFFICHAGE DES DONNÉES IMPORTÉES
    if st.session_state.imported_data is not None:
        st.divider()
        st.markdown("### 📊 Visualisation du Planning Importé")

        df_imported = st.session_state.imported_data

        # Statistiques
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("📁 Projets", df_imported['Projet'].nunique())
        with col_stat2:
            st.metric("📝 Tâches", len(df_imported))
        with col_stat3:
            st.metric("👥 Équipes", df_imported['Équipe'].nunique())
        with col_stat4:
            prod_count = df_imported[df_imported['Tâche'].str.contains('PROD', case=False, na=False)].shape[0]
            st.metric("🚀 Livraisons", prod_count)

        st.divider()

        # Filtres
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            all_projects = sorted(df_imported['Projet'].dropna().unique().tolist())
            selected_projects = st.multiselect(
                "🔍 Filtrer par projets :",
                options=all_projects,
                default=all_projects[:10] if len(all_projects) > 10 else all_projects
            )

        with col_filter2:
            all_teams = sorted(df_imported['Équipe'].dropna().unique().tolist())
            selected_teams = st.multiselect(
                "👥 Filtrer par équipes :",
                options=all_teams,
                default=all_teams
            )

        with col_filter3:
            all_phases = sorted(df_imported['Phase'].dropna().unique().tolist())
            selected_phases = st.multiselect(
                "⚙️ Filtrer par phases :",
                options=all_phases,
                default=all_phases
            )

        # Appliquer filtres
        df_filtered = df_imported[
            (df_imported['Projet'].isin(selected_projects)) &
            (df_imported['Équipe'].isin(selected_teams)) &
            (df_imported['Phase'].isin(selected_phases))
        ]

        st.info(f"📊 **{len(df_filtered)}** tâches affichées sur **{len(df_imported)}** au total")

        # Gantt Chart
        if not df_filtered.empty:
            fig_gantt = create_gantt_from_imported_data(df_filtered)
            if fig_gantt:
                st.plotly_chart(fig_gantt, use_container_width=True)
            else:
                st.warning("⚠️ Impossible de générer le Gantt (dates invalides)")
        else:
            st.warning("⚠️ Aucune donnée à afficher avec ces filtres")

        # Tableau détaillé
        st.divider()
        st.markdown("### 📋 Données Détaillées")

        # Trier par projet et date
        df_display = df_filtered.copy()
        df_display['Début_sort'] = df_display['Début'].apply(parse_date_with_hours)
        df_display = df_display.sort_values(['Projet', 'Début_sort'])
        df_display = df_display.drop('Début_sort', axis=1)

        st.dataframe(
            df_display[['Projet', 'Jira', 'Phase', 'Tâche', 'Équipe', 'Début', 'Fin']],
            use_container_width=True,
            height=500
        )

        # Export
        st.divider()
        col_export1, col_export2 = st.columns([1, 4])
        with col_export1:
            csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"planning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ═════════════════════════════════════════════════════════════════════
# ONGLET STATISTIQUES
# ═════════════════════════════════════════════════════════════════════
with tab_stats:
    st.subheader("📊 Statistiques par Projet")

    if st.session_state.imported_data is not None:
        df = st.session_state.imported_data

        # Stats par projet
        st.markdown("### 📁 Répartition des Tâches par Projet")

        project_stats = df.groupby('Projet').agg({
            'Tâche': 'count',
            'Équipe': lambda x: x.nunique(),
            'Jira': 'first'
        }).rename(columns={'Tâche': 'Nb Tâches', 'Équipe': 'Nb Équipes'})

        project_stats = project_stats.reset_index()
        project_stats = project_stats.sort_values('Nb Tâches', ascending=False)

        st.dataframe(project_stats, use_container_width=True, height=400)

        st.divider()

        # Stats par équipe
        st.markdown("### 👥 Charge par Équipe")

        team_stats = df.groupby('Équipe').agg({
            'Tâche': 'count',
            'Projet': lambda x: x.nunique()
        }).rename(columns={'Tâche': 'Nb Tâches', 'Projet': 'Nb Projets'})

        team_stats = team_stats.reset_index()
        team_stats = team_stats.sort_values('Nb Tâches', ascending=False)

        col_chart, col_table = st.columns([2, 1])

        with col_chart:
            fig_bar = px.bar(
                team_stats,
                x='Équipe',
                y='Nb Tâches',
                title='Nombre de tâches par équipe',
                color='Nb Tâches',
                color_continuous_scale='Blues'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_table:
            st.dataframe(team_stats, use_container_width=True, height=400)

    else:
        st.info("📥 Importez d'abord des données depuis l'onglet 'Import Excel'")

st.divider()
st.caption(f"Version 9.1 | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
