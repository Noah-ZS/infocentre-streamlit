"""
Router / entrypoint for the Infocentre app.
Run with: streamlit run streamlit_app.py

Owns the ONE allowed call to st.set_page_config(), injects the
global CSS once, declares every page via st.Page, renders the
shared custom sidebar, then hands off to whichever page is active.
"""

import streamlit as st
from common import inject_global_css, render_sidebar

# 1. Page Config
st.set_page_config(page_title="Infocentre", layout="wide")

# 2. Inject your global tokens
inject_global_css()

# 3. BULLETPROOF TOP-SPACE REMOVER (For Streamlit 1.36+)
# We place this here so it is guaranteed to inject on every single page switch.
st.markdown("""
    <style>
    /* Target all known Streamlit main wrappers for modern versions */
    .block-container, 
    [data-testid="stMainBlockContainer"], 
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 1.5rem !important; /* Pulls content to the very top */
        padding-bottom: 2rem !important;
        margin-top: 0 !important;
    }
    
    /* Completely nuke the native header block */
    header, 
    [data-testid="stHeader"], 
    .stAppHeader {
        display: none !important;
        height: 0px !important;
        min-height: 0px !important;
        visibility: hidden !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# PAGES
# ------------------------------------------------------------

accueil_page = st.Page(
    "pages/accueil.py", title="Accueil", icon=":material/home:",
    url_path="accueil", default=True
)
rapports_page = st.Page(
    "pages/liste_des_rapports.py", title="Liste des rapports", icon=":material/description:",
    url_path="liste-des-rapports"
)
suivi_page = st.Page(
    "pages/suivi_exploit.py", title="Suivi de l'exploit", icon=":material/monitoring:",
    url_path="suivi-exploit"
)
open_to_buy_page = st.Page(
    "pages/open_to_buy.py", title="Open to buy", icon=":material/shopping_bag:",
    url_path="open-to-buy"
)
password_page = st.Page(
    "pages/changer_mot_de_passe.py", title="Changer votre mot de passe", icon=":material/lock_reset:",
    url_path="changer-mot-de-passe"
)

# Registered for routing/deep-linking but NOT shown in the main
# sidebar nav list — each is opened as an in-app tab from within
# liste_des_rapports.py by clicking its report row.
article_coloris_page = st.Page(
    "pages/article_coloris.py",
    title="Article - Liste des Coloris / Taille",
    url_path="article-coloris"
)
mesures_produits_page = st.Page(
    "pages/mesures_produits.py",
    title="Mesures des Nouveaux Produits",
    url_path="mesures-produits"
)
commandes_detail_page = st.Page(
    "pages/commandes_detail.py",
    title="Commandes - Détail",
    url_path="commandes-detail"
)

NAV_ITEMS = [
    {"page": accueil_page, "label": "Accueil", "icon": ":material/home:"},
    {"page": rapports_page, "label": "Liste des rapports", "icon": ":material/description:"},
    {"page": suivi_page, "label": "Suivi de l'exploit", "icon": ":material/monitoring:"},
    {"page": open_to_buy_page, "label": "Open to buy", "icon": ":material/shopping_bag:"},
    {"page": password_page, "label": "Changer votre mot de passe", "icon": ":material/lock_reset:"},
]

pg = st.navigation(
    [
        accueil_page, rapports_page, suivi_page, open_to_buy_page, password_page,
        article_coloris_page, mesures_produits_page, commandes_detail_page,
    ],
    position="hidden",
)

render_sidebar(NAV_ITEMS)

pg.run()