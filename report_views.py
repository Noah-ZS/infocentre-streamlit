"""
Shared report content, rendered either as a standalone page
or embedded inline as an in-app tab (pages/liste_des_rapports.py's manager).
"""

import streamlit as st
from common import (
    load_articles, load_mesures_produits, load_commandes_detail,
    send_email_with_attachment
)

def _inject_compact_filter_css():
    st.markdown(
        """
        <style>
        div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] { margin-bottom: -14px; }
        div[data-testid="stWidgetLabel"] label { font-size: 13.5px; font-weight: 500; margin-bottom: 4px; }
        div[data-testid="stTextInput"] input { padding: 8px 12px; height: 38px; border-radius: 8px; }
        div[data-baseweb="select"] > div { min-height: 38px; border-radius: 8px; }
        button[kind="primary"] { background-color: #D9642A !important; border-color: #D9642A !important; padding: 6px 24px; font-weight: 500; border-radius: 8px; }
        button[kind="primary"]:hover { background-color: #C15720 !important; border-color: #C15720 !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

def _make_export_dialog(report_key, csv_bytes, default_subject, filename):
    @st.dialog("Exporter le rapport")
    def _dialog():
        st.write("Vous avez demandé un **EXPORT**.")
        st.selectbox("Format de fichier", ["📄 CSV séparateur virgule"], key=f"{report_key}_export_format")
        
        with st.container(border=True):
            st.markdown("📧 &nbsp; **Pour recevoir le rapport par e-mail**")
            to_email = st.text_input("E-mail", value="generic.cognos@hermes.com", key=f"{report_key}_export_to_email")
            subject = st.text_input("Objet", value=default_subject, key=f"{report_key}_export_subject")
            body = st.text_area("Texte", key=f"{report_key}_export_body")

            c_cancel, c_ok = st.columns([1, 1])
            with c_cancel:
                if st.button("Annuler", key=f"{report_key}_cancel_email_btn", use_container_width=True): st.rerun()
            with c_ok:
                if st.button("OK", key=f"{report_key}_ok_email_btn", type="primary", use_container_width=True):
                    try:
                        send_email_with_attachment(to_email=to_email, subject=subject, body=body, attachment_bytes=csv_bytes, attachment_filename=filename)
                        st.success("✅ E-mail envoyé.")
                    except Exception as e:
                        st.error(f"❌ Échec: {e}")

        with st.container(border=True):
            st.markdown("ℹ️ &nbsp; **Pour générer maintenant le fichier export**")
            c_cancel2, c_ok2 = st.columns([1, 1])
            with c_cancel2:
                if st.button("Annuler", key=f"{report_key}_cancel_download_btn", use_container_width=True): st.rerun()
            with c_ok2:
                st.download_button("Télécharger", data=csv_bytes, file_name=filename, mime="text/csv", key=f"{report_key}_ok_download_btn", use_container_width=True)
    return _dialog

# ================================================================
# 1. ARTICLE - LISTE DES COLORIS / TAILLE
# ================================================================

def render_article_coloris_view():
    _inject_compact_filter_css()
    if "art_df" not in st.session_state: st.session_state.art_df = load_articles()
    df = st.session_state.art_df
    if "art_show_table" not in st.session_state: st.session_state.art_show_table = False
    if "art_reset_counter" not in st.session_state: st.session_state.art_reset_counter = 0

    def _k(name): return f"art_{name}_{st.session_state.art_reset_counter}"
    def reveal_table(): st.session_state.art_show_table = True
    def reset_filters(): st.session_state.art_reset_counter += 1

    st.markdown('<div class="page-title font-serif" style="font-size:24px;">Article - Liste des Coloris / Taille</div>', unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1: metier = st.selectbox("Métier", ["Tous"] + sorted(df["METIER"].unique()), key=_k("f_metier"))
    with col2: supply = st.selectbox("Supply Chain", ["Tous"] + sorted(df["SUPPLY_CHAIN"].unique()), key=_k("f_supply"))
    with col3: search = st.text_input("Rechercher", placeholder="Code ou libellé...", key=_k("f_search"))

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    def apply_filters(data):
        filtered = data.copy()
        if metier != "Tous": filtered = filtered[filtered["METIER"] == metier]
        if supply != "Tous": filtered = filtered[filtered["SUPPLY_CHAIN"] == supply]
        if search:
            mask = (filtered["CODE_SKU"].str.contains(search, case=False) | filtered["LIBELLE_ARTICLE"].str.contains(search, case=False))
            filtered = filtered[mask]
        return filtered

    b1, b2, b3, spacer = st.columns([1.5, 1.5, 1.5, 5])
    with b1: st.button("Afficher", type="primary", on_click=reveal_table, key="art_afficher_btn", use_container_width=True)
    with b2: st.button("Réinitialiser", on_click=reset_filters, key="art_reinit_btn", use_container_width=True)
    with b3:
        export_source = apply_filters(df) if st.session_state.art_show_table else df.iloc[0:0]
        csv_bytes = export_source.to_csv(index=False).encode("utf-8-sig")
        if st.button("Exporter", disabled=not st.session_state.art_show_table, key="art_exporter_btn", use_container_width=True):
            _make_export_dialog("art", csv_bytes, "Extraction détaillée", "articles_export.csv")()

    st.divider()

    if st.session_state.art_show_table:
        st.session_state.art_filtered_df = apply_filters(df)
        st.dataframe(st.session_state.art_filtered_df, use_container_width=True, hide_index=True, height=500)
    else:
        st.info("Sélectionnez vos filtres et cliquez sur Afficher.")

# ================================================================
# 2. MESURES DES NOUVEAUX PRODUITS
# ================================================================

def render_mesures_produits_view():
    _inject_compact_filter_css()
    if "mes_df" not in st.session_state: st.session_state.mes_df = load_mesures_produits()
    df = st.session_state.mes_df
    if "mes_show_table" not in st.session_state: st.session_state.mes_show_table = False
    if "mes_reset_counter" not in st.session_state: st.session_state.mes_reset_counter = 0

    def _k(name): return f"mes_{name}_{st.session_state.mes_reset_counter}"
    def reveal_table(): st.session_state.mes_show_table = True
    def reset_filters(): st.session_state.mes_reset_counter += 1

    st.markdown('<div class="page-title font-serif" style="font-size:24px;">Suivi des mesures et performances produits</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 3])
    with col1: categories = st.multiselect("Catégorie", sorted(df["CATEGORIE"].unique()), placeholder="Choose options", key=_k("f_categorie"))
    with col2: statut = st.selectbox("Statut", ["Tous"] + sorted(df["STATUT_TEST"].unique()), key=_k("f_statut"))
    with col3: search = st.text_input("Rechercher", placeholder="Code ou nom de produit...", key=_k("f_search"))

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    def apply_filters(data):
        filtered = data.copy()
        if categories: filtered = filtered[filtered["CATEGORIE"].isin(categories)]
        if statut != "Tous": filtered = filtered[filtered["STATUT_TEST"] == statut]
        if search:
            mask = (filtered["CODE_PRODUIT"].str.contains(search, case=False) | filtered["NOM_PRODUIT"].str.contains(search, case=False))
            filtered = filtered[mask]
        return filtered

    # Exact layout matching screenshot
    b1, space1, b2, space2, b3 = st.columns([1.2, 3, 1.5, 3, 1.2])
    with b1: st.button("Afficher", type="primary", on_click=reveal_table, key="mes_afficher_btn", use_container_width=True)
    with b2: st.button("Réinitialiser", on_click=reset_filters, key="mes_reinit_btn", use_container_width=True)
    with b3:
        export_source = apply_filters(df) if st.session_state.mes_show_table else df.iloc[0:0]
        csv_bytes = export_source.to_csv(index=False).encode("utf-8-sig")
        if st.button("Exporter", disabled=not st.session_state.mes_show_table, key="mes_exporter_btn", use_container_width=True):
            _make_export_dialog("mes", csv_bytes, "Extraction détaillée", "mesures_produits_export.csv")()

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)
    st.divider()

    if st.session_state.mes_show_table:
        st.session_state.mes_filtered_df = apply_filters(df)
        st.dataframe(st.session_state.mes_filtered_df, use_container_width=True, hide_index=True, height=500)

# ================================================================
# 3. COMMANDES - DÉTAIL
# ================================================================

def render_commandes_detail_view():
    _inject_compact_filter_css()
    if "cmd_df" not in st.session_state: st.session_state.cmd_df = load_commandes_detail()
    df = st.session_state.cmd_df
    if "cmd_show_table" not in st.session_state: st.session_state.cmd_show_table = False
    if "cmd_reset_counter" not in st.session_state: st.session_state.cmd_reset_counter = 0

    def _k(name): return f"cmd_{name}_{st.session_state.cmd_reset_counter}"
    def reveal_table(): st.session_state.cmd_show_table = True
    def reset_filters(): st.session_state.cmd_reset_counter += 1

    st.markdown('<div class="page-title font-serif" style="font-size:24px;">Détail des commandes et lignes associées</div>', unsafe_allow_html=True)
    st.divider()

    df_dates = df["DATE_COMMANDE"]
    min_date, max_date = df_dates.min(), df_dates.max()

    col1, col2, col3 = st.columns([2, 2, 3])
    with col1: date_start = st.date_input("Date début", value=min_date, key=_k("f_date_start"))
    with col2: date_end = st.date_input("Date fin", value=max_date, key=_k("f_date_end"))
    with col3: statuts = st.multiselect("Statut", sorted(df["STATUT_LIVRAISON"].unique()), key=_k("f_statut"))

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    def apply_filters(data):
        filtered = data.copy()
        filtered = filtered[(filtered["DATE_COMMANDE"] >= date_start) & (filtered["DATE_COMMANDE"] <= date_end)]
        if statuts: filtered = filtered[filtered["STATUT_LIVRAISON"].isin(statuts)]
        return filtered

    b1, space1, b2, space2, b3 = st.columns([1.2, 3, 1.5, 3, 1.2])
    with b1: st.button("Afficher", type="primary", on_click=reveal_table, key="cmd_afficher_btn", use_container_width=True)
    with b2: st.button("Réinitialiser", on_click=reset_filters, key="cmd_reinit_btn", use_container_width=True)
    with b3:
        export_source = apply_filters(df) if st.session_state.cmd_show_table else df.iloc[0:0]
        csv_bytes = export_source.to_csv(index=False).encode("utf-8-sig")
        if st.button("Exporter", disabled=not st.session_state.cmd_show_table, key="cmd_exporter_btn", use_container_width=True):
            _make_export_dialog("cmd", csv_bytes, "Extraction détaillée", "commandes_detail_export.csv")()

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)
    st.divider()

    if st.session_state.cmd_show_table:
        st.session_state.cmd_filtered_df = apply_filters(df)
        st.dataframe(st.session_state.cmd_filtered_df, use_container_width=True, hide_index=True, height=500)