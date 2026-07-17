import streamlit as st
import pandas as pd
from common import (
    render_topbar, ICON_DOC, ICON_STAR, ICON_CHEVRON_RIGHT,
    get_reports_catalog, get_favorites
)

render_topbar("Version Production 5.2.1")

# ============================================================
# PAGE-LOCAL STYLE (scoped to Accueil only — doesn't touch
# common.py, so every other page keeps its current look)
# ============================================================

st.markdown(
    """
    <style>
    /* ---------------- HERO BANNER ---------------- */
    /* Dark slate-to-warm-ink gradient rather than blue/indigo,
       to stay visually connected to the app's existing ink/cream
       palette while still feeling bold. Kept short/thin per the
       brief so it doesn't push the dashboard down. */
    .hero-v2 {
        background: linear-gradient(135deg, #1C1B19 0%, #322F29 55%, #4A3B27 100%);
        border-radius: 16px;
        padding: 24px 36px;
        margin-bottom: 26px;
    }
    .hero-v2-greeting {
        font-family: 'Fraunces', serif; font-size: 24px; font-weight: 600;
        color: #FFFFFF; margin-bottom: 3px;
    }
    .hero-v2-sub { font-size: 14px; color: rgba(255,255,255,0.72); }

    /* ---------------- KPI CARDS ---------------- */
    .kpi-v2 {
        background: #FFFFFF; border: 1px solid var(--line);
        border-top: 4px solid var(--kpi-accent, var(--accent));
        border-radius: 14px; padding: 20px 20px 18px 20px; height: 100%;
        box-shadow: 0 4px 14px rgba(28,27,25,0.06);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-v2:hover { transform: translateY(-3px); box-shadow: 0 12px 26px rgba(28,27,25,0.11); }
    .kpi-v2.accent-blue   { border-top-color: #3B6FE0; }
    .kpi-v2.accent-green  { border-top-color: #1E9E6B; }
    .kpi-v2.accent-purple { border-top-color: #8A5CF6; }
    .kpi-v2.accent-red    { border-top-color: #E0473B; }

    .kpi-v2-icon  { font-size: 22px; margin-bottom: 10px; }
    .kpi-v2-label { font-size: 13px; color: var(--ink-soft); font-weight: 500; margin-bottom: 6px; }
    .kpi-v2-value { font-family: 'Fraunces', serif; font-size: 32px; font-weight: 600; color: var(--ink); margin-bottom: 10px; }

    .trend-pill {
        display: inline-flex; align-items: center; gap: 4px;
        font-size: 12px; font-weight: 700; padding: 3px 9px; border-radius: 20px;
    }
    .trend-pill.positive { background: #E7F6EE; color: #1E9E6B; }
    .trend-pill.negative { background: #FBE9E7; color: #E0473B; }
    .kpi-v2-caption { font-size: 11.5px; color: var(--ink-soft); margin-left: 6px; }

    /* ---------------- LIST PANELS (Rapports récents / Vos favoris) ---------------- */
    .panel-v2 {
        background: #FFFFFF; border: 1px solid var(--line); border-radius: 14px;
        padding: 22px 22px 12px 22px; height: 100%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .list-row-v2 {
        display: flex; align-items: center; gap: 12px;
        padding: 13px 10px; margin: 0 -10px 0 -10px;
        border-radius: 10px; border-bottom: 1px solid var(--line);
        transition: background 0.15s ease, transform 0.15s ease;
    }
    .list-row-v2:last-child { border-bottom: none; }
    .list-row-v2:hover { background: var(--card); transform: translateX(3px); }

    /* ---------------- FAVORITES PANEL (interactive) ---------------- */
    /* The panel is a real st.container(border=True, key="favoris_panel")
       so the remove button below can live inside it — a hand-written
       <div>...</div> spanning multiple st.markdown() calls would NOT
       actually wrap Streamlit widgets placed between them (they render
       as siblings, not children). */
    .st-key-favoris_panel [data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    /* The ✖ remove button — stripped of button chrome so it reads as
       a plain, subtle icon; reddens on hover to signal removal. */
    [class*="st-key-remove_fav_"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #B4AFA6 !important;
        padding: 0 !important;
        height: auto !important;
        min-height: 0 !important;
        font-size: 13px !important;
    }
    [class*="st-key-remove_fav_"] button:hover {
        color: #E0473B !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HERO BANNER
# ============================================================
# ASSUMPTION: "Noah" is a placeholder first name (matches the
# account used elsewhere in this app). Swap in a real value —
# e.g. from Snowflake's CURRENT_USER() or your auth/session
# state — once you have a proper identity source to pull from.

st.markdown(
    """
    <div class="hero-v2">
        <div class="hero-v2-greeting">Bonjour Noah !</div>
        <div class="hero-v2-sub">Voici l'état de vos rapports aujourd'hui.</div>
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

# "Vos favoris" now reflects real toggles from Liste des rapports
# (st.session_state.favorites), cross-referenced against the same
# shared reports catalog — not hardcoded mock data anymore.
favorites = get_favorites()
catalog = get_reports_catalog()
favorite_reports = catalog[catalog["numero"].isin(favorites)].rename(
    columns={"titre": "titre", "categorie": "categorie"}
)

kpis = [
    {"icon": "📈", "label": "Rapports générés ce mois", "value": "142",
     "trend_text": "▲ +12%", "trend_class": "positive", "accent": "accent-blue"},
    {"icon": "⏱️", "label": "Temps moyen d'exécution", "value": "1.8 s",
     "trend_text": "▼ -0.4 s", "trend_class": "positive", "accent": "accent-green"},
    {"icon": "⭐", "label": "Rapports favoris", "value": str(len(favorites)),
     "trend_text": "▲ +3", "trend_class": "positive", "accent": "accent-purple"},
    {"icon": "⚠️", "label": "Rapports en erreur", "value": "3",
     "trend_text": "▲ +2", "trend_class": "negative", "accent": "accent-red"},
]


def _remove_favorite(numero):
    """Removes a report from the shared favorites set (same
    st.session_state.favorites used by Liste des rapports), so
    unfavoriting here is instantly reflected there too."""
    favorites = get_favorites()
    favorites.discard(numero)
    st.rerun()

# ============================================================
# KPI CARDS
# ============================================================

kpi_cols = st.columns(4, gap="medium")

for col, kpi in zip(kpi_cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi-v2 {kpi['accent']}">
                <div class="kpi-v2-icon">{kpi['icon']}</div>
                <div class="kpi-v2-label">{kpi['label']}</div>
                <div class="kpi-v2-value">{kpi['value']}</div>
                <span class="trend-pill {kpi['trend_class']}">{kpi['trend_text']}</span>
                <span class="kpi-v2-caption">vs mois précédent</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div style="height:30px;"></div>', unsafe_allow_html=True)

# ============================================================
# TWO-COLUMN LIST PANELS
# ============================================================

left_col, right_col = st.columns(2, gap="large")

with left_col:
    rows_html = ""
    for _, r in recent_reports.iterrows():
        rows_html += (
            f'<div class="list-row-v2">'
            f'<div class="list-icon">{ICON_DOC}</div>'
            f'<div>'
            f'<div class="list-title">{r["titre"]}</div>'
            f'<div class="list-category">{r["categorie"]}</div>'
            f'</div>'
            f'<div class="list-meta">{r["quand"]}</div>'
            f'</div>'
        )

    st.markdown(
        f"""
        <div class="panel-v2">
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
    with st.container(border=True, key="favoris_panel"):
        st.markdown(
            f"""
            <div class="panel-header">
                <div class="panel-title font-serif">Vos favoris</div>
                <div class="panel-link">Voir tout {ICON_CHEVRON_RIGHT}</div>
            </div>
            <div class="panel-divider"></div>
            """,
            unsafe_allow_html=True,
        )

        if favorite_reports.empty:
            st.markdown(
                '<div style="padding:18px 4px; color:var(--ink-soft); font-size:13.5px;">'
                'Aucun rapport favori pour le moment. Cliquez sur ☆ dans '
                '<b>Liste des rapports</b> pour en ajouter.</div>',
                unsafe_allow_html=True,
            )
        else:
            for _, r in favorite_reports.iterrows():
                icon_col, text_col, remove_col = st.columns([0.6, 5, 0.6])

                with icon_col:
                    st.markdown(
                        f'<div class="list-icon starred">{ICON_STAR}</div>',
                        unsafe_allow_html=True,
                    )

                with text_col:
                    st.markdown(
                        f'<div class="list-title">{r["titre"]}</div>'
                        f'<div class="list-category">{r["categorie"]}</div>',
                        unsafe_allow_html=True,
                    )

                with remove_col:
                    st.button(
                        "✖",
                        key=f"remove_fav_{r['numero']}",
                        on_click=_remove_favorite,
                        args=(r["numero"],),
                        help="Retirer des favoris",
                    )

                st.markdown('<div class="panel-divider"></div>', unsafe_allow_html=True)