import streamlit as st
import pandas as pd
from common import (
    render_topbar, ICON_DOC, ICON_STAR, ICON_SEARCH, ICON_FOLDER,
    ICON_FILTER, ICON_CHEVRON_DOWN, ICON_CHEVRON_RIGHT, ICON_INFO,
    ICON_LIST_VIEW, ICON_GRID_VIEW, ICON_SETTINGS, ICON_KEBAB,
    get_reports_catalog, get_favorites
)
from report_views import (
    render_article_coloris_view, render_mesures_produits_view,
    render_commandes_detail_view
)

render_topbar("Production M3 13.4", breadcrumb=["Accueil", "Liste des rapports"])

st.markdown('<div class="page-title font-serif">Liste des rapports</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Accédez à l\'ensemble des rapports disponibles et analysez vos données.</div>',
    unsafe_allow_html=True
)

# ============================================================
# PAGE-LOCAL STYLE: TAB BAR
# Scoped to this page only (doesn't touch common.py). Overrides
# Streamlit's default bordered/pill button chrome so the tabs
# read as flat text — dark ink when inactive, accent-orange with
# a bottom underline when active — matching the target design.
# Close (×) buttons are styled separately, kept minimal/subtle.
# ============================================================

st.markdown(
    """
    <style>
    /* Tab label buttons: match on any key starting "tab_" that is
       NOT one of the "..._close_btn" close buttons. */
    [class*="st-key-tab_"]:not([class*="_close_btn"]) button {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 4px 2px 10px 2px !important;
        margin: 0 !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
        color: var(--ink, #1C1B19) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-bottom: 2px solid transparent !important;
        width: auto !important;
        min-width: 0 !important;
    }
    [class*="st-key-tab_"]:not([class*="_close_btn"]) button:hover {
        color: var(--accent, #D9642A) !important;
        background: transparent !important;
    }
    /* Active tab — Streamlit renders type="primary" buttons with a
       "primary" kind marker; covering both the older and current
       attribute/testid conventions so this holds across versions. */
    [class*="st-key-tab_"]:not([class*="_close_btn"]) button[kind="primary"],
    [class*="st-key-tab_"]:not([class*="_close_btn"]) [data-testid="stBaseButton-primary"],
    [class*="st-key-tab_"]:not([class*="_close_btn"]) [data-testid="baseButton-primary"] {
        color: var(--accent, #D9642A) !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--accent, #D9642A) !important;
    }

    /* Close (×) buttons: no box, just a small subtle glyph that
       reddens on hover — present for function, invisible as chrome. */
    [class*="st-key-tab_"][class*="_close_btn"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #B4AFA6 !important;
        padding: 0 !important;
        margin-top: 6px !important;
        height: auto !important;
        min-height: 0 !important;
        font-size: 12px !important;
        width: auto !important;
    }
    [class*="st-key-tab_"][class*="_close_btn"] button:hover {
        color: #E0473B !important;
    }

    /* ---------------- RÉPERTOIRES: INTERACTIVE FOLDER TREE ---------------- */
    /* The whole left panel is now a real st.container(key="repertoire_panel")
       (previously a hand-written <div> that never actually wrapped the
       search input / tree buttons — an unclosed tag spanning separate
       st.markdown()/st.button() calls doesn't nest them, it just renders
       as an empty sibling box). Styled here to reproduce the original
       card look for real. */
    .st-key-repertoire_panel > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF;
        border: 1px solid var(--line, #EAE5DC);
    }

    /* Each folder/file row is a real st.button (needed so it can be
       clicked to expand/collapse), stripped down to look like the
       original flat tree-item text row rather than a button. */
    [class*="st-key-tree_node_"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 6px 4px !important;
        margin: 0 !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        color: #4A4640 !important;
        width: 100% !important;
        border-radius: 6px !important;
        white-space: pre !important; /* preserve the \u00A0-based indent */
    }
    [class*="st-key-tree_node_"] button:hover {
        background: #F5F2EC !important;
    }
    /* Selected folder / ancestor-of-selected — reusing the same
       type="primary" -> accent-color trick already used for tabs. */
    [class*="st-key-tree_node_"] button[kind="primary"],
    [class*="st-key-tree_node_"] [data-testid="stBaseButton-primary"],
    [class*="st-key-tree_node_"] [data-testid="baseButton-primary"] {
        background: var(--accent-bg, #FBEAE0) !important;
        color: var(--accent, #D9642A) !important;
        font-weight: 600 !important;
    }

    /* ---------------- CARD GRID: TIGHTER SPACING ---------------- */
    /* Scoped to card_<numero> containers only, so nothing else on
       the page (KPI cards, favorites panel, etc.) is affected. */
    [class*="st-key-card_"] [data-testid="stVerticalBlock"] {
        gap: 0.4rem !important;
    }
    .rc-card-title { margin-bottom: 4px !important; }
    .rc-card-meta { margin-bottom: 2px !important; }
    .rc-card-footer-divider { margin: 4px 0 6px 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# REPORT REGISTRY
# Maps a report key -> its tab label and the shared view function
# that renders it (from report_views.py). Adding a new in-app
# report tab in the future just means adding an entry here.
# (UNCHANGED — pure UI/layout pass, no logic touched below.)
# ============================================================

REPORT_TABS = {
    "mesures": {"label": "Mesures Nouveaux Produits", "render": render_mesures_produits_view},
    "article": {"label": "Article - Coloris / Taille", "render": render_article_coloris_view},
    "commandes": {"label": "Commandes - Détail", "render": render_commandes_detail_view},
}

# ============================================================
# MULTI-TAB STATE (UNCHANGED)
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


def _toggle_favorite(numero):
    favorites = get_favorites()
    if numero in favorites:
        favorites.remove(numero)
    else:
        favorites.add(numero)


# ============================================================
# FOLDER TREE STATE
# lr_expanded_folders: set of folder keys currently expanded.
# lr_active_folder: the single folder key currently selected.
# "Informatique" starts expanded / "Infocentre" starts selected,
# matching the original static mockup's default look.
# ============================================================

if "lr_expanded_folders" not in st.session_state:
    st.session_state.lr_expanded_folders = {"informatique"}
if "lr_active_folder" not in st.session_state:
    st.session_state.lr_active_folder = "infocentre"


def _handle_folder_click(node_key, has_children):
    if has_children:
        expanded = st.session_state.lr_expanded_folders
        if node_key in expanded:
            expanded.discard(node_key)
        else:
            expanded.add(node_key)
    st.session_state.lr_active_folder = node_key


def _folder_contains_active(node):
    if node["key"] == st.session_state.lr_active_folder:
        return True
    return any(_folder_contains_active(c) for c in node.get("children") or [])


# ------------------------------------------------------------
# TAB BAR
# Streamlit columns can't natively size to their content — they
# only take a relative ratio of the row's total width. Rather
# than estimate pixel widths from character counts (fragile: it
# depends on the actual rendered font/padding, which a Python
# formula can't know), the tab row is wrapped in a keyed
# container and every column inside it is forced via CSS to
# hug its own content (flex: 0 0 auto) — letting the browser do
# the actual text measurement — except the trailing spacer
# column, which keeps growing to push all tabs to the left.
# ------------------------------------------------------------

open_tabs = st.session_state.lr_open_tabs

with st.container(key="tab_bar_row"):
    # Initial ratios barely matter — the CSS above overrides every
    # column to auto-size to its content regardless of what's passed
    # here, aside from the trailing spacer column.
    tab_cols = st.columns([1] * (len(open_tabs) + 1) + [6])

    with tab_cols[0]:
        st.button(
            "Liste des rapports",
            key="tab_liste_btn",
            type="primary" if st.session_state.lr_active_tab == "liste" else "secondary",
            on_click=_activate_tab,
            args=("liste",),
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
                )
            with close_col:
                st.button(
                    "✖",
                    key=f"tab_{key}_close_btn",
                    on_click=_close_tab,
                    args=(key,),
                )

st.divider()


# ============================================================
# TAB CONTENT (UNCHANGED dispatch logic)
# ============================================================

if st.session_state.lr_active_tab in REPORT_TABS:

    REPORT_TABS[st.session_state.lr_active_tab]["render"]()

else:

    # ========================================================
    # "LISTE DES RAPPORTS" BODY — redesigned to match the
    # target screenshots: single search/filter row, card grid
    # instead of a table.
    # ========================================================

    # ---------------- SEARCH / FILTER / SORT ROW (functional) ----------------

    reports = get_reports_catalog()
    favorites = get_favorites()

    search_col, filt_col, sort_label_col, sort_col = st.columns([6, 1.3, 0.9, 1.7])

    with search_col:
        search_query = st.text_input(
            "Recherche",
            placeholder="🔍  Rechercher un rapport par nom, numéro ou mot-clé...",
            label_visibility="collapsed",
            key="report_search"
        )

    with filt_col:
        with st.popover("▽  Filtres", use_container_width=True):
            selected_categories = st.multiselect(
                "Catégorie",
                sorted(reports["categorie"].unique()),
                key="category_filter"
            )

    with sort_label_col:
        st.markdown('<div style="padding-top:8px; font-size:13px; color:#6E6A63;">Trier par</div>', unsafe_allow_html=True)

    with sort_col:
        sort_option = st.selectbox(
            "Trier par",
            ["Nom (A-Z)", "Nom (Z-A)", "Dernière modif.", "Favoris en premier"],
            label_visibility="collapsed", key="sort_select"
        )

    st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)

    # ---------------- APPLY SEARCH / FILTER / SORT ----------------

    filtered_reports = reports.copy()

    if search_query:
        q = search_query.strip().lower()
        mask = (
            filtered_reports["titre"].str.lower().str.contains(q)
            | filtered_reports["desc"].str.lower().str.contains(q)
            | filtered_reports["numero"].astype(str).str.contains(q)
        )
        filtered_reports = filtered_reports[mask]

    if selected_categories:
        filtered_reports = filtered_reports[filtered_reports["categorie"].isin(selected_categories)]

    if sort_option == "Nom (A-Z)":
        filtered_reports = filtered_reports.sort_values("titre")
    elif sort_option == "Nom (Z-A)":
        filtered_reports = filtered_reports.sort_values("titre", ascending=False)
    elif sort_option == "Dernière modif.":
        filtered_reports = filtered_reports.assign(
            _maj_sort=pd.to_datetime(filtered_reports["maj"], format="%d/%m/%Y")
        ).sort_values("_maj_sort", ascending=False)
    elif sort_option == "Favoris en premier":
        filtered_reports = filtered_reports.assign(
            _is_fav=filtered_reports["numero"].isin(favorites)
        ).sort_values("_is_fav", ascending=False)

    REPERTOIRE_TREE = [
        {"key": "tous", "label": "Tous les dossiers", "children": []},
        {"key": "favoris", "label": "Favoris", "star": True, "children": []},
        {"key": "informatique", "label": "Informatique", "children": [
            {"key": "prod_informatique", "label": "Production informatique", "children": []},
            {"key": "infocentre", "label": "Infocentre", "children": []},
            {"key": "procedure_tarifaire", "label": "Procédure tarifaire", "children": []},
        ]},
        {"key": "nouvelles_requetes", "label": "Nouvelles requêtes", "children": []},
        {"key": "referentiel_article", "label": "Référentiel Article", "children": []},
        {"key": "lmh_commerciale", "label": "LMH - Gestion Commerciale", "children": []},
        {"key": "lmh_financiere", "label": "LMH - Gestion Financière", "children": []},
        {"key": "lmh_production", "label": "LMH - Gestion Production", "children": []},
        {"key": "lmh_controle", "label": "LMH - Contrôle de gestion", "children": []},
        {"key": "lmh_logistique", "label": "LMH - Logistique", "children": []},
        {"key": "referentiel_mercure", "label": "Référentiel Mercure", "children": []},
        {"key": "divers", "label": "Divers", "children": []},
    ]

    def _render_folder_tree(nodes, depth=0):
        for node in nodes:
            node_key = node["key"]
            children = node.get("children") or []
            has_children = len(children) > 0
            is_star = node.get("star", False)
            is_expanded = node_key in st.session_state.lr_expanded_folders
            is_active = node_key == st.session_state.lr_active_folder
            is_parent_active = has_children and not is_active and _folder_contains_active(node)

            indent = "\u00A0" * (depth * 4)
            if is_star:
                prefix = "\u00A0\u00A0"
                glyph = "⭐" if is_active else "☆"
            elif has_children:
                prefix = "▾ " if is_expanded else "▸ "
                glyph = "📂" if is_expanded else "📁"
            else:
                prefix = "\u00A0\u00A0"
                glyph = "📁"

            st.button(
                f"{indent}{prefix}{glyph} {node['label']}",
                key=f"tree_node_{node_key}",
                type="primary" if (is_active or is_parent_active) else "secondary",
                on_click=_handle_folder_click,
                args=(node_key, has_children),
            )

            if has_children and is_expanded:
                _render_folder_tree(children, depth=depth + 1)

    # ---------------- LAYOUT: REPERTOIRES + CARD GRID ----------------

    left_col, right_col = st.columns([1.15, 3.4], gap="medium")

    with left_col:

        with st.container(border=True, key="repertoire_panel"):
            st.markdown('<div class="repertoire-title font-serif">Répertoires</div>', unsafe_allow_html=True)

            st.text_input(
                "Rechercher un dossier",
                placeholder="Rechercher un dossier...",
                label_visibility="collapsed",
                key="folder_search"
            )

            st.markdown('<div style="height:2px;"></div>', unsafe_allow_html=True)

            _render_folder_tree(REPERTOIRE_TREE)

            st.markdown(
                f'<div class="tree-footer">{ICON_SETTINGS}<span>Gérer les dossiers</span></div>',
                unsafe_allow_html=True
            )

    with right_col:

        # ---------------- CARD GRID (3 columns) ----------------
        # Rows with a real report key (mesures/article/commandes)
        # still open their in-app tab exactly as before — the
        # title is a genuine st.button. Each card uses a REAL
        # st.container(border=True, key=f"card_{numero}") rather
        # than a raw HTML <div> spanning two separate st.markdown()
        # calls — Streamlit widgets can't nest inside a hand-written
        # div that way (they render as siblings, not children),
        # which is what caused the broken/empty card boxes before.
        # The per-card key also lets the CSS above target each
        # card's internal spacing without touching bordered
        # containers elsewhere on the page.

        if filtered_reports.empty:

            st.info("Aucun rapport ne correspond à votre recherche.")

        else:

            reports_list = filtered_reports.to_dict("records")
            CARDS_PER_ROW = 3

            for row_start in range(0, len(reports_list), CARDS_PER_ROW):
                pair = reports_list[row_start:row_start + CARDS_PER_ROW]
                card_cols = st.columns(CARDS_PER_ROW, gap="medium")

                for card_col, r in zip(card_cols, pair):
                    with card_col:
                        with st.container(border=True, key=f"card_{r['numero']}"):

                            is_favori = r["numero"] in favorites
                            star_icon = "⭐" if is_favori else "☆"

                            top_l, top_r = st.columns([1, 5])
                            with top_l:
                                st.button(
                                    star_icon,
                                    key=f"fav_btn_{r['numero']}",
                                    on_click=_toggle_favorite,
                                    args=(r["numero"],),
                                )
                            with top_r:
                                st.markdown(
                                    f'<div class="rc-kebab" style="text-align:right;">{ICON_KEBAB}</div>',
                                    unsafe_allow_html=True,
                                )

                            if pd.notna(r["key"]):
                                st.button(
                                    r["titre"],
                                    key=f"open_{r['key']}_title_btn",
                                    on_click=_open_tab,
                                    args=(r["key"],),
                                )
                            else:
                                st.markdown(
                                    f'<div class="rc-card-title">{r["titre"]}</div>',
                                    unsafe_allow_html=True,
                                )

                            st.markdown(
                                f'<div class="rc-card-meta">N° {r["numero"]} · {r["dossier"]}</div>',
                                unsafe_allow_html=True,
                            )

                            st.markdown('<div class="rc-card-footer-divider"></div>', unsafe_allow_html=True)

                            foot_l, foot_r = st.columns(2)
                            with foot_l:
                                st.markdown(
                                    '<div class="rc-card-footer-label">Dernière modif.</div>',
                                    unsafe_allow_html=True,
                                )
                            with foot_r:
                                st.markdown(
                                    f'<div class="rc-card-footer-label" style="text-align:right;">{r["maj"]}</div>',
                                    unsafe_allow_html=True,
                                )

                st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

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