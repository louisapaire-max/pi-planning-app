import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

st.set_page_config(page_title="PI Planning - Capacity Tool v9.2", layout="wide")
st.title("📊 PI Planning - Capacity Planning avec Import Excel")

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
    "Dev Manager": "#4CAF50", "QA": "#8E44AD", "Traduction": "#1ABC9C"
}

# DONNÉES PAR DÉFAUT (CORRIGÉES GUIDELINES 2026)
DEFAULT_PLANNING = """PROJET 1: Email - Add File Edition to Zimbra Pro
Jira: LVL2-18232
Phase	Tâche	Équipe	Début	Fin
DESIGN	Documentation Projet	PO	02/02/2026	20/02/2026
DESIGN	Etude d'impact	PO	04/02/2026	04/02/2026
DESIGN	Refinement	PO	11/02/2026	11/02/2026
DEV	Dev Website	Dev Front/Back	23/02/2026	13/03/2026
DEV	PROD	PO	12/03/2026 09:00	12/03/2026 18:00
PROJET 2: Website Revamp - homepage telephony
Jira: LVL2-18282
Phase	Tâche	Équipe	Début	Fin
DESIGN	Documentation Projet	PO	12/01/2026	30/01/2026
DESIGN	Etude d'impact	PO	14/01/2026	14/01/2026
DESIGN	Refinement	PO	21/01/2026	21/01/2026
DEV	Dev Website	Dev Front/Back	02/02/2026	20/02/2026
DEV	PROD	PO	19/02/2026 09:00	19/02/2026 18:00
PROJET 4: Zimbra : add yearly commitment (prod)
Jira: LVL2-18237
Phase	Tâche	Équipe	Début	Fin
DESIGN	Documentation Projet	PO	23/02/2026	13/03/2026
DESIGN	Etude d'impact	PO	25/02/2026	25/02/2026
DESIGN	Refinement	PO	04/03/2026	04/03/2026
DEV	Dev Website	Dev Front/Back	16/03/2026	20/03/2026
DEV	PROD	PO	19/03/2026 09:00	19/03/2026 18:00"""

# SESSION STATE
if "imported_data" not in st.session_state:
    st.session_state.imported_data = None

# FONCTIONS DE PARSING
def parse_date_with_hours(date_str):
    date_str = str(date_str).strip()
    for fmt in ['%d/%m/%Y %H:%M', '%d/%m/%Y']:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except:
            continue
    return pd.NaT

def parse_excel_paste(text_data):
    lines = text_data.strip().split('\n')
    all_data = []
    current_project, current_jira = None, None
    for line in lines:
        line = line.strip()
        if not line: continue
        if 'PROJET' in line and ':' in line:
            current_project = line.split(':', 1)[1].strip()
            continue
        if line.startswith('Jira:'):
            current_jira = line.replace('Jira:', '').strip()
            continue
        if 'Phase' in line and 'Tâche' in line: continue
        parts = [p.strip() for p in (line.split('\t') if '\t' in line else line.split('|')) if p.stri
