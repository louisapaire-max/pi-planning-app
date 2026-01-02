import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from workalendar.europe import France

# ═════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="PI Planning - Capacity Tool", layout="wide")
st.title("📊 PI Planning - Capacity Planning avec ETA")

# Vérification rapide de l'import plotly
try:
    import plotly.express as px
except ImportError:
    st.error("Le module 'plotly' est manquant. Installez-le via pip install plotly")
    st.stop()

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

TASK_STATUSES = ["À faire", "En cours", "Terminé", "Bloqué", "En attente"]

# ═════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ════════════════════════════════════════════════
