import streamlit as st
import pandas as pd
from common import (
    render_topbar,
    ICON_DOC,
    ICON_STAR,
    ICON_SEARCH,
    ICON_FOLDER,
    ICON_FILTER,
    ICON_CHEVRON_DOWN,
    ICON_CHEVRON_RIGHT,
    ICON_INFO,
    ICON_LIST_VIEW,
    ICON_GRID_VIEW,
    ICON_SETTINGS,
    ICON_KEBAB,
)
from report_views import render_article_coloris_view

render_topbar("Production M3 13.4")

st.markdown(
    '<div class="page-title font-serif">Liste des rapports</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-subtitle">Accédez à l\'ensemble des rapports disponibles et analysez vos données.</div>',
    unsafe_allow_html=True,
)

# ============================================================
# SCOPED STYLE FIXES
# Targets only the search row and the report table rows via
# Streamlit's st.container(key=...) -> ".st-key-<name>" class,
# so nothing else on the page is affected.
# ============================================================

st.markdown(
    """
    <style>
    /* ---- Search row: align input + button on the same baseline ---- */
    .st-key-report_search_row [data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    .st-key-report_search_row div.lr-search-btn {
        margin: 0 !important;
    }
    .st-key-report_search_row .stTextInput,
    .st-key-report_search_row .stButton {
        margin: 0 !important;
    }
    .st-key-report_search_row .stTextInput input {
        height: 42px;
    }
    .st-key-report_search_row .stButton > button {
        height: 42px;
    }

    /* ---- Report table: tighter row height ---- */
    .st-key-rl_table_rows [data-testid="stVerticalBlock"] {
        gap: 0.3rem !important;
    }
    .st-key-rl_table_rows hr {
        margin: 2px 0 !important;
    }
    .st-key-rl_table_rows [data-testid="column"] {
        padding-top: 4px !important;
        padding-bottom: 4px !important;
    }
    .st-key-rl_table_rows .rl-report-title {
        margin-bottom: 0px;
        line-height: 1.25;
    }
    .st-key-rl_table_rows .rl-report-desc {
        margin-top: 1px;
        line-height: 1.2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# IN-APP TAB STATE
# "Liste des rapports" is always open. "Article - Liste des
# Coloris / Taille" opens as a 2nd, closeable in-app tab when
# its row is clicked — no page navigation, no new browser tab,
# just a session_state-driven view swap under a tab bar.
# ============================================================

if "lr_active_tab" not in st.session_state:
    st.session_state.lr_active_tab = "liste"
if "lr_article_open" not in st.session_state:
    st.session_state.lr_article_open = False


def _activate_liste_tab():
    st.session_state.lr_active_tab = "liste"


def _open_article_tab():
    st.session_state.lr_article_open = True
    st.session_state.lr_active_tab = "article"


def _activate_article_tab():
    st.session_state.lr_active_tab = "article"


def _close_article_tab():
    st.session_state.lr_article_open = False
    st.session_state.lr_active_tab = "liste"


# ------------------------------------------------------------
# TAB BAR
# ------------------------------------------------------------

if st.session_state.lr_article_open:
    tab_col1, tab_col2, tab_spacer = st.columns([1.7, 2.8, 6.0])
else:
    tab_col1, tab_spacer = st.columns([1.7, 9.8])

with tab_col1:
    st.button(
        "Liste des rapports",
        key="tab_liste_btn",
        type="primary" if st.session_state.lr_active_tab == "liste" else "secondary",
        on_click=_activate_liste_tab,
        use_container_width=True,
    )

if st.session_state.lr_article_open:
    with tab_col2:
        tab_label_col, tab_close_col = st.columns([5, 1])
        with tab_label_col:
            st.button(
                "Article - Coloris / Taille",
                key="tab_article_btn",
                type="primary"
                if st.session_state.lr_active_tab == "article"
                else "secondary",
                on_click=_activate_article_tab,
                use_container_width=True,
            )
        with tab_close_col:
            st.button(
                "✖",
                key="tab_article_close_btn",
                on_click=_close_article_tab,
                use_container_width=True,
            )

st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
st.divider()

# ============================================================
# TAB CONTENT: "ARTICLE - LISTE DES COLORIS / TAILLE"
# ============================================================

if st.session_state.lr_active_tab == "article":

    render_article_coloris_view()

else:

    # ========================================================
    # TAB CONTENT: "LISTE DES RAPPORTS"
    # ========================================================

    # ---------------- SEARCH ROW ----------------

    with st.container(key="report_search_row"):
        search_col, btn_col, spacer_col, fav_col = st.columns([5, 1, 3, 1.4])

        with search_col:
            st.text_input(
                "Recherche",
                placeholder="Rechercher un rapport par nom, numéro ou mot-clé...",
                label_visibility="collapsed",
                key="report_search",
            )

        with btn_col:
            st.markdown('<div class="lr-search-btn">', unsafe_allow_html=True)
            st.button("Rechercher", key="report_search_btn", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with fav_col:
            st.button("☆  Mes favoris", key="mes_favoris_btn", use_container_width=True)

    st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)

    # ---------------- MOCK DATA ----------------

    reports = pd.DataFrame(
        [
            {
                "titre": "Mesures des Nouveaux Produits",
                "desc": "Suivi des mesures et performances produits",
                "numero": 1722,
                "dossier": "Logistique - Infolog",
                "favori": False,
                "page": None,
            },
            {
                "titre": "Article - Liste des Coloris / Taille",
                "desc": "Référentiel des coloris et tailles par article",
                "numero": 646,
                "dossier": "Nouvelles requêtes - Référentiel Article",
                "favori": False,
                "page": "article_coloris",
            },
            {
                "titre": "Commandes - Détail",
                "desc": "Détail des commandes et lignes associées",
                "numero": 667,
                "dossier": "Nouvelles requêtes - Gestion Commerciale",
                "favori": False,
                "page": None,
            },
            {
                "titre": "Stock Disponible - Dépôt Métier",
                "desc": "Disponibilités stock par dépôt et métier",
                "numero": 662,
                "dossier": "Nouvelles requêtes - Gestion Commerciale",
                "favori": False,
                "page": None,
            },
            {
                "titre": "Expéditions - Détail (après Facturation)",
                "desc": "Détail des expéditions après facturation",
                "numero": 669,
                "dossier": "Nouvelles requêtes - Gestion Commerciale",
                "favori": False,
                "page": None,
            },
            {
                "titre": "Commandes - Consolidation (Temps Réel)",
                "desc": "Consolidation temps réel des commandes",
                "numero": 986,
                "dossier": "Nouvelles requêtes - Gestion Commerciale",
                "favori": False,
                "page": None,
            },
            {
                "titre": "Liste des Produits",
                "desc": "Référentiel complet des produits",
                "numero": 644,
                "dossier": "Nouvelles requêtes - Référentiel Article",
                "favori": False,
                "page": None,
            },
            {
                "titre": "Factures - CA Consolidation (J-1)",
                "desc": "Chiffre d'affaires consolidé à J-1",
                "numero": 671,
                "dossier": "Nouvelles requêtes - Gestion Financière",
                "favori": False,
                "page": None,
            },
        ]
    )

    REPERTOIRE_TREE = [
        {"label": "Tous les dossiers", "level": 0, "chevron": True, "state": "normal"},
        {
            "label": "Favoris",
            "level": 0,
            "chevron": False,
            "state": "normal",
            "star": True,
        },
        {
            "label": "Informatique",
            "level": 0,
            "chevron": "down",
            "state": "parent-active",
        },
        {
            "label": "Production informatique",
            "level": 1,
            "chevron": True,
            "state": "normal",
        },
        {"label": "Infocentre", "level": 1, "chevron": True, "state": "active"},
        {
            "label": "Procédure tarifaire",
            "level": 1,
            "chevron": True,
            "state": "normal",
        },
        {"label": "Nouvelles requêtes", "level": 0, "chevron": True, "state": "normal"},
        {
            "label": "Référentiel Article",
            "level": 0,
            "chevron": True,
            "state": "normal",
        },
        {
            "label": "LMH - Gestion Commerciale",
            "level": 0,
            "chevron": True,
            "state": "normal",
        },
        {
            "label": "LMH - Gestion Financière",
            "level": 0,
            "chevron": True,
            "state": "normal",
        },
        {
            "label": "LMH - Gestion Production",
            "level": 0,
            "chevron": True,
            "state": "normal",
        },
        {
            "label": "LMH - Contrôle de gestion",
            "level": 0,
            "chevron": True,
            "state": "normal",
        },
        {"label": "LMH - Logistique", "level": 0, "chevron": True, "state": "normal"},
        {
            "label": "Référentiel Mercure",
            "level": 0,
            "chevron": True,
            "state": "normal",
        },
        {"label": "Divers", "level": 0, "chevron": True, "state": "normal"},
    ]

    # ---------------- LAYOUT: REPERTOIRES + TABLE ----------------

    left_col, right_col = st.columns([1.15, 3.4], gap="medium")

    with left_col:

        st.markdown('<div class="repertoire-panel">', unsafe_allow_html=True)
        st.markdown(
            '<div class="repertoire-title font-serif">Répertoires</div>',
            unsafe_allow_html=True,
        )

        st.text_input(
            "Rechercher un dossier",
            placeholder="Rechercher un dossier...",
            label_visibility="collapsed",
            key="folder_search",
        )

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

        tree_html = ""
        for item in REPERTOIRE_TREE:
            indent_class = "tree-indent-1" if item["level"] == 1 else ""
            state_class = {
                "active": "tree-active",
                "parent-active": "tree-parent-active",
                "normal": "",
            }[item["state"]]

            if item.get("star"):
                chevron_html = f'<span class="tree-chevron">{ICON_STAR}</span>'
            elif item["chevron"] == "down":
                chevron_html = f'<span class="tree-chevron">{ICON_CHEVRON_DOWN}</span>'
            elif item["chevron"]:
                chevron_html = f'<span class="tree-chevron">{ICON_CHEVRON_RIGHT}</span>'
            else:
                chevron_html = '<span class="tree-chevron" style="width:15px;"></span>'

            icon_html = (
                ""
                if item.get("star")
                else f'<span class="tree-icon">{ICON_FOLDER}</span>'
            )

            tree_html += (
                f'<div class="tree-item {state_class} {indent_class}">'
                f'{chevron_html}{icon_html}<span>{item["label"]}</span></div>'
            )

        st.markdown(tree_html, unsafe_allow_html=True)

        st.markdown(
            f'<div class="tree-footer">{ICON_SETTINGS}<span>Gérer les dossiers</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:

        (
            count_col,
            filt_col,
            sort_label_col,
            sort_col,
            view1_col,
            view2_col,
        ) = st.columns([3, 1.1, 0.9, 1.5, 0.55, 0.55])

        with count_col:
            st.markdown(
                f'<div class="rl-count">{len(reports)} rapports</div>',
                unsafe_allow_html=True,
            )

        with filt_col:
            st.button("▽  Filtres", key="filters_btn", use_container_width=True)

        with sort_label_col:
            st.markdown(
                '<div style="padding-top:6px; font-size:13px; color:#6E6A63;">Trier par</div>',
                unsafe_allow_html=True,
            )

        with sort_col:
            st.selectbox(
                "Trier par",
                ["Nom (A-Z)", "Nom (Z-A)", "Dernière modif.", "Utilisations"],
                label_visibility="collapsed",
                key="sort_select",
            )

        with view1_col:
            st.markdown(
                f'<div class="pill-btn active" style="padding:8px 10px;">{ICON_LIST_VIEW}</div>',
                unsafe_allow_html=True,
            )

        with view2_col:
            st.markdown(
                f'<div class="pill-btn" style="padding:8px 10px;">{ICON_GRID_VIEW}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

        with st.container(key="rl_table_rows"):
            st.markdown(
                """
                <div class="rl-table-header">
                    <div>Rapport</div>
                    <div>Numéro</div>
                    <div>Dossier</div>
                    <div></div>
                    <div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            def render_row(r):
                cols = st.columns([5, 1, 3, 0.5, 0.5])

                with cols[0]:
                    icon, text = st.columns([0.12, 0.88])

                    with icon:
                        st.markdown(
                            f'<div class="rl-report-icon">{ICON_DOC}</div>',
                            unsafe_allow_html=True,
                        )

                    with text:
                        if r["page"] == "article_coloris":
                            if st.button(
                                r["titre"],
                                key=f"title_{r['numero']}",
                                type="tertiary",
                            ):
                                _open_article_tab()  # or st.switch_page(...)
                        else:
                            st.markdown(
                                f'<div class="rl-report-title">{r["titre"]}</div>',
                                unsafe_allow_html=True,
                            )

                        st.markdown(
                            f'<div class="rl-report-desc">{r["desc"]}</div>',
                            unsafe_allow_html=True,
                        )

                with cols[1]:
                    st.write(r["numero"])

                with cols[2]:
                    st.write(r["dossier"])

                with cols[3]:
                    st.markdown(
                        f'<div class="rl-star">{ICON_STAR}</div>',
                        unsafe_allow_html=True,
                    )

                with cols[4]:
                    st.markdown(
                        f'<div class="rl-kebab">{ICON_KEBAB}</div>',
                        unsafe_allow_html=True,
                    )

                st.divider()

            for _, report in reports.iterrows():
                render_row(report)

# ---------------- FOOTER: PAGE SIZE + PAGINATION ----------------

foot_left, foot_right = st.columns([2, 3])

with foot_left:
    pp_label, pp_select = st.columns([2, 1])
    with pp_label:
        st.markdown(
            '<div style="padding-top:6px; font-size:13.5px; color:#4A4640;">Afficher</div>',
            unsafe_allow_html=True,
        )
    with pp_select:
        st.selectbox(
            "Résultats par page",
            ["25", "50", "100"],
            label_visibility="collapsed",
            key="page_size",
        )

with foot_right:
    st.markdown(
        """
        <div class="pagination-row" style="justify-content:flex-end;">
            <div class="page-pill">‹</div>
            <div class="page-pill current">1</div>
            <div class="page-pill">2</div>
            <div class="page-pill">3</div>
            <div class="page-pill">4</div>
            <div class="page-pill">5</div>
            <div class="page-pill">…</div>
            <div class="page-pill">›</div>
        </div>
        """,
        unsafe_allow_html=True,
    )