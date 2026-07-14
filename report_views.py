"""
Shared report content that can be rendered either as its own
standalone page (pages/article_coloris.py) or embedded inline
as an in-app tab (pages/liste_des_rapports.py's tab system).

Keeping this in one place means both entry points stay in sync
with a single copy of the filter/export/table logic.
"""

import streamlit as st
from common import load_articles, send_email_with_attachment


def render_article_coloris_view():
    """Renders the full 'Article - Liste des Coloris / Taille' report
    body: compact filter styling, Snowflake data, filters, export
    dialog (with Gmail delivery), results table, and SQL preview.
    Does NOT render a page title or top bar — the caller decides
    whether/how to show those (standalone page vs. embedded tab)."""

    # ----------------------------------------------------
    # COMPACT STYLING FOR FILTER WIDGETS
    # ----------------------------------------------------

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

    # ----------------------------------------------------
    # SNOWFLAKE DATA
    # ----------------------------------------------------

    if "df" not in st.session_state:
        st.session_state.df = load_articles()

    df = st.session_state.df

    # ----------------------------------------------------
    # SHOW/HIDE TABLE STATE
    # ----------------------------------------------------

    if "show_table" not in st.session_state:
        st.session_state.show_table = False

    def reveal_table():
        st.session_state.show_table = True

    # ----------------------------------------------------
    # WIDGET KEYS FOR THE FILTER FIELDS
    # ----------------------------------------------------

    if "reset_counter" not in st.session_state:
        st.session_state.reset_counter = 0

    def _k(name):
        return f"{name}_{st.session_state.reset_counter}"

    def reset_filters():
        st.session_state.reset_counter += 1

    # ----------------------------------------------------
    # REPORT HEADER
    # ----------------------------------------------------

    c1, c2, c3 = st.columns([5, 1, 1])

    with c1:
        st.text_input(
            "Rapport",
            value="Rapport n°646 : Article - Liste des Coloris / Taille",
            disabled=True
        )

    with c2:
        st.selectbox("Vue", ["Initiale"])

    with c3:
        st.write("")
        st.button("Modification", key="modif_btn")

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
                podium = st.checkbox("Pod-New", key=_k("f_podium"))
            with cb2:
                nouveaute = st.checkbox("Nouveauté", key=_k("f_nouveaute"))

    with coloris_tab:
        st.info("Onglet Coloris")

    st.divider()

    # ----------------------------------------------------
    # FILTER FUNCTION
    # ----------------------------------------------------

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

    # ----------------------------------------------------
    # EXPORT DIALOG
    # ----------------------------------------------------

    @st.dialog("Exporter le rapport")
    def export_dialog():

        st.write("Vous avez demandé un **EXPORT**.")

        file_format = st.selectbox(
            "Format de fichier",
            [
                "📄 CSV séparateur virgule avec symbole décimale : virgule",
                "📄 CSV séparateur point-virgule avec symbole décimale : virgule",
            ],
            key="export_format"
        )

        separator = ";" if "point-virgule" in file_format else ","
        export_source = apply_filters(df) if st.session_state.show_table else df.iloc[0:0]
        csv_bytes = export_source.to_csv(index=False, sep=separator).encode("utf-8-sig")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        with st.container(border=True):

            st.markdown("📧 &nbsp; **Pour recevoir le rapport par e-mail**")

            to_email = st.text_input("E-mail du destinataire", value="generic.cognos@hermes.com", key="export_to_email")
            subject = st.text_input(
                "Objet de l'e-mail",
                value="Ariane - Rapport n°646 : Article - Liste des Coloris / Taille : Extraction détaillée",
                key="export_subject"
            )
            body = st.text_area(
                "Texte de l'e-mail (optionnel)",
                placeholder="Ajoutez un message personnalisé (optionnel)...",
                key="export_body"
            )

            spacer, c_cancel, c_ok = st.columns([2, 1, 1])

            cancel_email_clicked = False
            ok_email_clicked = False

            with c_cancel:
                cancel_email_clicked = st.button("Annuler", key="cancel_email_btn", use_container_width=True)

            with c_ok:
                ok_email_clicked = st.button("OK", key="ok_email_btn", type="primary", use_container_width=True)

            if cancel_email_clicked:
                st.rerun()

            if ok_email_clicked:
                try:
                    send_email_with_attachment(
                        to_email=to_email,
                        subject=subject,
                        body=body,
                        attachment_bytes=csv_bytes,
                        attachment_filename="articles_export.csv",
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
                if st.button("Annuler", key="cancel_download_btn", use_container_width=True):
                    st.rerun()

            with c_ok2:
                st.download_button(
                    "OK", data=csv_bytes, file_name="articles_export.csv",
                    mime="text/csv", key="ok_download_btn", use_container_width=True
                )

    # ----------------------------------------------------
    # BUTTONS
    # ----------------------------------------------------

    b1, b2, b3, b4 = st.columns(4)

    with b1:
        st.button("Afficher", on_click=reveal_table, key="afficher_btn")

    with b2:
        st.button("Réinitialiser", on_click=reset_filters, key="reinit_btn")

    with b3:
        if st.button("Exporter", disabled=not st.session_state.show_table, key="exporter_btn"):
            export_dialog()

    with b4:
        st.button("Sauvegarder la vue", key="sauvegarder_btn")

    st.divider()

    # ----------------------------------------------------
    # TABLE
    # ----------------------------------------------------

    if st.session_state.show_table:
        st.session_state.filtered_df = apply_filters(df)
        st.data_editor(
            st.session_state.filtered_df,
            use_container_width=True,
            hide_index=True,
            height=500
        )
    else:
        st.info("Cliquez sur **Afficher** pour afficher les résultats.")

    # ----------------------------------------------------
    # SQL QUERY PREVIEW
    # ----------------------------------------------------

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