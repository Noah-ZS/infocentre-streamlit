import streamlit as st
import pandas as pd
from common import (
    inject_global_css, render_sidebar, render_topbar,
    ICON_DOC, ICON_STAR, ICON_SEARCH, ICON_FOLDER,
    ICON_FILTER, ICON_CHEVRON_DOWN, ICON_CHEVRON_RIGHT, ICON_INFO,
    ICON_LIST_VIEW, ICON_GRID_VIEW, ICON_SETTINGS, ICON_KEBAB
)

# ------------------------------------------------------------
# CHROME: CSS + sidebar + topbar
# inject_global_css() is idempotent (just (re)injects a <style> tag),
# so it's safe to call again even if the router already called it —
# call it here explicitly so this page never renders unstyled.
# ------------------------------------------------------------
inject_global_css()

render_topbar("Production M3 13.4")

st.markdown('<div class="page-title font-serif">Liste des rapports</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Accédez à l\'ensemble des rapports disponibles et analysez vos données.</div>',
    unsafe_allow_html=True
)

# ============================================================
# SEARCH & FILTERS BAR
# ============================================================
search_col, btn_col, fav_col = st.columns([6, 1.5, 2], gap="small")

with search_col:
    st.text_input(
        "Recherche",
        placeholder="Rechercher un rapport par nom, numéro ou mot-clé...",
        label_visibility="collapsed",
        key="report_search"
    )

with btn_col:
    st.markdown('<div class="lr-search-btn">', unsafe_allow_html=True)
    st.button("Rechercher", key="report_search_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with fav_col:
    st.button("☆  Mes favoris", key="mes_favoris_btn", use_container_width=True)

st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

# ============================================================
# MOCK DATA
# (propriétaire / maj / usages are kept on the dataframe in case
# they're needed elsewhere — e.g. sort_select — but are no longer
# rendered as table columns per the design change below.)
# ============================================================
reports = pd.DataFrame([
    {"titre": "Mesures des Nouveaux Produits", "desc": "Suivi des mesures et performances produits",
     "numero": 1722, "dossier": "Logistique - Infolog", "proprietaire": "J. Martin",
     "maj": "23/05/2026", "usages": 124, "favori": False, "page": None},
    {"titre": "Article - Liste des Coloris / Taille", "desc": "Référentiel des coloris et tailles par article",
     "numero": 646, "dossier": "Nouvelles requêtes - Référentiel Article", "proprietaire": "A. Dubois",
     "maj": "22/05/2026", "usages": 312, "favori": False, "page": "article_coloris"},
    {"titre": "Commandes - Détail", "desc": "Détail des commandes et lignes associées",
     "numero": 667, "dossier": "Nouvelles requêtes - Gestion Commerciale", "proprietaire": "S. Bernard",
     "maj": "21/05/2026", "usages": 845, "favori": False, "page": None},
    {"titre": "Stock Disponible - Dépôt Métier", "desc": "Disponibilités stock par dépôt et métier",
     "numero": 662, "dossier": "Nouvelles requêtes - Gestion Commerciale", "proprietaire": "M. Moreau",
     "maj": "20/05/2026", "usages": 278, "favori": False, "page": None},
    {"titre": "Expéditions - Détail (après Facturation)", "desc": "Détail des expéditions après facturation",
     "numero": 669, "dossier": "Nouvelles requêtes - Gestion Commerciale", "proprietaire": "J. Martin",
     "maj": "20/05/2026", "usages": 193, "favori": False, "page": None},
    {"titre": "Commandes - Consolidation (Temps Réel)", "desc": "Consolidation temps réel des commandes",
     "numero": 986, "dossier": "Nouvelles requêtes - Gestion Commerciale", "proprietaire": "A. Dubois",
     "maj": "19/05/2026", "usages": 156, "favori": False, "page": None},
    {"titre": "Liste des Produits", "desc": "Référentiel complet des produits",
     "numero": 644, "dossier": "Nouvelles requêtes - Référentiel Article", "proprietaire": "S. Bernard",
     "maj": "19/05/2026", "usages": 98, "favori": False, "page": None},
    {"titre": "Factures - CA Consolidation (J-1)", "desc": "Chiffre d'affaires consolidé à J-1",
     "numero": 671, "dossier": "Nouvelles requêtes - Gestion Financière", "proprietaire": "M. Moreau",
     "maj": "18/05/2026", "usages": 211, "favori": False, "page": None},
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

# ============================================================
# DYNAMIC IN-APP TABS — session-state driven, rendered by
# render_sidebar() in common.py right under "Liste des rapports"
# ============================================================
if "dynamic_tabs" not in st.session_state:
    st.session_state.dynamic_tabs = []
if "active_dynamic_tab" not in st.session_state:
    st.session_state.active_dynamic_tab = None


def open_dynamic_tab(key: str, label: str, target_page: str):
    if key not in [t["key"] for t in st.session_state.dynamic_tabs]:
        st.session_state.dynamic_tabs.append(
            {"key": key, "label": label, "target_page": target_page}
        )
    st.session_state.active_dynamic_tab = key
    st.switch_page(target_page)


# ============================================================
# MAIN LAYOUT: REPERTOIRES (left) + CONTENT TABLE (right)
# ============================================================
left_col, right_col = st.columns([1.2, 3.8], gap="large")

# ---------------- LEFT PANEL: REPERTOIRES ----------------
with left_col:
    st.markdown('<div class="repertoire-panel">', unsafe_allow_html=True)
    st.markdown('<div class="repertoire-title font-serif">Répertoires</div>', unsafe_allow_html=True)

    st.text_input(
        "Rechercher un dossier",
        placeholder="Rechercher un dossier...",
        label_visibility="collapsed",
        key="folder_search"
    )

    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

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


# ---------------- RIGHT PANEL: REPORTS TABLE ----------------
with right_col:
    count_col, filt_col, sort_col, view_col = st.columns([3, 1.2, 2.5, 1])

    with count_col:
        st.markdown(f'<div class="rl-count" style="line-height: 38px;">{len(reports)} rapports</div>', unsafe_allow_html=True)

    with filt_col:
        st.button("▽  Filtres", key="filters_btn", use_container_width=True)

    with sort_col:
        st.selectbox(
            "Trier par", ["Nom (A-Z)", "Nom (Z-A)", "Dernière modif.", "Utilisations"],
            label_visibility="collapsed", key="sort_select"
        )

    with view_col:
        st.markdown(
            f"""
            <div style="display: flex; gap: 4px; justify-content: flex-end; padding-top: 4px;">
                <div class="pill-btn active" style="padding:8px 10px; cursor: pointer;">{ICON_LIST_VIEW}</div>
                <div class="pill-btn" style="padding:8px 10px; cursor: pointer;">{ICON_GRID_VIEW}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    # ---- Table header: Rapport / Numéro / Dossier only ----
    st.markdown(
        f"""
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

# ---- Table rows ----
    for _, r in reports.iterrows():
        star_class = "filled" if r["favori"] else ""
        is_tab_trigger = r["page"] == "article_coloris"

        with st.container(key=f"row_{r['numero']}"):
            c_report, c_num, c_dossier, c_star, c_kebab = st.columns(
                [4, 0.9, 2.2, 0.34, 0.26], gap="small"
            )

            with c_report:
                if is_tab_trigger:
                    clicked = st.button(
                        r["titre"],
                        key=f"open_tab_{r['numero']}",
                        use_container_width=True,
                    )
                    st.markdown(
                        f'<div class="rl-report-desc-inline">{r["desc"]}</div>',
                        unsafe_allow_html=True,
                    )
                    if clicked:
                        open_dynamic_tab(
                            key=f"tab_{r['numero']}",
                            label=r["titre"],
                            target_page="pages/article_coloris.py",
                        )
                else:
                    st.markdown(
                        f"""
                        <div class="rl-report-cell">
                            <div class="rl-report-icon">{ICON_DOC}</div>
                            <div>
                                <div class="rl-report-title">{r['titre']}</div>
                                <div class="rl-report-desc">{r['desc']}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with c_num:
                st.markdown(f'<div class="rl-cell">{r["numero"]}</div>', unsafe_allow_html=True)

            with c_dossier:
                st.markdown(
                    f'<div class="rl-cell" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{r["dossier"]}</div>',
                    unsafe_allow_html=True,
                )

            with c_star:
                st.markdown(f'<div class="rl-star {star_class}">{ICON_STAR}</div>', unsafe_allow_html=True)

            with c_kebab:
                st.markdown(f'<div class="rl-kebab">{ICON_KEBAB}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    # ---------------- FOOTER: PAGINATION ----------------
    foot_left, foot_right = st.columns([2, 3])

    with foot_left:
        pp_label, pp_select = st.columns([2, 1.2])
        with pp_label:
            st.markdown('<div style="padding-top:6px; font-size:13.5px; color:#4A4640; text-align: right; padding-right: 10px;">Afficher</div>', unsafe_allow_html=True)
        with pp_select:
            st.selectbox("Résultats par page", ["25", "50", "100"], label_visibility="collapsed", key="page_size")

    with foot_right:
        st.markdown(
            f"""
            <div class="pagination-row" style="display: flex; justify-content: flex-end; gap: 4px; padding-top: 4px;">
                <div class="page-pill" style="padding: 6px 12px; border: 1px solid #EAE8E4; border-radius: 4px; cursor: pointer; font-size: 13px;">‹</div>
                <div class="page-pill current" style="padding: 6px 12px; background-color: #1A1A1A; color: white; border-radius: 4px; font-size: 13px; font-weight: 600;">1</div>
                <div class="page-pill" style="padding: 6px 12px; border: 1px solid #EAE8E4; border-radius: 4px; cursor: pointer; font-size: 13px;">2</div>
                <div class="page-pill" style="padding: 6px 12px; border: 1px solid #EAE8E4; border-radius: 4px; cursor: pointer; font-size: 13px;">3</div>
                <div class="page-pill" style="padding: 6px 12px; border: 1px solid #EAE8E4; border-radius: 4px; cursor: pointer; font-size: 13px;">4</div>
                <div class="page-pill" style="padding: 6px 12px; border: 1px solid #EAE8E4; border-radius: 4px; cursor: pointer; font-size: 13px;">5</div>
                <div class="page-pill" style="padding: 6px 12px; color: #8C8881; font-size: 13px;">…</div>
                <div class="page-pill" style="padding: 6px 12px; border: 1px solid #EAE8E4; border-radius: 4px; cursor: pointer; font-size: 13px;">›</div>
            </div>
            """,
            unsafe_allow_html=True,
        )