import streamlit as st
import pandas as pd
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------

st.set_page_config(
    page_title="Infocentre",
    layout="wide"
)

st.image("image.png", width=300)
# --------------------------------------------------------
# COMPACT STYLING FOR FILTER WIDGETS
# (tightens vertical spacing so the filter panel doesn't
#  eat up the screen — purely cosmetic CSS)
# --------------------------------------------------------

st.markdown(
    """
    <style>
    /* shrink the gap Streamlit adds under every widget */
    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin-bottom: -14px;
    }
    /* smaller, tighter labels */
    div[data-testid="stWidgetLabel"] label {
        font-size: 12.5px;
        margin-bottom: 0px;
    }
    /* shorter input / select boxes */
    div[data-testid="stTextInput"] input {
        padding-top: 4px;
        padding-bottom: 4px;
        height: 32px;
    }
    div[data-baseweb="select"] > div {
        min-height: 32px;
    }
    /* tighter radio and checkbox rows */
    div[data-testid="stRadio"] > div {
        gap: 0.5rem;
    }
    div[data-testid="stCheckbox"] {
        padding-top: 6px;
    }

    /* ---- Export dialog styling ---- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 10px !important;
    }
    button[kind="primary"] {
        background-color: #D9642A !important;
        border-color: #D9642A !important;
    }
    button[kind="primary"]:hover {
        background-color: #C15720 !important;
        border-color: #C15720 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------------
# SNOWFLAKE DATA
# --------------------------------------------------------

@st.cache_data(ttl=300)
def load_articles():
    conn = st.connection("snowflake", type="snowflake")
    df = conn.query(
        """
        SELECT *
        FROM INFOCENTRE_DB.PUBLIC.ARTICLES
        """,
        ttl=300
    )
    return df

if "df" not in st.session_state:
    st.session_state.df = load_articles()

df = st.session_state.df

# --------------------------------------------------------
# SHOW/HIDE TABLE STATE
# The table stays hidden until "Afficher" is clicked once.
# After that, it stays visible and updates live on every
# filter change (no need to click "Afficher" again) because
# Streamlit reruns the whole script on any widget change.
# --------------------------------------------------------

if "show_table" not in st.session_state:
    st.session_state.show_table = False

def reveal_table():
    st.session_state.show_table = True

# --------------------------------------------------------
# WIDGET KEYS FOR THE FILTER FIELDS
# (versioned with a counter so "Réinitialiser" always
#  produces brand-new widgets with their default values,
#  regardless of whatever the user typed/selected before)
# --------------------------------------------------------

if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

def _k(name):
    """Build a versioned widget key, e.g. f_metier_0, f_metier_1, ..."""
    return f"{name}_{st.session_state.reset_counter}"

def reset_filters():
    """Force every filter widget to be recreated with its default value
    (Métier / Supply Chain / Statut -> 'Tous', everything else -> empty/unchecked).
    Does NOT hide the table again — if it was visible, it stays visible,
    now showing the full unfiltered dataset."""
    st.session_state.reset_counter += 1

# --------------------------------------------------------
# EMAIL SENDING (Gmail SMTP)
# --------------------------------------------------------
# Requires a Google App Password (NOT your regular Gmail password)
# stored in .streamlit/secrets.toml as:
#
#   smtp_password = "xxxx xxxx xxxx xxxx"
#
# Generate one at: https://myaccount.google.com/apppasswords
# (Gmail must have 2-Step Verification enabled to create App Passwords.)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "noahsamueljubain@gmail.com"


def send_email_with_attachment(to_email, subject, body, attachment_bytes=None, attachment_filename=None):
    """Send an email via Gmail SMTP (STARTTLS on port 587), optionally
    with a file attached. Raises on failure — caller is expected to
    wrap this in a try/except and show st.success / st.error."""

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body or "", "plain"))

    if attachment_bytes is not None and attachment_filename:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment_bytes)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{attachment_filename}"'
        )
        msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SENDER_EMAIL, st.secrets["smtp_password"])
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

# --------------------------------------------------------
# TOP NAVIGATION
# --------------------------------------------------------

tabs = st.tabs([
    "Menu",
    "Liste des rapports",
    "Article - Emballage",
    "Article - Liste des Coloris / Taille",
    "Article - Fournisseur"
])

with tabs[3]:

    # ----------------------------------------------------
    # REPORT HEADER
    # ----------------------------------------------------

    c1, c2, c3 = st.columns([5,1,1])

    with c1:
        st.text_input(
            "Rapport",
            value="Rapport n°646 : Article - Liste des Coloris / Taille",
            disabled=True
        )

    with c2:
        st.selectbox(
            "Vue",
            ["Initiale"]
        )

    with c3:
        st.write("")
        st.button("Modification")

    st.subheader("Liste des articles - Coloris - Taille")

    general_tab, coloris_tab = st.tabs([
        "Général",
        "Coloris"
    ])

    # ====================================================
    # GENERAL TAB
    # ====================================================

    with general_tab:

        col1, col2, col3, col4 = st.columns(4, gap="small")

        # ---------------- COLUMN 1 -----------------

        with col1:

            metier = st.selectbox(
                "Métier",
                ["Tous"] + sorted(df["METIER"].unique()),
                key=_k("f_metier")
            )

            code_coloris = st.text_input(
                "Code Coloris",
                key=_k("f_code_coloris")
            )

            ref_article = st.text_input(
                "REF ARTICLE",
                key=_k("f_ref_article")
            )

        # ---------------- COLUMN 2 ----------------

        with col2:

            supply = st.selectbox(
                "Supply Chain",
                ["Tous"] + sorted(df["SUPPLY_CHAIN"].unique()),
                key=_k("f_supply")
            )

            sku = st.text_input(
                "Code SKU",
                key=_k("f_sku")
            )

            libelle_article = st.text_input(
                "Libellé Article",
                key=_k("f_libelle_article")
            )

        # ---------------- COLUMN 3 ----------------

        with col3:

            famille = st.text_input(
                "Famille",
                key=_k("f_famille")
            )

            libelle_coloris = st.text_input(
                "Libellé Coloris",
                key=_k("f_libelle_coloris")
            )

            statut = st.radio(
                "Statut",
                [
                    "Tous",
                    "Actif",
                    "Inactif"
                ],
                key=_k("f_statut"),
                horizontal=True
            )

        # ---------------- COLUMN 4 ----------------

        with col4:

            produit = st.text_input(
                "Produit",
                key=_k("f_produit")
            )

            cb1, cb2 = st.columns(2)

            with cb1:
                podium = st.checkbox("Pod-New", key=_k("f_podium"))

            with cb2:
                nouveaute = st.checkbox("Nouveauté", key=_k("f_nouveaute"))

    with coloris_tab:
        st.info("Onglet Coloris")

    st.divider()

    # ====================================================
    # FILTER FUNCTION
    # ====================================================

    def apply_filters(data):

        filtered = data.copy()

        if metier != "Tous":
            filtered = filtered[
                filtered["METIER"] == metier
            ]

        if code_coloris:
            filtered = filtered[
                filtered["CODE_COLORIS"].str.contains(code_coloris)
            ]

        if sku:
            filtered = filtered[
                filtered["CODE_SKU"].str.contains(sku)
            ]

        if libelle_article:
            filtered = filtered[
                filtered["LIBELLE_ARTICLE"].str.contains(libelle_article)
            ]

        if libelle_coloris:
            filtered = filtered[
                filtered["LIBELLE_COLORIS"].str.contains(libelle_coloris)
            ]

        if famille:
            filtered = filtered[
                filtered["FAMILLE"].str.contains(famille)
            ]

        if produit:
            filtered = filtered[
                filtered["PRODUIT"].str.contains(produit)
            ]

        if supply != "Tous":
            filtered = filtered[
                filtered["SUPPLY_CHAIN"] == supply
            ]

        if statut != "Tous":
            filtered = filtered[
                filtered["STATUT"] == statut
            ]

        if ref_article:
            filtered = filtered[
                filtered["REF_ARTICLE"].str.contains(ref_article)
            ]

        return filtered

    # ====================================================
    # EXPORT DIALOG
    # Replicates the "Exporter le rapport" modal: file format
    # picker, an "email delivery" card (SMTP send via Gmail),
    # and a "generate now" card (direct CSV download).
    # ====================================================

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

        # ---------------- EMAIL DELIVERY CARD ----------------

        with st.container(border=True):

            st.markdown("📧 &nbsp; **Pour recevoir le rapport par e-mail**")

            to_email = st.text_input(
                "E-mail du destinataire",
                value="generic.cognos@hermes.com",
                key="export_to_email"
            )

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

            spacer, c_cancel, c_ok = st.columns([4, 1, 1])

            with c_cancel:
                if st.button("Annuler", key="cancel_email_btn"):
                    st.rerun()

            with c_ok:
                if st.button("OK", key="ok_email_btn", type="primary"):
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

        # ---------------- GENERATE NOW CARD ----------------

        with st.container(border=True):

            st.markdown("ℹ️ &nbsp; **Pour générer maintenant le fichier export**")

            st.warning(
                "**Attention** — L'application n'est pas en mesure d'estimer le temps que "
                "prendra l'extraction. Les requêtes les plus lourdes peuvent provoquer une "
                "absence de réponse du serveur (timeout). Dans ce cas, nous vous invitons "
                "à utiliser l'export par email."
            )

            spacer2, c_cancel2, c_ok2 = st.columns([4, 1, 1])

            with c_cancel2:
                if st.button("Annuler", key="cancel_download_btn"):
                    st.rerun()

            with c_ok2:
                st.download_button(
                    "OK",
                    data=csv_bytes,
                    file_name="articles_export.csv",
                    mime="text/csv",
                    key="ok_download_btn"
                )

    # ====================================================
    # BUTTONS
    # ====================================================

    b1, b2, b3, b4 = st.columns(4)

    with b1:

        # First click reveals the table. After that it's a no-op —
        # the table is already visible and updates live on its own.
        st.button("Afficher", on_click=reveal_table)

    with b2:

        # Réinitialiser: wipe every filter field back to its default.
        # Table stays visible (if it already was) and now shows the
        # full unfiltered dataset.
        st.button("Réinitialiser", on_click=reset_filters)

    with b3:

        # Exporter: opens the "Exporter le rapport" dialog (email
        # delivery or immediate CSV download), matching the mockup.
        if st.button("Exporter", disabled=not st.session_state.show_table):
            export_dialog()

    with b4:

        st.button("Sauvegarder la vue")

    st.divider()

    # ====================================================
    # TABLE (hidden until "Afficher" is clicked once, then
    # live-updates on every filter change)
    # ====================================================

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

    # ====================================================
    # SQL QUERY PREVIEW (bottom of page)
    # Shows the actual SELECT statement corresponding to the
    # current filter values, mirroring what apply_filters()
    # does against the ARTICLES table.
    # ====================================================

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