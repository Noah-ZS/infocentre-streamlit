import streamlit as st
import pandas as pd
from common import (
    render_topbar, ICON_DOC, ICON_CLOCK, ICON_STAR,
    ICON_ARROW_UP, ICON_ARROW_DOWN, ICON_CHEVRON_RIGHT
)

render_topbar("Version Production 5.2.1")

# ============================================================
# HERO BANNER
# (soft gradient background; margin-bottom is negative so the
# KPI row below visually overlaps its bottom edge)
# ============================================================

st.markdown(
    """
    <div class="hero-banner">
        <div class="page-title font-serif">Bienvenue sur votre Infocentre</div>
        <div class="page-subtitle">Votre portail de Business Intelligence dédié à la performance.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# MOCK DATA
# ============================================================

recent_reports = pd.DataFrame([
    {"titre": "Commandes - Détail", "categorie": "Gestion Commerciale", "quand": "Il y a 2 h"},
    {"titre": "Article - Liste des coloris / Taille", "categorie": "Référentiel Article", "quand": "Il y a 5 h"},
    {"titre": "Stock Disponible - Dépôt", "categorie": "Gestion Commerciale", "quand": "Hier"},
    {"titre": "Expéditions - Détail", "categorie": "Gestion Commerciale", "quand": "Hier"},
    {"titre": "Factures - CA Consolidation (J-1)", "categorie": "Gestion Financière", "quand": "Il y a 2 jours"},
])

favorite_reports = pd.DataFrame([
    {"titre": "Commande - Détail", "categorie": "Gestion Commerciale"},
    {"titre": "Article - Emballage", "categorie": "Référentiel Article"},
    {"titre": "Suivi de l'exploit", "categorie": "Production"},
    {"titre": "Open to buy - Synthèse", "categorie": "Pilotage"},
    {"titre": "Ventes - Par pays", "categorie": "Gestion Commerciale"},
])

kpis = [
    {"label": "Rapports générés ce mois", "value": "142", "delta": "+12% vs mois précédent", "trend": "up", "icon": ICON_DOC},
    {"label": "Temps moyen d'exécution", "value": "1.8 s", "delta": "-0.4 s vs mois précédent", "trend": "down", "icon": ICON_CLOCK},
    {"label": "Rapports favoris", "value": "18", "delta": "+3 vs mois précédent", "trend": "up", "icon": ICON_STAR},
]

# ============================================================
# KPI CARDS (overlapping the hero's bottom edge)
# ============================================================

kpi_cols = st.columns(3, gap="medium")

for col, kpi in zip(kpi_cols, kpis):
    arrow = ICON_ARROW_UP if kpi["trend"] == "up" else ICON_ARROW_DOWN
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">{kpi['icon']}</div>
                <div class="kpi-label">{kpi['label']}</div>
                <div class="kpi-value font-serif">{kpi['value']}</div>
                <div class="kpi-delta">{kpi['delta']} {arrow}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div style="height:34px;"></div>', unsafe_allow_html=True)

# ============================================================
# TWO-COLUMN LIST PANELS
# ============================================================

left_col, right_col = st.columns(2, gap="large")

with left_col:
    rows_html = ""
    for _, r in recent_reports.iterrows():
        rows_html += f"""
        <div class="list-row">
            <div class="list-icon">{ICON_DOC}</div>
            <div>
                <div class="list-title">{r['titre']}</div>
                <div class="list-category">{r['categorie']}</div>
            </div>
            <div class="list-meta">{r['quand']}</div>
        </div>
        """

    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-header">
                <div class="panel-title font-serif">Rapports récents</div>
                <div class="panel-link">Voir tout {ICON_CHEVRON_RIGHT}</div>
            </div>
            <div class="panel-divider"></div>
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    rows_html = ""
    for _, r in favorite_reports.iterrows():
        rows_html += f"""
        <div class="list-row">
            <div class="list-icon starred">{ICON_STAR}</div>
            <div>
                <div class="list-title">{r['titre']}</div>
                <div class="list-category">{r['categorie']}</div>
            </div>
        </div>
        """

    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-header">
                <div class="panel-title font-serif">Vos favoris</div>
                <div class="panel-link">Voir tout {ICON_CHEVRON_RIGHT}</div>
            </div>
            <div class="panel-divider"></div>
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True,
    )