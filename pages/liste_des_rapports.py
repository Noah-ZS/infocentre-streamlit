import streamlit as st
import pandas as pd
from common import (
    render_topbar, ICON_DOC, ICON_STAR, ICON_SEARCH, ICON_FOLDER,
    ICON_FILTER, ICON_CHEVRON_DOWN, ICON_CHEVRON_RIGHT, ICON_INFO,
    ICON_LIST_VIEW, ICON_GRID_VIEW, ICON_SETTINGS, ICON_KEBAB
)
from report_views import (
    render_article_coloris_view, render_mesures_produits_view,
    render_commandes_detail_view
)

render_topbar("Production M3 13.4")

st.markdown('<div class="page-title font-serif">Liste des rapports</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Accédez à l\'ensemble des rapports disponibles et analysez vos données.</div>',
    unsafe_allow_html=True
)

# ============================================================
# REPORT REGISTRY
# Maps a report key -> its tab label and the shared view function
# that renders it (from report_views.py). Adding a new in-app
# report tab in the future just means adding an entry here.
# ============================================================

REPORT_TABS = {
    "mesures": {"label": "Mesures Nouveaux Produits", "render": render_mesures_produits_view},
    "article": {"label": "Article - Coloris / Taille", "render": render_article_coloris_view},
    "commandes": {"label": "Commandes - Détail", "render": render_commandes_detail_view},
}

# ============================================================
# MULTI-TAB STATE
# "Liste des rapports" is always open and always first. Any
# number of report tabs can be open alongside it, in the order
# they were opened, each with its own close (✖) button.
# ============================================================

if "lr_active_tab" not in st.session_state:
    st.session_state.lr_active_tab = "liste"
if "lr_open_tabs" not in st.session_state:
    st.session_state.lr_open_tabs = []  # ordered list of report keys


def _activate_tab(key):
    st.session_state.lr_active_tab = key


def _open_tab(key):
    if key not in st.session_state.lr_open_tabs:
        st.session_state.lr_open_tabs.append(key)
    st.session_state.lr_active_tab = key


def _close_tab(key):
    if key in st.session_state.lr_open_tabs:
        st.session_state.lr_open_tabs.remove(key)
    if st.session_state.lr_active_tab == key:
        st.session_state.lr_active_tab = "liste"


# ------------------------------------------------------------
# TAB BAR
# ------------------------------------------------------------

open_tabs = st.session_state.lr_open_tabs
n_open = len(open_tabs)
tab_ratios = [1.7] + [2.1] * n_open + [max(9.6 - 2.1 * n_open, 1.0)]
tab_cols = st.columns(tab_ratios)

with tab_cols[0]:
    st.button(
        "Liste des rapports",
        key="tab_liste_btn",
        type="primary" if st.session_state.lr_active_tab == "liste" else "secondary",
        on_click=_activate_tab,
        args=("liste",),
        use_container_width=True,
    )

for i, key in enumerate(open_tabs):
    with tab_cols[i + 1]:
        label_col, close_col = st.columns([5, 1])
        with label_col:
            st.button(
                REPORT_TABS[key]["label"],
                key=f"tab_{key}_btn",
                type="primary" if st.session_state.lr_active_tab == key else "secondary",
                on_click=_activate_tab,
                args=(key,),
                use_container_width=True,
            )
        with close_col:
            st.button(
                "✖",
                key=f"tab_{key}_close_btn",
                on_click=_close_tab,
                args=(key,),
                use_container_width=True,
            )

st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
st.divider()

# ============================================================
# TAB CONTENT
# ============================================================

if st.session_state.lr_active_tab in REPORT_TABS:

    REPORT_TABS[st.session_state.lr_active_tab]["render"]()

else:

    # ========================================================
    # "LISTE DES RAPPORTS" BODY
    # ========================================================

    # ---------------- SEARCH ROW ----------------

    search_col, btn_col, spacer_col, fav_col = st.columns([5, 1, 3, 1.4])

    with search_col:
        st.text_input(
            "Recherche",
            placeholder="Rechercher un rapport par nom, numéro ou mot-clé...",
            label_visibility="collapsed",
            key="report_search"
        )

    with btn_col:
        st.button("Rechercher", key="report_search_btn", type="primary", use_container_width=True)

    with fav_col:
        st.button("☆  Mes favoris", key="mes_favoris_btn", use_container_width=True)

    st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)

    # ---------------- MOCK DATA ----------------
    # "key" links a row to an entry in REPORT_TABS above; rows with
    # key=None are static/non-interactive mock rows.

    reports = pd.DataFrame([
        {"key": "mesures", "titre": "Mesures des Nouveaux Produits", "desc": "Suivi des mesures et performances produits",
         "numero": 1722, "dossier": "Logistique - Infolog", "favori": False},
        {"key": "article", "titre": "Article - Liste des Coloris / Taille", "desc": "Référentiel des coloris et tailles par article",
         "numero": 646, "dossier": "Nouvelles requêtes - Référentiel Article", "favori": False},
        {"key": "commandes", "titre": "Commandes - Détail", "desc": "Détail des commandes et lignes associées",
         "numero": 667, "dossier": "Nouvelles requêtes - Gestion Commerciale", "favori": False},
        {"key": None, "titre": "Stock Disponible - Dépôt Métier", "desc": "Disponibilités stock par dépôt et métier",
         "numero": 662, "dossier": "Nouvelles requêtes - Gestion Commerciale", "favori": False},
        {"key": None, "titre": "Expéditions - Détail (après Facturation)", "desc": "Détail des expéditions après facturation",
         "numero": 669, "dossier": "Nouvelles requêtes - Gestion Commerciale", "favori": False},
        {"key": None, "titre": "Commandes - Consolidation (Temps Réel)", "desc": "Consolidation temps réel des commandes",
         "numero": 986, "dossier": "Nouvelles requêtes - Gestion Commerciale", "favori": False},
        {"key": None, "titre": "Liste des Produits", "desc": "Référentiel complet des produits",
         "numero": 644, "dossier": "Nouvelles requêtes - Référentiel Article", "favori": False},
        {"key": None, "titre": "Factures - CA Consolidation (J-1)", "desc": "Chiffre d'affaires consolidé à J-1",
         "numero": 671, "dossier": "Nouvelles requêtes - Gestion Financière", "favori": False},
    ])

    REPERTOIRE_TREE = [
        {"label": "Tous les dossiers", "level": 0, "chevron": True, "state": "normal"},
        {"label": "Favoris", "level": 0, "chevron": False, "state": "normal", "star": True},
        {"label": "Informatique", "level": 0, "chevron": "down", "state": "parent-active"},
        {"label": "Production informatique", "level": 1, "chevron": True, "state": "normal"},
        {"label": "Infocentre", "level": 1, "chevron": True, "state": "active"},
        {"label": "Procédure tarifaire", "level": 1, "chevron": True, "state": "normal"},
        {"label": "Nouvelles requêtes", "level": 0, "chevron": True, "state": "normal"},
        {"label": "Référentiel Article", "level": 0, "chevron": True, "state": "normal"},
        {"label": "LMH - Gestion Commerciale", "level": 0, "chevron": True, "state": "normal"},
        {"label": "LMH - Gestion Financière", "level": 0, "chevron": True, "state": "normal"},
        {"label": "LMH - Gestion Production", "level": 0, "chevron": True, "state": "normal"},
        {"label": "LMH - Contrôle de gestion", "level": 0, "chevron": True, "state": "normal"},
        {"label": "LMH - Logistique", "level": 0, "chevron": True, "state": "normal"},
        {"label": "Référentiel Mercure", "level": 0, "chevron": True, "state": "normal"},
        {"label": "Divers", "level": 0, "chevron": True, "state": "normal"},
    ]

    # ---------------- LAYOUT: REPERTOIRES + TABLE ----------------

    left_col, right_col = st.columns([1.15, 3.4], gap="medium")

    with left_col:

        st.markdown('<div class="repertoire-panel">', unsafe_allow_html=True)
        st.markdown('<div class="repertoire-title font-serif">Répertoires</div>', unsafe_allow_html=True)

        st.text_input(
            "Rechercher un dossier",
            placeholder="Rechercher un dossier...",
            label_visibility="collapsed",
            key="folder_search"
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

            icon_html = "" if item.get("star") else f'<span class="tree-icon">{ICON_FOLDER}</span>'

            tree_html += (
                f'<div class="tree-item {state_class} {indent_class}">'
                f'{chevron_html}{icon_html}<span>{item["label"]}</span></div>'
            )

        st.markdown(tree_html, unsafe_allow_html=True)

        st.markdown(
            f'<div class="tree-footer">{ICON_SETTINGS}<span>Gérer les dossiers</span></div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:

        count_col, filt_col, sort_label_col, sort_col, view1_col, view2_col = st.columns(
            [3, 1.1, 0.9, 1.5, 0.55, 0.55]
        )

        with count_col:
            st.markdown(f'<div class="rl-count">{len(reports)} rapports</div>', unsafe_allow_html=True)

        with filt_col:
            st.button("▽  Filtres", key="filters_btn", use_container_width=True)

        with sort_label_col:
            st.markdown('<div style="padding-top:6px; font-size:13px; color:#6E6A63;">Trier par</div>', unsafe_allow_html=True)

        with sort_col:
            st.selectbox(
                "Trier par", ["Nom (A-Z)", "Nom (Z-A)", "Dernière modif.", "Utilisations"],
                label_visibility="collapsed", key="sort_select"
            )

        with view1_col:
            st.markdown(
                f'<div class="pill-btn active" style="padding:8px 10px;">{ICON_LIST_VIEW}</div>',
                unsafe_allow_html=True
            )

        with view2_col:
            st.markdown(
                f'<div class="pill-btn" style="padding:8px 10px;">{ICON_GRID_VIEW}</div>',
                unsafe_allow_html=True
            )

        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

        # ---------------- TABLE HEADER ----------------

        th1, th2, th3, th4, th5 = st.columns([3, 0.6, 1.6, 0.25, 0.2])
        with th1:
            st.markdown('<div class="rl-th">Rapport</div>', unsafe_allow_html=True)
        with th2:
            st.markdown('<div class="rl-th">Numéro</div>', unsafe_allow_html=True)
        with th3:
            st.markdown('<div class="rl-th">Dossier</div>', unsafe_allow_html=True)
        with th4:
            st.markdown('<div class="rl-th"></div>', unsafe_allow_html=True)
        with th5:
            st.markdown('<div class="rl-th"></div>', unsafe_allow_html=True)

        st.markdown('<hr class="rl-row-hr">', unsafe_allow_html=True)

        # ---------------- TABLE ROWS ----------------
        # Every row uses real st.columns (not raw HTML) so the
        # title can be a genuine, natively-laid-out st.button for
        # the 3 rows that link to a report, with zero overlay
        # hacks. Non-linked rows render identical markup, just
        # without the click behavior, styled the same way so the
        # table reads as one consistent list.

        # Replace the TABLE ROWS section in liste_des_rapports.py with this:

        # ---------------- GRID CARDS ----------------
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

        grid_col1, grid_col2 = st.columns(2, gap="medium")

        for i, (_, r) in enumerate(reports.iterrows()):
            target_col = grid_col1 if i % 2 == 0 else grid_col2
            
            with target_col:
                fav_tag = f'<div class="rc-tag">{ICON_STAR} Favoris</div>' if r["favori"] else '<div></div>'
                
                st.markdown(f"""
                <div class="report-card">
                    <div class="rc-header">
                        {fav_tag}
                        <div style="color: #B4AFA6;">{ICON_KEBAB}</div>
                    </div>
                    <div class="rc-title">{r['titre']}</div>
                    <div class="rc-id">{r['numero']}</div>
                    <div class="rc-footer">
                        <div>{r['dossier']}</div>
                        <div>26/03/2024</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Remove the th1, th2 (table headers) and rl-row-hr elements completely.

        # ---------------- FOOTER: PAGE SIZE + PAGINATION ----------------

        foot_left, foot_right = st.columns([2, 3])

        with foot_left:
            pp_label, pp_select = st.columns([2, 1])
            with pp_label:
                st.markdown('<div style="padding-top:6px; font-size:13.5px; color:#4A4640;">Afficher</div>', unsafe_allow_html=True)
            with pp_select:
                st.selectbox("Résultats par page", ["25", "50", "100"], label_visibility="collapsed", key="page_size")

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