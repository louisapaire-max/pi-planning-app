import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="PI Planning Editor v13.0", layout="wide")
st.title("📊 PI Planning Q2 2026 - Éditeur Excel & Gantt Optimisé")

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════
# DONNÉES PAR DÉFAUT (15 PROJETS)
# ═══════════════════════════════════════════════════════════
DEFAULT_DATA = [
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DESIGN", "Tâche": "Maquettes/Wireframe", "Équipe": "Design", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "11/02/2026", "Fin": "11/02/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DEV", "Tâche": "QA & UAT", "Équipe": "QA", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/03/2026 09:00", "Fin": "12/03/2026 18:00"},
    {"Projet": "Website Revamp - homepage telephony", "Jira": "LVL2-18282", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "12/01/2026", "Fin": "30/01/2026"},
    {"Projet": "Website Revamp - homepage telephony", "Jira": "LVL2-18282", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "14/01/2026", "Fin": "14/01/2026"},
    {"Projet": "Website Revamp - homepage telephony", "Jira": "LVL2-18282", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "21/01/2026", "Fin": "21/01/2026"},
    {"Projet": "Website Revamp - homepage telephony", "Jira": "LVL2-18282", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Website Revamp - homepage telephony", "Jira": "LVL2-18282", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/02/2026 09:00", "Fin": "19/02/2026 18:00"},
    {"Projet": "VPS - Add more choice on Disk options", "Jira": "LVL2-16718", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "12/01/2026", "Fin": "30/01/2026"},
    {"Projet": "VPS - Add more choice on Disk options", "Jira": "LVL2-16718", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "14/01/2026", "Fin": "14/01/2026"},
    {"Projet": "VPS - Add more choice on Disk options", "Jira": "LVL2-16718", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "21/01/2026", "Fin": "21/01/2026"},
    {"Projet": "VPS - Add more choice on Disk options", "Jira": "LVL2-16718", "Phase": "DEV", "Tâche": "Dev Order", "Équipe": "Dev Order", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "VPS - Add more choice on Disk options", "Jira": "LVL2-16718", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/02/2026 09:00", "Fin": "19/02/2026 18:00"},
    {"Projet": "Zimbra : add yearly commitment", "Jira": "LVL2-18237", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Zimbra : add yearly commitment", "Jira": "LVL2-18237", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "Zimbra : add yearly commitment", "Jira": "LVL2-18237", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "Zimbra : add yearly commitment", "Jira": "LVL2-18237", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "Zimbra : add yearly commitment", "Jira": "LVL2-18237", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    {"Projet": "Telco - Create new plans for Trunk", "Jira": "LVL2-18063", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Telco - Create new plans for Trunk", "Jira": "LVL2-18063", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "Telco - Create new plans for Trunk", "Jira": "LVL2-18063", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "Telco - Create new plans for Trunk", "Jira": "LVL2-18063", "Phase": "DEV", "Tâche": "Dev Order", "Équipe": "Dev Order", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "Telco - Create new plans for Trunk", "Jira": "LVL2-18063", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    {"Projet": "Funnel order improvement", "Jira": "LVL2-19317", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Funnel order improvement", "Jira": "LVL2-19317", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "Funnel order improvement", "Jira": "LVL2-19317", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "11/02/2026", "Fin": "11/02/2026"},
    {"Projet": "Funnel order improvement", "Jira": "LVL2-19317", "Phase": "DEV", "Tâche": "Dev Order", "Équipe": "Dev Order", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Funnel order improvement", "Jira": "LVL2-19317", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/03/2026 09:00", "Fin": "12/03/2026 18:00"},
    {"Projet": "VPS 2026 RBX7", "Jira": "LVL2-18432", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "VPS 2026 RBX7", "Jira": "LVL2-18432", "Phase": "DEV", "Tâche": "Dev Order", "Équipe": "Dev Order", "Début": "09/02/2026", "Fin": "10/02/2026"},
    {"Projet": "VPS 2026 RBX7", "Jira": "LVL2-18432", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/02/2026 09:00", "Fin": "12/02/2026 18:00"},
    {"Projet": "lot 2 website page Phone & Headset", "Jira": "LVL2-18859", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "lot 2 website page Phone & Headset", "Jira": "LVL2-18859", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "lot 2 website page Phone & Headset", "Jira": "LVL2-18859", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "lot 2 website page Phone & Headset", "Jira": "LVL2-18859", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "lot 2 website page Phone & Headset", "Jira": "LVL2-18859", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    {"Projet": "Website Revamp - numbers page", "Jira": "LVL2-15863", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Website Revamp - numbers page", "Jira": "LVL2-15863", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "Website Revamp - numbers page", "Jira": "LVL2-15863", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "11/02/2026", "Fin": "11/02/2026"},
    {"Projet": "Website Revamp - numbers page", "Jira": "LVL2-15863", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Website Revamp - numbers page", "Jira": "LVL2-15863", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/03/2026 09:00", "Fin": "12/03/2026 18:00"},
    {"Projet": "VOIP Offers - Update 40 Destinations", "Jira": "LVL2-18408", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "VOIP Offers - Update 40 Destinations", "Jira": "LVL2-18408", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "VOIP Offers - Update 40 Destinations", "Jira": "LVL2-18408", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "11/02/2026", "Fin": "11/02/2026"},
    {"Projet": "VOIP Offers - Update 40 Destinations", "Jira": "LVL2-18408", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "VOIP Offers - Update 40 Destinations", "Jira": "LVL2-18408", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/03/2026 09:00", "Fin": "12/03/2026 18:00"},
    {"Projet": "Email - Quick Wins - Zimbra Webmail", "Jira": "LVL2-18562", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Email - Quick Wins - Zimbra Webmail", "Jira": "LVL2-18562", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "Email - Quick Wins - Zimbra Webmail", "Jira": "LVL2-18562", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "Email - Quick Wins - Zimbra Webmail", "Jira": "LVL2-18562", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "Email - Quick Wins - Zimbra Webmail", "Jira": "LVL2-18562", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    {"Projet": "Email - Quick Wins - Exchange Pages", "Jira": "LVL2-18598", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Email - Quick Wins - Exchange Pages", "Jira": "LVL2-18598", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "Email - Quick Wins - Exchange Pages", "Jira": "LVL2-18598", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "Email - Quick Wins - Exchange Pages", "Jira": "LVL2-18598", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "Email - Quick Wins - Exchange Pages", "Jira": "LVL2-18598", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    {"Projet": "VPS - Website Application New pages", "Jira": "LVL2-16407", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "VPS - Website Application New pages", "Jira": "LVL2-16407", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "VPS - Website Application New pages", "Jira": "LVL2-16407", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "VPS - Website Application New pages", "Jira": "LVL2-16407", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "VPS - Website Application New pages", "Jira": "LVL2-16407", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    {"Projet": "Revamp Web Cloud - Migrate P1", "Jira": "LVL2-19319", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Revamp Web Cloud - Migrate P1", "Jira": "LVL2-19319", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "Revamp Web Cloud - Migrate P1", "Jira": "LVL2-19319", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "Revamp Web Cloud - Migrate P1", "Jira": "LVL2-19319", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "Revamp Web Cloud - Migrate P1", "Jira": "LVL2-19319", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    {"Projet": "Telephony - Website revamp", "Jira": "LVL2-16404", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Telephony - Website revamp", "Jira": "LVL2-16404", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "Telephony - Website revamp", "Jira": "LVL2-16404", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "11/02/2026", "Fin": "11/02/2026"},
    {"Projet": "Telephony - Website revamp", "Jira": "LVL2-16404", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Telephony - Website revamp", "Jira": "LVL2-16404", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/03/2026 09:00", "Fin": "12/03/2026 18:00"},
]

# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════
if "df_planning" not in st.session_state:
    st.session_state.df_planning = pd.DataFrame(DEFAULT_DATA)
if "df_with_dates" not in st.session_state:
    st.session_state.df_with_dates = None
    st.session_state.data_hash = None
if "selected_projects" not in st.session_state:
    st.session_state.selected_projects = []
if "selected_teams" not in st.session_state:
    st.session_state.selected_teams = []
if "selected_phases" not in st.session_state:
    st.session_state.selected_phases = []
if "selected_tasks" not in st.session_state:
    st.session_state.selected_tasks = []

# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════
def parse_date_safe(date_str):
    if pd.isna(date_str):
        return pd.NaT
    date_str = str(date_str).strip()
    for fmt in ['%d/%m/%Y %H:%M', '%d/%m/%Y']:
        try:
            parsed = pd.to_datetime(date_str, format=fmt)
            if parsed.year < 2020 or parsed.year > 2030:
                return pd.NaT
            return parsed
        except:
            continue
    return pd.NaT

def is_prod_task(task_name):
    return str(task_name).strip().upper() == 'PROD'

def format_with_day(dt):
    if pd.isna(dt):
        return ""
    weekday_map = {0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi", 4: "Vendredi", 5: "Samedi", 6: "Dimanche"}
    day = weekday_map[int(dt.weekday())]
    if dt.hour == 0 and dt.minute == 0:
        return f"{day} {dt.strftime('%d/%m/%Y')}"
    return f"{day} {dt.strftime('%d/%m/%Y %H:%M')}"

@st.cache_data(show_spinner=False)
def compute_dates_cached(df_dict, data_version):
    df = pd.DataFrame(df_dict)
    df['Start_Date'] = df['Début'].apply(parse_date_safe)
    df['End_Date'] = df['Fin'].apply(parse_date_safe)
    df = df.dropna(subset=['Start_Date', 'End_Date'])
    return df

def get_cached_df():
    data_hash = pd.util.hash_pandas_object(st.session_state.df_planning).sum()
    if st.session_state.data_hash != data_hash:
        st.session_state.data_hash = data_hash
        df_dict = st.session_state.df_planning.to_dict('list')
        st.session_state.df_with_dates = compute_dates_cached(df_dict, data_hash)
    return st.session_state.df_with_dates

def create_gantt_chart(df_source):
    if df_source.empty:
        return None
    df = df_source.copy()
    same_day = df['Start_Date'].dt.date == df['End_Date'].dt.date
    no_hours = (df['Start_Date'].dt.hour == 0) & (df['End_Date'].dt.hour == 0)
    mask = same_day & no_hours
    df.loc[mask, 'Start_Date'] += pd.Timedelta(hours=9)
    df.loc[mask, 'End_Date'] += pd.Timedelta(hours=18)
    df = df.sort_values(['Start_Date', 'Projet', 'Phase'])
    df['Projet_Court'] = df['Projet'].apply(lambda x: x[:35] + '...' if len(x) > 35 else x)
    df['Label_Hiérarchique'] = df['Projet_Court'] + ' | ' + df['Phase'] + ' | ' + df['Tâche']
    df['Type_Tache'] = df['Tâche'].apply(lambda x: '🎯 JALON' if is_prod_task(x) else 'Tâche')
    df['Durée_Jours'] = (df['End_Date'] - df['Start_Date']).dt.days + 1

    fig = px.timeline(df, x_start='Start_Date', x_end='End_Date', y='Label_Hiérarchique', color='Équipe',
                      color_discrete_map=TEAM_COLORS,
                      hover_data={'Projet': True, 'Jira': True, 'Phase': True, 'Type_Tache': True, 'Durée_Jours': True,
                                  'Label_Hiérarchique': False, 'Start_Date': False, 'End_Date': False},
                      height=max(700, len(df) * 40))

    colors_bg = ["rgba(230, 230, 250, 0.25)", "rgba(200, 230, 255, 0.3)", "rgba(220, 255, 220, 0.3)",
                 "rgba(255, 240, 220, 0.3)", "rgba(255, 220, 255, 0.25)"]

    for i, it in enumerate(ITERATIONS):
        fig.add_vrect(x0=it["start"], x1=it["end"], fillcolor=colors_bg[i % len(colors_bg)], layer="below", line_width=0,
                      annotation_text=f"<b>{it['name']}</b>", annotation_position="top left",
                      annotation_font=dict(size=8, color="darkblue", family="Arial"))
        fig.add_vline(x=it["end"], line_width=1, line_dash="dash", line_color="rgba(100,100,100,0.4)")

    today = datetime.now().date().isoformat()
    fig.add_shape(type="line", x0=today, x1=today, y0=0, y1=1, yref="paper",
                  line=dict(color="rgba(255, 100, 100, 0.7)", width=2, dash="dash"))
    fig.add_annotation(x=today, y=1.01, yref="paper", text=f"Aujourd'hui ({datetime.now().strftime('%d/%m')})",
                       showarrow=False, font=dict(size=9, color="rgba(200, 50, 50, 0.8)"),
                       bgcolor="rgba(255,255,255,0.7)")

    fig.update_xaxes(title="<b>Calendrier 2026</b>", tickformat="%d/%m", dtick=86400000.0 * 7, side="top",
                     tickfont=dict(size=10), tickangle=-45, rangebreaks=[dict(bounds=["sat", "mon"])])
    fig.update_yaxes(title="<b>Tâches</b>", autorange="reversed", tickfont=dict(size=9))
    fig.update_layout(showlegend=True, margin=dict(t=80, b=80, l=500, r=200), plot_bgcolor='rgba(250,250,250,1)',
                      paper_bgcolor='white', hovermode='closest')

    prods = df[df['Tâche'].apply(is_prod_task)]
    for idx, row in prods.iterrows():
        fig.add_annotation(x=row['End_Date'], y=row['Label_Hiérarchique'], text="🚀", showarrow=False, font=dict(size=20), xshift=15)

    return fig

def dataframe_to_tsv(df):
    return df.to_csv(sep='\t', index=False)

# ═══════════════════════════════════════════════════════════
# INTERFACE
# ═══════════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["📊 Planning & Gantt", "📅 Vue Temporelle"])

with tab1:
    st.subheader("📊 Gantt et Tableau")
    df_cached = get_cached_df()

    if not df_cached.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📁 Projets", df_cached['Projet'].nunique())
        col2.metric("📝 Tâches", len(df_cached))
        col3.metric("👥 Équipes", df_cached['Équipe'].nunique())
        col4.metric("🚀 Livraisons", df_cached[df_cached['Tâche'].apply(is_prod_task)].shape[0])

        st.divider()

        all_projects = sorted(df_cached['Projet'].unique())
        all_teams = sorted(df_cached['Équipe'].unique())
        all_phases = sorted(df_cached['Phase'].unique())
        all_tasks = sorted(df_cached['Tâche'].unique())

        # FIX: Synchroniser les valeurs par défaut avec les options disponibles
        if not st.session_state.selected_projects:
            st.session_state.selected_projects = all_projects
        else:
            st.session_state.selected_projects = [p for p in st.session_state.selected_projects if p in all_projects]
            if not st.session_state.selected_projects:
                st.session_state.selected_projects = all_projects

        if not st.session_state.selected_teams:
            st.session_state.selected_teams = all_teams
        else:
            st.session_state.selected_teams = [t for t in st.session_state.selected_teams if t in all_teams]
            if not st.session_state.selected_teams:
                st.session_state.selected_teams = all_teams

        if not st.session_state.selected_phases:
            st.session_state.selected_phases = all_phases
        else:
            st.session_state.selected_phases = [p for p in st.session_state.selected_phases if p in all_phases]
            if not st.session_state.selected_phases:
                st.session_state.selected_phases = all_phases

        if not st.session_state.selected_tasks:
            st.session_state.selected_tasks = all_tasks
        else:
            st.session_state.selected_tasks = [t for t in st.session_state.selected_tasks if t in all_tasks]
            if not st.session_state.selected_tasks:
                st.session_state.selected_tasks = all_tasks

        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            selected_projects = st.multiselect("🔍 Projets", all_projects, default=st.session_state.selected_projects, key="filter_projects")
            st.session_state.selected_projects = selected_projects
        with col_f2:
            selected_teams = st.multiselect("👥 Équipes", all_teams, default=st.session_state.selected_teams, key="filter_teams")
            st.session_state.selected_teams = selected_teams
        with col_f3:
            selected_phases = st.multiselect("⚙️ Phases", all_phases, default=st.session_state.selected_phases, key="filter_phases")
            st.session_state.selected_phases = selected_phases
        with col_f4:
            selected_tasks = st.multiselect("📋 Tâches", all_tasks, default=st.session_state.selected_tasks, key="filter_tasks")
            st.session_state.selected_tasks = selected_tasks

        df_filtered = df_cached[(df_cached['Projet'].isin(selected_projects)) & (df_cached['Équipe'].isin(selected_teams)) &
                                (df_cached['Phase'].isin(selected_phases)) & (df_cached['Tâche'].isin(selected_tasks))]

        fig = create_gantt_chart(df_filtered)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown("### 📝 Tableau Éditable (500 lignes)")

        # NOUVELLE MÉTHODE : On travaille directement avec les colonnes texte sans conversion
        # Créer une copie pour l'affichage sans les colonnes Start_Date et End_Date
        df_edit = st.session_state.df_planning.copy()

        # S'assurer que toutes les colonnes nécessaires existent
        required_columns = ["Projet", "Jira", "Phase", "Tâche", "Équipe", "Début", "Fin"]
        for col in required_columns:
            if col not in df_edit.columns:
                df_edit[col] = ""

        # Garder l'ordre des colonnes
        df_edit = df_edit[required_columns]

        # Éditer le tableau avec 500 lignes
        edited_df = st.data_editor(
            df_edit, 
            num_rows="dynamic", 
            use_container_width=True, 
            height=500,
            key="data_editor",
            column_config={
                "Projet": st.column_config.TextColumn("Projet", width="large"),
                "Jira": st.column_config.TextColumn("Jira", width="small"),
                "Phase": st.column_config.TextColumn("Phase", width="small"),
                "Tâche": st.column_config.TextColumn("Tâche", width="medium"),
                "Équipe": st.column_config.TextColumn("Équipe", width="small"),
                "Début": st.column_config.TextColumn("Début", width="medium", help="Format: JJ/MM/AAAA ou JJ/MM/AAAA HH:MM"),
                "Fin": st.column_config.TextColumn("Fin", width="medium", help="Format: JJ/MM/AAAA ou JJ/MM/AAAA HH:MM"),
            }
        )

        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 4])
        with col1:
            if st.button("💾 Enregistrer", type="primary", use_container_width=True):
                # CORRECTION: Sauvegarder directement edited_df sans transformation
                st.session_state.df_planning = edited_df.copy()
                st.session_state.data_hash = None
                st.success("✅ Sauvegardé !")
                st.rerun()

        with col2:
            # Préparer les données pour l'export (avec les jours de la semaine)
            df_export = df_filtered.copy().sort_values('Start_Date')
            df_export["Début"] = df_export["Start_Date"].apply(format_with_day)
            df_export["Fin"] = df_export["End_Date"].apply(format_with_day)
            df_export_display = df_export[["Projet", "Jira", "Phase", "Tâche", "Équipe", "Début", "Fin"]]
            tsv_data = dataframe_to_tsv(df_export_display)
            st.download_button("📋 Copier (Excel)", tsv_data, "planning.tsv", "text/tab-separated-values", use_container_width=True)

        with col3:
            csv = df_export_display.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 CSV", csv, f"planning_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)

        with col4:
            if st.button("🗑️ Supprimer tout", use_container_width=True, type="secondary"):
                if st.session_state.get('confirm_delete', False):
                    # Créer un DataFrame vide avec les colonnes requises
                    st.session_state.df_planning = pd.DataFrame(columns=["Projet", "Jira", "Phase", "Tâche", "Équipe", "Début", "Fin"])
                    st.session_state.data_hash = None
                    st.session_state.confirm_delete = False
                    st.success("🗑️ Toutes les données ont été supprimées !")
                    st.rerun()
                else:
                    st.session_state.confirm_delete = True
                    st.warning("⚠️ Cliquez à nouveau pour confirmer la suppression")
                    st.rerun()

        with col5:
            if st.button("🔄 Réinitialiser", use_container_width=True):
                st.session_state.df_planning = pd.DataFrame(DEFAULT_DATA)
                st.session_state.data_hash = None
                st.session_state.selected_projects = []
                st.session_state.selected_teams = []
                st.session_state.selected_phases = []
                st.session_state.selected_tasks = []
                st.session_state.confirm_delete = False
                st.rerun()

        # Afficher un message si la confirmation de suppression est active
        if st.session_state.get('confirm_delete', False):
            st.error("⚠️ ATTENTION : Cliquez à nouveau sur 'Supprimer tout' pour confirmer la suppression définitive de toutes les données")

with tab2:
    st.subheader("📅 Vue Temporelle")
    df_cached = get_cached_df()

    if not df_cached.empty:
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        start_of_next_week = end_of_week + timedelta(days=1)
        end_of_next_week = start_of_next_week + timedelta(days=6)

        st.markdown(f"## 📍 Aujourd'hui - {today.strftime('%A %d/%m/%Y')}")
        tasks_today = df_cached[(df_cached['Start_Date'] <= pd.Timestamp(today)) & (df_cached['End_Date'] >= pd.Timestamp(today))]
        if not tasks_today.empty:
            for _, row in tasks_today.iterrows():
                emoji = "🚀 " if is_prod_task(row['Tâche']) else ""
                st.markdown(f"- {emoji}**{row['Projet']}** [{row['Jira']}] - {row['Tâche']} ({row['Équipe']})")
        else:
            st.info("Aucune tâche aujourd'hui")

        st.divider()
        st.markdown(f"## 📅 Cette semaine - {start_of_week.strftime('%d/%m')} au {end_of_week.strftime('%d/%m')}")
        tasks_week = df_cached[(df_cached['Start_Date'] <= pd.Timestamp(end_of_week)) & (df_cached['End_Date'] >= pd.Timestamp(start_of_week))]
        if not tasks_week.empty:
            for _, row in tasks_week.iterrows():
                emoji = "🚀 " if is_prod_task(row['Tâche']) else ""
                st.markdown(f"- {emoji}**{row['Projet']}** - {row['Tâche']} ({row['Équipe']})")
        else:
            st.info("Aucune tâche cette semaine")

        st.divider()
        st.markdown(f"## 📆 Semaine prochaine - {start_of_next_week.strftime('%d/%m')} au {end_of_next_week.strftime('%d/%m')}")
        tasks_next = df_cached[(df_cached['Start_Date'] <= pd.Timestamp(end_of_next_week)) & (df_cached['End_Date'] >= pd.Timestamp(start_of_next_week))]
        if not tasks_next.empty:
            for _, row in tasks_next.iterrows():
                emoji = "🚀 " if is_prod_task(row['Tâche']) else ""
                st.markdown(f"- {emoji}**{row['Projet']}** - {row['Tâche']} ({row['Équipe']})")
        else:
            st.info("Aucune tâche la semaine prochaine")

st.divider()
st.caption(f"PI Planning Tool v13.0 | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
