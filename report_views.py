"""
Shared report content, rendered either as a standalone page
(pages/article_coloris.py, pages/mesures_produits.py,
pages/commandes_detail.py) or embedded inline as an in-app tab
(pages/liste_des_rapports.py's multi-tab manager).

IMPORTANT: since several of these views can be open as separate
in-app tabs at the same time, every piece of session_state and
every widget key is namespaced per report (prefixes "art_",
"mes_", "cmd_") so switching tabs never leaks one report's data,
filters, or reset-counter into another's.
"""

import streamlit as st
from common import (
    load_articles, load_mesures_produits, load_commandes_detail,
    send_email_with_attachment
)


# ================================================================
# SHARED HELPERS
# ================================================================

def _inject_compact_filter_css():
    st.markdown(
        """
        <style>
        div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] { margin-bottom: -14px; }
        div[data-testid="stWidgetLabel"] label { font-size: 12.5px; margin-bottom: 0px; }
        div[data-testid="stTextInput"] input { padding-top: 4px; padding-bottom: 4px; height: 32px; }
        div[data-baseweb="select"] > div { min-height: 32px; }
        div[data-testid="stRadio"] > div { gap: 0.5rem; }
        div[data-testid="stCheckbox"] { padding-top: 6px; }
        div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 10px !important; }
        button[kind="primary"] { background-color: #D9642A !important; border-color: #D9642A !important; }
        button[kind="primary"]:hover { background-color: #C15720 !important; border-color: #C15720 !important; }
        </style>
        """,
        unsafe_allow_html=True
    )


def _make_export_dialog(report_key, csv_bytes, default_subject, filename):
    """Builds the 'Exporter le rapport' dialog (email delivery via
    Gmail, or immediate CSV download) for a given report. Returns a
    callable — call it to actually open the dialog."""

    @st.dialog("Exporter le rapport")
    def _dialog():

        st.write("Vous avez demandé un **EXPORT**.")

        st.selectbox(
            "Format de fichier",
            ["📄 CSV séparateur virgule avec symbole décimale : virgule"],
            key=f"{report_key}_export_format"
        )

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        with st.container(border=True):

            st.markdown("📧 &nbsp; **Pour recevoir le rapport par e-mail**")

            to_email = st.text_input(
                "E-mail du destinataire", value="generic.cognos@hermes.com",
                key=f"{report_key}_export_to_email"
            )
            subject = st.text_input(
                "Objet de l'e-mail", value=default_subject,
                key=f"{report_key}_export_subject"
            )
            body = st.text_area(
                "Texte de l'e-mail (optionnel)",
                placeholder="Ajoutez un message personnalisé (optionnel)...",
                key=f"{report_key}_export_body"
            )

            spacer, c_cancel, c_ok = st.columns([2, 1, 1])

            with c_cancel:
                if st.button("Annuler", key=f"{report_key}_cancel_email_btn", use_container_width=True):
                    st.rerun()

            with c_ok:
                if st.button("OK", key=f"{report_key}_ok_email_btn", type="primary", use_container_width=True):
                    try:
                        send_email_with_attachment(
                            to_email=to_email, subject=subject, body=body,
                            attachment_bytes=csv_bytes, attachment_filename=filename,
                        )
                        st.success("✅ E-mail envoyé avec succès.")
                    except Exception as e:
                        st.error(f"❌ Échec de l'envoi de l'e-mail : {e}")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        with st.container(border=True):

            st.markdown("ℹ️ &nbsp; **Pour générer maintenant le fichier export**")

            st.warning(
                "**Attention** — L'application n'est pas en mesure d'estimer le temps que "
                "prendra l'extraction. Les requêtes les plus lourdes peuvent provoquer une "
                "absence de réponse du serveur (timeout). Dans ce cas, nous vous invitons "
                "à utiliser l'export par email."
            )

            spacer2, c_cancel2, c_ok2 = st.columns([2, 1, 1])

            with c_cancel2:
                if st.button("Annuler", key=f"{report_key}_cancel_download_btn", use_container_width=True):
                    st.rerun()

            with c_ok2:
                st.download_button(
                    "OK", data=csv_bytes, file_name=filename, mime="text/csv",
                    key=f"{report_key}_ok_download_btn", use_container_width=True
                )

    return _dialog


# ================================================================
# 1. ARTICLE - LISTE DES COLORIS / TAILLE
# ================================================================

def render_article_coloris_view():

    _inject_compact_filter_css()

    if "art_df" not in st.session_state:
        st.session_state.art_df = load_articles()
    df = st.session_state.art_df

    if "art_show_table" not in st.session_state:
        st.session_state.art_show_table = False

    if "art_reset_counter" not in st.session_state:
        st.session_state.art_reset_counter = 0

    def _k(name):
        return f"art_{name}_{st.session_state.art_reset_counter}"

    def reveal_table():
        st.session_state.art_show_table = True

    def reset_filters():
        st.session_state.art_reset_counter += 1

    c1, c2, c3 = st.columns([5, 1, 1])
    with c1:
        st.text_input("Rapport", value="Rapport n°646 : Article - Liste des Coloris / Taille", disabled=True, key="art_rapport_label")
    with c2:
        st.selectbox("Vue", ["Initiale"], key="art_vue")
    with c3:
        st.write("")
        st.button("Modification", key="art_modif_btn")

    st.subheader("Liste des articles - Coloris - Taille")

    general_tab, coloris_tab = st.tabs(["Général", "Coloris"])

    with general_tab:
        col1, col2, col3, col4 = st.columns(4, gap="small")
        with col1:
            metier = st.selectbox("Métier", ["Tous"] + sorted(df["METIER"].unique()), key=_k("f_metier"))
            code_coloris = st.text_input("Code Coloris", key=_k("f_code_coloris"))
            ref_article = st.text_input("REF ARTICLE", key=_k("f_ref_article"))
        with col2:
            supply = st.selectbox("Supply Chain", ["Tous"] + sorted(df["SUPPLY_CHAIN"].unique()), key=_k("f_supply"))
            sku = st.text_input("Code SKU", key=_k("f_sku"))
            libelle_article = st.text_input("Libellé Article", key=_k("f_libelle_article"))
        with col3:
            famille = st.text_input("Famille", key=_k("f_famille"))
            libelle_coloris = st.text_input("Libellé Coloris", key=_k("f_libelle_coloris"))
            statut = st.radio("Statut", ["Tous", "Actif", "Inactif"], key=_k("f_statut"), horizontal=True)
        with col4:
            produit = st.text_input("Produit", key=_k("f_produit"))
            cb1, cb2 = st.columns(2)
            with cb1:
                st.checkbox("Pod-New", key=_k("f_podium"))
            with cb2:
                st.checkbox("Nouveauté", key=_k("f_nouveaute"))

    with coloris_tab:
        st.info("Onglet Coloris")

    st.divider()

    def apply_filters(data):
        filtered = data.copy()
        if metier != "Tous":
            filtered = filtered[filtered["METIER"] == metier]
        if code_coloris:
            filtered = filtered[filtered["CODE_COLORIS"].str.contains(code_coloris)]
        if sku:
            filtered = filtered[filtered["CODE_SKU"].str.contains(sku)]
        if libelle_article:
            filtered = filtered[filtered["LIBELLE_ARTICLE"].str.contains(libelle_article)]
        if libelle_coloris:
            filtered = filtered[filtered["LIBELLE_COLORIS"].str.contains(libelle_coloris)]
        if famille:
            filtered = filtered[filtered["FAMILLE"].str.contains(famille)]
        if produit:
            filtered = filtered[filtered["PRODUIT"].str.contains(produit)]
        if supply != "Tous":
            filtered = filtered[filtered["SUPPLY_CHAIN"] == supply]
        if statut != "Tous":
            filtered = filtered[filtered["STATUT"] == statut]
        if ref_article:
            filtered = filtered[filtered["REF_ARTICLE"].str.contains(ref_article)]
        return filtered

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.button("Afficher", on_click=reveal_table, key="art_afficher_btn")
    with b2:
        st.button("Réinitialiser", on_click=reset_filters, key="art_reinit_btn")
    with b3:
        export_source = apply_filters(df) if st.session_state.art_show_table else df.iloc[0:0]
        csv_bytes = export_source.to_csv(index=False).encode("utf-8-sig")
        if st.button("Exporter", disabled=not st.session_state.art_show_table, key="art_exporter_btn"):
            _make_export_dialog(
                "art", csv_bytes,
                "Ariane - Rapport n°646 : Article - Liste des Coloris / Taille : Extraction détaillée",
                "articles_export.csv",
            )()
    with b4:
        st.button("Sauvegarder la vue", key="art_sauvegarder_btn")

    st.divider()

    if st.session_state.art_show_table:
        st.session_state.art_filtered_df = apply_filters(df)
        st.data_editor(st.session_state.art_filtered_df, use_container_width=True, hide_index=True, height=500)
    else:
        st.info("Cliquez sur **Afficher** pour afficher les résultats.")

    def build_sql():
        where = []
        if metier != "Tous":
            where.append(f"METIER = '{metier}'")
        if code_coloris:
            where.append(f"CODE_COLORIS LIKE '%{code_coloris}%'")
        if ref_article:
            where.append(f"REF_ARTICLE LIKE '%{ref_article}%'")
        if sku:
            where.append(f"CODE_SKU LIKE '%{sku}%'")
        if libelle_article:
            where.append(f"LIBELLE_ARTICLE LIKE '%{libelle_article}%'")
        if libelle_coloris:
            where.append(f"LIBELLE_COLORIS LIKE '%{libelle_coloris}%'")
        if famille:
            where.append(f"FAMILLE LIKE '%{famille}%'")
        if produit:
            where.append(f"PRODUIT LIKE '%{produit}%'")
        if supply != "Tous":
            where.append(f"SUPPLY_CHAIN = '{supply}'")
        if statut != "Tous":
            where.append(f"STATUT = '{statut}'")
        sql = "SELECT *\nFROM INFOCENTRE_DB.PUBLIC.ARTICLES"
        if where:
            sql += "\nWHERE " + "\n  AND ".join(where)
        return sql

    st.divider()
    with st.expander("Afficher la requête SQL"):
        st.code(build_sql(), language="sql")


# ================================================================
# 2. MESURES DES NOUVEAUX PRODUITS
# ================================================================

def render_mesures_produits_view():

# Inside render_mesures_produits_view() in report_views.py

b1, b2, b3, spacer = st.columns([1, 1, 1, 4])
with b1:
    st.button("Afficher", on_click=reveal_table, key="mes_afficher_btn", type="primary", use_container_width=True)
with b2:
    # Streamlit natively doesn't support "outlined" primary. 
    # It will render as a secondary button unless we inject CSS targeting this specific key.
    st.button("Réinitialiser", on_click=reset_filters, key="mes_reinit_btn", use_container_width=True)
with b3:
    export_source = apply_filters(df) if st.session_state.mes_show_table else df.iloc[0:0]
    csv_bytes = export_source.to_csv(index=False).encode("utf-8-sig")
    if st.button("Exporter", disabled=not st.session_state.mes_show_table, key="mes_exporter_btn", use_container_width=True):
         _make_export_dialog(...)()

# ================================================================
# 3. COMMANDES - DÉTAIL
# ================================================================

def render_commandes_detail_view():

    _inject_compact_filter_css()

    if "cmd_df" not in st.session_state:
        st.session_state.cmd_df = load_commandes_detail()
    df = st.session_state.cmd_df

    if "cmd_show_table" not in st.session_state:
        st.session_state.cmd_show_table = False

    if "cmd_reset_counter" not in st.session_state:
        st.session_state.cmd_reset_counter = 0

    def _k(name):
        return f"cmd_{name}_{st.session_state.cmd_reset_counter}"

    def reveal_table():
        st.session_state.cmd_show_table = True

    def reset_filters():
        st.session_state.cmd_reset_counter += 1

    st.text_input(
        "Rapport", value="Rapport n°667 : Commandes - Détail",
        disabled=True, key="cmd_rapport_label"
    )
    st.subheader("Détail des commandes et lignes associées")
    st.divider()

    df_dates = df["DATE_COMMANDE"]
    min_date, max_date = df_dates.min(), df_dates.max()

    col1, col2, col3, col4 = st.columns([1.1, 1.1, 1.6, 1.6])
    with col1:
        date_start = st.date_input("Date début", value=min_date, key=_k("f_date_start"))
    with col2:
        date_end = st.date_input("Date fin", value=max_date, key=_k("f_date_end"))
    with col3:
        statuts = st.multiselect(
            "Statut de livraison", sorted(df["STATUT_LIVRAISON"].unique()), key=_k("f_statut")
        )
    with col4:
        search = st.text_input(
            "Rechercher", placeholder="Client ou n° de commande...", key=_k("f_search")
        )

    st.divider()

    def apply_filters(data):
        filtered = data.copy()
        filtered = filtered[
            (filtered["DATE_COMMANDE"] >= date_start) & (filtered["DATE_COMMANDE"] <= date_end)
        ]
        if statuts:
            filtered = filtered[filtered["STATUT_LIVRAISON"].isin(statuts)]
        if search:
            mask = (
                filtered["NOM_CLIENT"].str.contains(search, case=False)
                | filtered["ID_COMMANDE"].str.contains(search, case=False)
            )
            filtered = filtered[mask]
        return filtered

    b1, b2, b3 = st.columns(3)
    with b1:
        st.button("Afficher", on_click=reveal_table, key="cmd_afficher_btn")
    with b2:
        st.button("Réinitialiser", on_click=reset_filters, key="cmd_reinit_btn")
    with b3:
        export_source = apply_filters(df) if st.session_state.cmd_show_table else df.iloc[0:0]
        csv_bytes = export_source.to_csv(index=False).encode("utf-8-sig")
        if st.button("Exporter", disabled=not st.session_state.cmd_show_table, key="cmd_exporter_btn"):
            _make_export_dialog(
                "cmd", csv_bytes,
                "Ariane - Rapport n°667 : Commandes - Détail : Extraction détaillée",
                "commandes_detail_export.csv",
            )()

    st.divider()

    if st.session_state.cmd_show_table:
        st.session_state.cmd_filtered_df = apply_filters(df)
        st.data_editor(st.session_state.cmd_filtered_df, use_container_width=True, hide_index=True, height=500)
    else:
        st.info("Cliquez sur **Afficher** pour afficher les résultats.")

    def build_sql():
        where = [f"DATE_COMMANDE BETWEEN '{date_start}' AND '{date_end}'"]
        if statuts:
            statut_list = ", ".join(f"'{s}'" for s in statuts)
            where.append(f"STATUT_LIVRAISON IN ({statut_list})")
        if search:
            where.append(f"(NOM_CLIENT ILIKE '%{search}%' OR ID_COMMANDE ILIKE '%{search}%')")
        sql = "SELECT *\nFROM INFOCENTRE_DB.PUBLIC.COMMANDES_DETAIL"
        sql += "\nWHERE " + "\n  AND ".join(where)
        return sql

    st.divider()
    with st.expander("Afficher la requête SQL"):
        st.code(build_sql(), language="sql")