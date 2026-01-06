import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="PI Planning Editor v11.1", layout="wide")
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
    # PROJET 1: Email - Zimbra Pro (Design Iter#3, Dev Iter#4)
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DESIGN", "Tâche": "Maquettes/Wireframe", "Équipe": "Design", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "11/02/2026", "Fin": "11/02/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DEV", "Tâche": "QA & UAT", "Équipe": "QA", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Email - Add File Edition to Zimbra Pro", "Jira": "LVL2-18232", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/03/2026 09:00", "Fin": "12/03/2026 18:00"},
    
    # PROJET 2: Website Revamp - homepage telephony (Design Iter#2, Dev Iter#3)
    {"Projet": "Website Revamp - homepage telephony", "Jira": "LVL2-18282", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "12/01/2026", "Fin": "30/01/2026"},
    {"Projet": "Website Revamp - homepage telephony", "Jira": "LVL2-18282", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "14/01/2026", "Fin": "14/01/2026"},
    {"Projet": "Website Revamp - homepage telephony", "Jira": "LVL2-18282", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "21/01/2026", "Fin": "21/01/2026"},
    {"Projet": "Website Revamp - homepage telephony", "Jira": "LVL2-18282", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Website Revamp - homepage telephony", "Jira": "LVL2-18282", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/02/2026 09:00", "Fin": "19/02/2026 18:00"},
    
    # PROJET 3: VPS - Add more choice on Disk options (Design Iter#2, Dev Iter#3)
    {"Projet": "VPS - Add more choice on Disk options", "Jira": "LVL2-16718", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "12/01/2026", "Fin": "30/01/2026"},
    {"Projet": "VPS - Add more choice on Disk options", "Jira": "LVL2-16718", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "14/01/2026", "Fin": "14/01/2026"},
    {"Projet": "VPS - Add more choice on Disk options", "Jira": "LVL2-16718", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "21/01/2026", "Fin": "21/01/2026"},
    {"Projet": "VPS - Add more choice on Disk options", "Jira": "LVL2-16718", "Phase": "DEV", "Tâche": "Dev Order", "Équipe": "Dev Order", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "VPS - Add more choice on Disk options", "Jira": "LVL2-16718", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/02/2026 09:00", "Fin": "19/02/2026 18:00"},
    
    # PROJET 4: Zimbra yearly commitment (Design Iter#4, Dev Iter#5)
    {"Projet": "Zimbra : add yearly commitment", "Jira": "LVL2-18237", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Zimbra : add yearly commitment", "Jira": "LVL2-18237", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "Zimbra : add yearly commitment", "Jira": "LVL2-18237", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "Zimbra : add yearly commitment", "Jira": "LVL2-18237", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "Zimbra : add yearly commitment", "Jira": "LVL2-18237", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    
    # PROJET 5: Telco Trunk (Design Iter#4, Dev Iter#5)
    {"Projet": "Telco - Create new plans for Trunk", "Jira": "LVL2-18063", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Telco - Create new plans for Trunk", "Jira": "LVL2-18063", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "Telco - Create new plans for Trunk", "Jira": "LVL2-18063", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "Telco - Create new plans for Trunk", "Jira": "LVL2-18063", "Phase": "DEV", "Tâche": "Dev Order", "Équipe": "Dev Order", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "Telco - Create new plans for Trunk", "Jira": "LVL2-18063", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    
    # PROJET 6: Funnel order (Design Iter#3, Dev Iter#4)
    {"Projet": "Funnel order improvement", "Jira": "LVL2-19317", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Funnel order improvement", "Jira": "LVL2-19317", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "Funnel order improvement", "Jira": "LVL2-19317", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "11/02/2026", "Fin": "11/02/2026"},
    {"Projet": "Funnel order improvement", "Jira": "LVL2-19317", "Phase": "DEV", "Tâche": "Dev Order", "Équipe": "Dev Order", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Funnel order improvement", "Jira": "LVL2-19317", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/03/2026 09:00", "Fin": "12/03/2026 18:00"},
    
    # PROJET 7: VPS RBX7 (Cycle court Iter#3)
    {"Projet": "VPS 2026 RBX7", "Jira": "LVL2-18432", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "VPS 2026 RBX7", "Jira": "LVL2-18432", "Phase": "DEV", "Tâche": "Dev Order", "Équipe": "Dev Order", "Début": "09/02/2026", "Fin": "10/02/2026"},
    {"Projet": "VPS 2026 RBX7", "Jira": "LVL2-18432", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/02/2026 09:00", "Fin": "12/02/2026 18:00"},
    
    # PROJET 8: Phone & Headset (Design Iter#4, Dev Iter#5)
    {"Projet": "lot 2 website page Phone & Headset", "Jira": "LVL2-18859", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "lot 2 website page Phone & Headset", "Jira": "LVL2-18859", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "lot 2 website page Phone & Headset", "Jira": "LVL2-18859", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "lot 2 website page Phone & Headset", "Jira": "LVL2-18859", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "lot 2 website page Phone & Headset", "Jira": "LVL2-18859", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    
    # PROJET 9: Numbers page (Design Iter#3, Dev Iter#4)
    {"Projet": "Website Revamp - numbers page", "Jira": "LVL2-15863", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "Website Revamp - numbers page", "Jira": "LVL2-15863", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "Website Revamp - numbers page", "Jira": "LVL2-15863", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "11/02/2026", "Fin": "11/02/2026"},
    {"Projet": "Website Revamp - numbers page", "Jira": "LVL2-15863", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Website Revamp - numbers page", "Jira": "LVL2-15863", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/03/2026 09:00", "Fin": "12/03/2026 18:00"},
    
    # PROJET 10: VOIP Destinations (Design Iter#3, Dev Iter#4)
    {"Projet": "VOIP Offers - Update 40 Destinations", "Jira": "LVL2-18408", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "02/02/2026", "Fin": "20/02/2026"},
    {"Projet": "VOIP Offers - Update 40 Destinations", "Jira": "LVL2-18408", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "04/02/2026", "Fin": "04/02/2026"},
    {"Projet": "VOIP Offers - Update 40 Destinations", "Jira": "LVL2-18408", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "11/02/2026", "Fin": "11/02/2026"},
    {"Projet": "VOIP Offers - Update 40 Destinations", "Jira": "LVL2-18408", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "VOIP Offers - Update 40 Destinations", "Jira": "LVL2-18408", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "12/03/2026 09:00", "Fin": "12/03/2026 18:00"},
    
    # PROJET 11: Zimbra Webmail (Design Iter#4, Dev Iter#5)
    {"Projet": "Email - Quick Wins - Zimbra Webmail", "Jira": "LVL2-18562", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Email - Quick Wins - Zimbra Webmail", "Jira": "LVL2-18562", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "Email - Quick Wins - Zimbra Webmail", "Jira": "LVL2-18562", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "Email - Quick Wins - Zimbra Webmail", "Jira": "LVL2-18562", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "Email - Quick Wins - Zimbra Webmail", "Jira": "LVL2-18562", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    
    # PROJET 12: Exchange Product pages (Design Iter#4, Dev Iter#5)
    {"Projet": "Email - Quick Wins - Exchange Pages", "Jira": "LVL2-18598", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Email - Quick Wins - Exchange Pages", "Jira": "LVL2-18598", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "Email - Quick Wins - Exchange Pages", "Jira": "LVL2-18598", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "Email - Quick Wins - Exchange Pages", "Jira": "LVL2-18598", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "Email - Quick Wins - Exchange Pages", "Jira": "LVL2-18598", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    
    # PROJET 13: VPS Application pages (Design Iter#4, Dev Iter#5)
    {"Projet": "VPS - Website Application New pages", "Jira": "LVL2-16407", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "VPS - Website Application New pages", "Jira": "LVL2-16407", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "VPS - Website Application New pages", "Jira": "LVL2-16407", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "VPS - Website Application New pages", "Jira": "LVL2-16407", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "VPS - Website Application New pages", "Jira": "LVL2-16407", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    
    # PROJET 14: Web Cloud Migrate (Design Iter#4, Dev Iter#5)
    {"Projet": "Revamp Web Cloud - Migrate P1", "Jira": "LVL2-19319", "Phase": "DESIGN", "Tâche": "Documentation Projet", "Équipe": "PO", "Début": "23/02/2026", "Fin": "13/03/2026"},
    {"Projet": "Revamp Web Cloud - Migrate P1", "Jira": "LVL2-19319", "Phase": "DESIGN", "Tâche": "Etude d'impact", "Équipe": "PO", "Début": "25/02/2026", "Fin": "25/02/2026"},
    {"Projet": "Revamp Web Cloud - Migrate P1", "Jira": "LVL2-19319", "Phase": "DESIGN", "Tâche": "Refinement", "Équipe": "PO", "Début": "04/03/2026", "Fin": "04/03/2026"},
    {"Projet": "Revamp Web Cloud - Migrate P1", "Jira": "LVL2-19319", "Phase": "DEV", "Tâche": "Dev Website", "Équipe": "Dev Front/Back", "Début": "16/03/2026", "Fin": "20/03/2026"},
    {"Projet": "Revamp Web Cloud - Migrate P1", "Jira": "LVL2-19319", "Phase": "DEV", "Tâche": "PROD", "Équipe": "PO", "Début": "19/03/2026 09:00", "Fin": "19/03/2026 18:00"},
    
    # PROJET 15: Telephony revamp (Design Iter#3, Dev Iter#4)
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

# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════
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

def format_with_day(dt):
    """Formate une date avec le jour de la semaine"""
    if pd.isna(dt):
        return ""
    weekday_map = {
        0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi",
        4: "Vendredi", 5: "Samedi", 6: "Dimanche"
    }
    day = weekday_map[int(dt.weekday())]
    if dt.hour == 0 and dt.minute == 0:
        return f"{day} {dt.strftime('%d/%m/%Y')}"
    return f"{day} {dt.strftime('%d/%m/%Y %H:%M')}"

def create_gantt_chart(df_source):
    """Crée un Gantt optimisé avec groupement et jalons"""
    if df_source.empty:
        return None
    
    df = df_source.copy()
    df['Start_Date'] = df['Début'].apply(parse_date_safe)
    df['End_Date'] = df['Fin'].apply(parse_date_safe)
    df = df.dropna(subset=['Start_Date', 'End_Date'])
    
    if df.empty:
        return None
    
    # Correction tâches d'un jour
    same_day = df['Start_Date'].dt.date == df['End_Date'].dt.date
    no_hours = (df['Start_Date'].dt.hour == 0) & (df['End_Date'].dt.hour == 0)
    mask = same_day & no_hours
    df.loc[mask, 'Start_Date'] += pd.Timedelta(hours=9)
    df.loc[mask, 'End_Date'] += pd.Timedelta(hours=18)
    
    # TRI PAR DATE DE DÉBUT
    df = df.sort_values(['Start_Date', 'Projet', 'Phase'])
    
    # Labels hiérarchiques
    df['Projet_Court'] = df['Projet'].apply(lambda x: x[:35] + '...' if len(x) > 35 else x)
    df['Label_Hiérarchique'] = df['Projet_Court'] + ' | ' + df['Phase'] + ' | ' + df['Tâche']
    
    # Identification jalons (SEULEMENT pour PROD exactement)
    df['Type_Tache'] = df['Tâche'].apply(lambda x: 
        '🎯 JALON' if str(x).strip().upper() == 'PROD' else 'Tâche')
    
    # Durée en jours
    df['Durée_Jours'] = (df['End_Date'] - df['Start_Date']).dt.days + 1
    
    # Création Gantt
    fig = px.timeline(
        df,
        x_start='Start_Date',
        x_end='End_Date',
        y='Label_Hiérarchique',
        color='Équipe',
        color_discrete_map=TEAM_COLORS,
        hover_data={
            'Projet': True,
            'Jira': True,
            'Phase': True,
            'Type_Tache': True,
            'Durée_Jours': True,
            'Label_Hiérarchique': False,
            'Start_Date': False,
            'End_Date': False
        },
        title='<b>📊 Planning Q2 2026 - Vue Gantt Hiérarchique</b>',
        height=max(700, len(df) * 40)
    )
    
    # Itérations avec dégradés (annotations plus petites)
    colors_bg = [
        "rgba(230, 230, 250, 0.25)",
        "rgba(200, 230, 255, 0.3)",
        "rgba(220, 255, 220, 0.3)",
        "rgba(255, 240, 220, 0.3)",
        "rgba(255, 220, 255, 0.25)"
    ]
    
    for i, it in enumerate(ITERATIONS):
        fig.add_vrect(
            x0=it["start"], x1=it["end"],
            fillcolor=colors_bg[i % len(colors_bg)],
            layer="below", line_width=0,
            annotation_text=f"<b>{it['name']}</b>",
            annotation_position="top left",
            annotation_font=dict(size=8, color="darkblue", family="Arial")
        )
        fig.add_vline(
            x=it["end"], 
            line_width=1, 
            line_dash="dash", 
            line_color="rgba(100,100,100,0.4)"
        )
    
    # Grille hebdomadaire
    start_date = df['Start_Date'].min()
    end_date = df['End_Date'].max()
    
    start_monday = start_date - pd.Timedelta(days=start_date.weekday())
    end_sunday = end_date + pd.Timedelta(days=(6 - end_date.weekday()))
    
    date_range = pd.date_range(
        start=start_monday, 
        end=end_sunday, 
        freq='W-MON'
    )
    
    for monday in date_range:
        fig.add_vline(
            x=monday.isoformat(), 
            line_width=0.5, 
            line_dash="dot", 
            line_color="rgba(150,150,150,0.3)"
        )
    
    # Ligne "Aujourd'hui" (plus discrète)
    today = datetime.now().date().isoformat()
    fig.add_shape(
        type="line", x0=today, x1=today, y0=0, y1=1,
        yref="paper", 
        line=dict(color="rgba(255, 100, 100, 0.7)", width=2, dash="dash")
    )
    fig.add_annotation(
        x=today, y=1.01, yref="paper",
        text=f"Aujourd'hui ({datetime.now().strftime('%d/%m')})", 
        showarrow=False,
        font=dict(size=9, color="rgba(200, 50, 50, 0.8)", family="Arial"),
        bgcolor="rgba(255,255,255,0.7)",
        bordercolor="rgba(255, 100, 100, 0.5)",
        borderwidth=1
    )
    
    # Axes
    fig.update_xaxes(
        title="<b>Calendrier 2026</b>",
        tickformat="%d/%m",
        dtick=86400000.0 * 7,
        side="top",
        tickfont=dict(size=10, color="darkblue"),
        tickangle=-45,
        rangebreaks=[dict(bounds=["sat", "mon"])],
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(200,200,200,0.3)"
    )
    
    fig.update_yaxes(
        title="<b>Tâches (par date de début)</b>",
        autorange="reversed",
        tickfont=dict(size=9),
        showgrid=True,
        gridwidth=0.5,
        gridcolor="rgba(200,200,200,0.2)"
    )
    
    # Layout professionnel
    fig.update_layout(
        showlegend=True,
        legend=dict(
            title="<b>Équipes</b>",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="gray",
            borderwidth=1
        ),
        margin=dict(t=120, b=80, l=500, r=200),
        plot_bgcolor='rgba(250,250,250,1)',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=11),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    # Annotations PROD (SEULEMENT pour les tâches "PROD" exactement)
    prods = df[df['Tâche'].str.strip().str.upper() == 'PROD']
    for idx, row in prods.iterrows():
        fig.add_annotation(
            x=row['End_Date'],
            y=row['Label_Hiérarchique'],
            text="🚀",
            showarrow=False,
            font=dict(size=20),
            xshift=15
        )
    
    return fig

def get_tasks_for_period(df, start_date, end_date):
    """Retourne les tâches actives dans une période donnée"""
    df_copy = df.copy()
    df_copy['Start_Date'] = df_copy['Début'].apply(parse_date_safe)
    df_copy['End_Date'] = df_copy['Fin'].apply(parse_date_safe)
    df_copy = df_copy.dropna(subset=['Start_Date', 'End_Date'])
    
    # Tâches qui se chevauchent avec la période
    mask = (df_copy['Start_Date'] <= end_date) & (df_copy['End_Date'] >= start_date)
    return df_copy[mask].sort_values('Start_Date')

# ═══════════════════════════════════════════════════════════
# INTERFACE UTILISATEUR
# ═══════════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["📊 Planning & Gantt", "📅 Vue Temporelle"])

# TAB 1: PLANNING PRINCIPAL
with tab1:
    st.subheader("📊 Visualisation Gantt et Tableau des Tâches")
    
    if not st.session_state.df_planning.empty:
        # Métriques
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📁 Projets", st.session_state.df_planning['Projet'].nunique())
        with col2:
            st.metric("📝 Tâches", len(st.session_state.df_planning))
        with col3:
            st.metric("👥 Équipes", st.session_state.df_planning['Équipe'].nunique())
        with col4:
            prod_count = st.session_state.df_planning[
                st.session_state.df_planning['Tâche'].str.strip().str.upper() == 'PROD'
            ].shape[0]
            st.metric("🚀 Livraisons", prod_count)
        
        st.divider()
        
        # Filtres
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            all_projects = sorted(st.session_state.df_planning['Projet'].unique())
            selected_projects = st.multiselect(
                "🔍 Projets", 
                all_projects, 
                default=all_projects
            )
        with col_f2:
            all_teams = sorted(st.session_state.df_planning['Équipe'].unique())
            selected_teams = st.multiselect(
                "👥 Équipes", 
                all_teams, 
                default=all_teams
            )
        with col_f3:
            all_phases = sorted(st.session_state.df_planning['Phase'].unique())
            selected_phases = st.multiselect(
                "⚙️ Phases", 
                all_phases, 
                default=all_phases
            )
        with col_f4:
            all_tasks = sorted(st.session_state.df_planning['Tâche'].unique())
            selected_tasks = st.multiselect(
                "📋 Tâches", 
                all_tasks, 
                default=all_tasks
            )
        
        # Appliquer filtres
        df_filtered = st.session_state.df_planning[
            (st.session_state.df_planning['Projet'].isin(selected_projects)) &
            (st.session_state.df_planning['Équipe'].isin(selected_teams)) &
            (st.session_state.df_planning['Phase'].isin(selected_phases)) &
            (st.session_state.df_planning['Tâche'].isin(selected_tasks))
        ]
        
        st.info(f"📊 **{len(df_filtered)}** tâches affichées / **{len(st.session_state.df_planning)}** total")
        
        # Gantt
        st.markdown("### 📊 Diagramme de Gantt")
        fig = create_gantt_chart(df_filtered)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Aucune donnée valide (vérifiez les dates)")
        
        st.divider()
        
        # Tableau Excel éditable
        st.markdown("### 📝 Tableau des Tâches (Éditable)")
        
        df_view = df_filtered.copy()
        df_view["Start_Date"] = df_view["Début"].apply(parse_date_safe)
        df_view["End_Date"] = df_view["Fin"].apply(parse_date_safe)
        df_view = df_view.sort_values('Start_Date')
        df_view["Début"] = df_view["Start_Date"].apply(format_with_day)
        df_view["Fin"] = df_view["End_Date"].apply(format_with_day)
        df_view = df_view.drop(columns=["Start_Date", "End_Date"])
        
        edited_df = st.data_editor(
            df_view,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Projet": st.column_config.TextColumn("Projet", width="large"),
                "Jira": st.column_config.TextColumn("Jira", width="small"),
                "Phase": st.column_config.SelectboxColumn("Phase", options=["DESIGN", "DEV"], required=True),
                "Tâche": st.column_config.TextColumn("Tâche", width="medium"),
                "Équipe": st.column_config.SelectboxColumn("Équipe", options=list(TEAM_COLORS.keys()), required=True),
                "Début": st.column_config.TextColumn("Début"),
                "Fin": st.column_config.TextColumn("Fin"),
            },
            hide_index=False,
            key="data_editor",
            height=400
        )
        
        col1, col2, col3 = st.columns([2, 2, 6])
        with col1:
            if st.button("💾 Enregistrer", type="primary", use_container_width=True):
                st.session_state.df_planning = edited_df.copy()
                st.success("✅ Sauvegardé !")
                st.rerun()
        
        with col2:
            csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV",
                data=csv,
                file_name=f"planning_Q2_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            if st.button("🔄 Réinitialiser", use_container_width=True):
                st.session_state.df_planning = pd.DataFrame(DEFAULT_DATA)
                st.rerun()

# TAB 2: VUE TEMPORELLE
with tab2:
    st.subheader("📅 Vue Temporelle - Aujourd'hui, Cette Semaine, Semaine Prochaine")
    
    if not st.session_state.df_planning.empty:
        today = datetime.now().date()
        
        # Calcul des périodes
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        start_of_next_week = end_of_week + timedelta(days=1)
        end_of_next_week = start_of_next_week + timedelta(days=6)
        
        today_dt = pd.Timestamp(today)
        start_week_dt = pd.Timestamp(start_of_week)
        end_week_dt = pd.Timestamp(end_of_week)
        start_next_dt = pd.Timestamp(start_of_next_week)
        end_next_dt = pd.Timestamp(end_of_next_week)
        
        # Tâches aujourd'hui
        st.markdown(f"## 📍 Aujourd'hui - {today.strftime('%A %d/%m/%Y')}")
        tasks_today = get_tasks_for_period(st.session_state.df_planning, today_dt, today_dt)
        
        if not tasks_today.empty:
            for _, row in tasks_today.iterrows():
                emoji = "🚀 " if row['Tâche'].strip().upper() == 'PROD' else ""
                st.markdown(f"- {emoji}**{row['Projet']}** [{row['Jira']}] - *{row['Phase']}* - {row['Tâche']} ({row['Équipe']})")
        else:
            st.info("Aucune tâche prévue aujourd'hui")
        
        st.divider()
        
        # Tâches cette semaine
        st.markdown(f"## 📅 Cette semaine - du {start_of_week.strftime('%d/%m')} au {end_of_week.strftime('%d/%m/%Y')}")
        tasks_week = get_tasks_for_period(st.session_state.df_planning, start_week_dt, end_week_dt)
        
        if not tasks_week.empty:
            for _, row in tasks_week.iterrows():
                start_str = format_with_day(row['Start_Date'])
                end_str = format_with_day(row['End_Date'])
                emoji = "🚀 " if row['Tâche'].strip().upper() == 'PROD' else ""
                st.markdown(f"- {emoji}**{row['Projet']}** [{row['Jira']}] - *{row['Phase']}* - {row['Tâche']} ({row['Équipe']}) | {start_str} → {end_str}")
        else:
            st.info("Aucune tâche prévue cette semaine")
        
        st.divider()
        
        # Tâches semaine prochaine
        st.markdown(f"## 📆 Semaine prochaine - du {start_of_next_week.strftime('%d/%m')} au {end_of_next_week.strftime('%d/%m/%Y')}")
        tasks_next = get_tasks_for_period(st.session_state.df_planning, start_next_dt, end_next_dt)
        
        if not tasks_next.empty:
            for _, row in tasks_next.iterrows():
                start_str = format_with_day(row['Start_Date'])
                end_str = format_with_day(row['End_Date'])
                emoji = "🚀 " if row['Tâche'].strip().upper() == 'PROD' else ""
                st.markdown(f"- {emoji}**{row['Projet']}** [{row['Jira']}] - *{row['Phase']}* - {row['Tâche']} ({row['Équipe']}) | {start_str} → {end_str}")
        else:
            st.info("Aucune tâche prévue la semaine prochaine")

st.divider()
st.caption(f"PI Planning Tool v11.1 | Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
