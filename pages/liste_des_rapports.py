import streamlit as st
import pandas as pd
from common import (
    render_topbar, ICON_STAR, ICON_FOLDER,
    ICON_CHEVRON_DOWN, ICON_CHEVRON_RIGHT, ICON_KEBAB
)
from report_views import (
    render_article_coloris_view, render_mesures_produits_view,
    render_commandes_detail_view
)

render_topbar("Production M3 13.4", breadcrumb="Accueil / Liste des rapports")

# ============================================================
# MULTI-TAB STATE & REGISTRY
# ============================================================

REPORT_TABS = {
    "mesures": {"label": "Mesures Nouveaux Produits", "render": render_mesures_produits_view},
    "article": {"label": "Article - Coloris / Taille", "render": render_article_coloris_view},
    "commandes": {"label": "Commandes - Détail", "render": render_commandes_detail_view},
}

if "lr_active_tab" not in st.session_state:
    st.session_state.lr_active_tab = "liste"
if "lr_open_tabs" not in st.session_state:
    st.session_state.lr_open_tabs = [] 

def _activate_tab(key): st.session_state.lr_active_tab = key
def _open_tab(key):
    if key not in st.session_state.lr_open_tabs: st.session_state.lr_open_tabs.append(key)
    st.session_state.lr_active_tab = key
def _close_tab(key):
    if key in st.session_state.lr_open_tabs: st.session_state.lr_open_tabs.remove(key)
    if st.session_state.lr_active_tab == key: st.session_state.lr_active_tab = "liste"

# ------------------------------------------------------------
# TAB BAR
# ------------------------------------------------------------
open_tabs = st.session_state.lr_open_tabs
n_open = len(open_tabs)
tab_ratios = [1.8] + [2.5] * n_open + [max(10 - 2.5 * n_open, 1.0)]
tab_cols = st.columns(tab_ratios)

with tab_cols[0]:
    st.button(
        "Liste des rapports", key="tab_liste_btn",
        type="primary" if st.session_state.lr_active_tab == "liste" else "secondary",
        on_click=_activate_tab, args=("liste",), use_container_width=True,
    )

for i, key in enumerate(open_tabs):
    with tab_cols[i + 1]:
        label_col, close_col = st.columns([6, 1])
        with label_col:
            st.button(
                REPORT_TABS[key]["label"], key=f"tab_{key}_btn",
                type="primary" if st.session_state.lr_active_tab == key else "secondary",
                on_click=_activate_tab, args=(key,), use_container_width=True,
            )
        with close_col:
            st.button("✖", key=f"tab_{key}_close_btn", on_click=_close_tab, args=(key,), use_container_width=True)

st.markdown('<div style="height:12px; border-top: 1px solid var(--line); margin-top: -14px;"></div>', unsafe_allow_html=True)

# ============================================================
# TAB CONTENT
# ============================================================

if st.session_state.lr_active_tab in REPORT_TABS:
    REPORT_TABS[st.session_state.lr_active_tab]["render"]()
else:
    # ---------------- LISTE DES RAPPORTS BODY ----------------
    st.markdown('<div class="page-title font-serif">Liste des rapports</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Accédez à l\'ensemble des rapports disponibles et analysez vos données.</div>', unsafe_allow_html=True)

    # Search Row aligned visually
    search_col, filter_col, sort_lbl_col, sort_val_col = st.columns([6.5, 1.5, 1.2, 2.5])
    with search_col:
        st.text_input("Recherche", placeholder="🔍 Rechercher un rapport...", label_visibility="collapsed", key="report_search")
    with filter_col:
        st.button("▽ Filtres", key="report_filter_btn", use_container_width=True)
    with sort_lbl_col:
        st.markdown('<div style="padding-top:8px; font-size:14px; text-align:right;">Trier par</div>', unsafe_allow_html=True)
    with sort_val_col:
        st.selectbox("Trier par", ["Nom (A-Z)", "Nom (Z-A)", "Dernière modif."], label_visibility="collapsed", key="report_sort")

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    # Mock Data
    reports = pd.DataFrame([
        {"key": "mesures", "titre": "Mesures des Nouveaux Produits", "numero": 1722, "dossier": "Logistique - Infolog", "fav": True},
        {"key": "mesures", "titre": "Suivi des mesures et performances produits", "numero": 1722, "dossier": "Logistique - Infolog", "fav": True},
        {"key": "article", "titre": "Article - Liste des Coloris / Taille", "numero": 646, "dossier": "Logistique - Infolog", "fav": True},
        {"key": "article", "titre": "Nouvelles requêtes - Référentiel Article", "numero": 646, "dossier": "Logistique - Infolog", "fav": True},
        {"key": "commandes", "titre": "Commandes - Détail", "numero": 667, "dossier": "Logistique - Infolog", "fav": True},
        {"key": "commandes", "titre": "Nouvelles requêtes - Gestion Commerciale", "numero": 667, "dossier": "Logistique - Infolog", "fav": True},
    ])

    REPERTOIRE_TREE = [
        {"label": "Tous les dossiers", "level": 0, "chevron": True, "state": "normal"},
        {"label": "Favoris", "level": 0, "chevron": False, "state": "normal", "star": True},
        {"label": "Informatique", "level": 0, "chevron": "down", "state": "parent-active"},
        {"label": "Production informatique", "level": 1, "chevron": True, "state": "normal"},
        {"label": "Infocentre", "level": 1, "chevron": True, "state": "active"},
        {"label": "Procédure tarifaire", "level": 1, "chevron": True, "state": "normal"},
        {"label": "Nouvelles requêtes", "level": 1, "chevron": True, "state": "normal"},
        {"label": "Nouvelles requêtes", "level": 0, "chevron": True, "state": "normal"},
        {"label": "Référentiel Article", "level": 0, "chevron": True, "state": "normal"},
        {"label": "LMH - Gestion Commerciale", "level": 0, "chevron": True, "state": "normal"},
    ]

    left_col, right_col = st.columns([1.2, 3.5], gap="large")

    with left_col:
        st.markdown('<div class="repertoire-panel">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Fraunces\', serif; font-size:18px; font-weight:600; margin-bottom:16px;">Répertoires</div>', unsafe_allow_html=True)
        st.text_input("Rechercher un dossier...", placeholder="Rechercher un dossier...", label_visibility="collapsed", key="folder_search")
        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

        tree_html = ""
        for item in REPERTOIRE_TREE:
            indent_class = "tree-indent-1" if item["level"] == 1 else ""
            state_class = {"active": "tree-active", "parent-active": "tree-parent-active", "normal": ""}[item["state"]]
            
            if item.get("star"): chevron_html = f'<span class="tree-chevron" style="color:var(--accent);">★'</span>
            elif item["chevron"] == "down": chevron_html = f'<span class="tree-chevron">{ICON_CHEVRON_DOWN}'</span>
            else: chevron_html = f'<span class="tree-chevron">{ICON_CHEVRON_RIGHT}'</span>
            
            icon_html = "" if item.get("star") else f'<span class="tree-icon">{ICON_FOLDER}'</span>
            tree_html += f'<div class="tree-item {state_class} {indent_class}">{chevron_html}{icon_html}<span>{item["label"]}</div>'</span>

        st.markdown(tree_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        # GRID OF CARDS mapped via exact column iteration matching screenshot
        grid_c1, grid_c2 = st.columns(2, gap="medium")
        for i, r in reports.iterrows():
            target_c = grid_c1 if i % 2 == 0 else grid_c2
            with target_c:
                st.markdown('<div class="report-grid-card">', unsafe_allow_html=True)
                
                st.markdown(f'''
                    <div class="rgc-header">
                        <div class="rgc-fav">★ Favoris</div>
                        <div class="rgc-kebab">{ICON_KEBAB}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Interactive title button
                if pd.notna(r["key"]):
                    st.button(r["titre"], key=f"open_{r['key']}_title_btn_{i}", on_click=_open_tab, args=(r["key"],))
                
                st.markdown(f'<div class="rgc-id">{r["numero"]}</div>', unsafe_allow_html=True)
                st.markdown(f'''
                    <div class="rgc-footer">
                        <span>{r["dossier"]}</span>
                        <span>26/03/2024</span>
                    </div>
                </div>''', unsafe_allow_html=True)