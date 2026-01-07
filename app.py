import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="PI Planning Editor v12.2", layout="wide")
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
    {"Projet": "Telco - Create new plans for T
