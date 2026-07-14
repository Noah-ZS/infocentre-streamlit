"""
Shared building blocks for the Infocentre multi-page app:
icons, global CSS/design tokens, the custom sidebar + top bar,
the Snowflake data loader, and the Gmail sending helper.

Imported by streamlit_app.py (the router) and by every page in
pages/. Do NOT call st.set_page_config() here — only the router
may call it, and only once.
"""

import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st

# ============================================================
# ICONS
# ============================================================

def icon(path, size=18, stroke_width=1.8):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )

ICON_DOC = icon('<path d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z"/><path d="M14 3v5h5"/>')
ICON_CLOCK = icon('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>')
ICON_STAR = icon('<path d="M12 3.5l2.5 5.5 6 .6-4.5 4 1.3 6-5.3-3-5.3 3 1.3-6-4.5-4 6-.6 2.5-5.5Z"/>', stroke_width=1.6)
ICON_CHEVRON_RIGHT = icon('<path d="m9 6 6 6-6 6"/>', size=15, stroke_width=2.1)
ICON_CHEVRON_DOWN = icon('<path d="m6 9 6 6 6-6"/>', size=15, stroke_width=2.1)
ICON_ARROW_UP = icon('<path d="M12 19V6"/><path d="m6 12 6-6 6 6"/>', size=13, stroke_width=2.3)
ICON_ARROW_DOWN = icon('<path d="M12 5v13"/><path d="m18 12-6 6-6-6"/>', size=13, stroke_width=2.3)
ICON_KEBAB = icon('<circle cx="12" cy="5" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="12" cy="19" r="1.3"/>', size=16)
ICON_LOGOUT = icon('<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/>', size=17)
ICON_SEARCH = icon('<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>', size=17)
ICON_FOLDER = icon('<path d="M4 6a1 1 0 0 1 1-1h4.5l1.5 2H19a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6Z"/>', size=16)
ICON_FILTER = icon('<path d="M4 5h16"/><path d="M7 10h10"/><path d="M10 15h4"/>', size=15)
ICON_INFO = icon('<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>', size=13)
ICON_LIST_VIEW = icon('<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>', size=15)
ICON_GRID_VIEW = icon('<rect x="4" y="4" width="7" height="7" rx="1"/><rect x="13" y="4" width="7" height="7" rx="1"/><rect x="4" y="13" width="7" height="7" rx="1"/><rect x="13" y="13" width="7" height="7" rx="1"/>', size=15)
ICON_SETTINGS = icon('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.9V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z"/>', size=15)
ICON_LANGUAGE = icon('<path d="M4 5h16M9 3v2c0 4.4-3.6 8-8 8M17 21l-5-10-5 10M13.5 14h3M2 13s3.5-2 6-6"/>', size=17)

# ============================================================
# GLOBAL DESIGN TOKENS + CSS
# ============================================================

def inject_global_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');

        :root {
            --ink: #1C1B19;
            --ink-soft: #6E6A63;
            --accent: #D9642A;
            --accent-bg: #FBEAE0;
            --cream: #FAF8F4;
            --card: #FFFFFF;
            --line: #EAE5DC;
            --success: #1E8A5F;
        }

        #MainMenu, footer { visibility: hidden; height: 0; }
        div[data-testid="stDecoration"] { display: none; }
        div[data-testid="stToolbar"] { visibility: hidden; }
        header[data-testid="stHeader"] { display: none !important; height: 0px !important; }
        
        .stApp { background: #FFFFFF; padding-top: 0 !important; }
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--ink); }
        .font-serif { font-family: 'Fraunces', serif; }

        section.main { padding-top: 0 !important; }
        section.main .block-container {
            max-width: 1440px;
            margin: 0 auto;
            padding: 2rem 3rem 4rem 3rem !important;
        }

        /* ---------------- SIDEBAR POLISHING ---------------- */
        section[data-testid="stSidebar"] {
            background: var(--cream);
            border-right: 1px solid var(--line);
            min-width: 272px;
            max-width: 272px;
        }
        section[data-testid="stSidebar"] > div:first-child { 
            padding: 2rem 1.5rem !important; 
        }

        .brand-container { display: flex; align-items: center; gap: 12px; margin-bottom: 30px; }
        .brand-logo-text { font-family: 'Fraunces', serif; font-size: 16px; font-weight: 600; line-height: 1; text-align: center; }
        .brand-logo-sub { font-family: 'Inter', sans-serif; font-size: 8px; letter-spacing: 0.2em; display: block; margin-top: 2px;}
        .brand-word { font-family: 'Fraunces', serif; font-size: 26px; font-weight: 400; color: var(--ink); }

        section[data-testid="stSidebar"] a[data-testid^="stPageLink"] {
            display: flex; align-items: center; gap: 12px;
            padding: 10px 14px !important; border-radius: 8px;
            font-size: 14.5px !important; font-weight: 500;
            color: #57534A !important; border-left: 3px solid transparent;
            margin-bottom: 4px; transition: all 0.2s;
        }
        section[data-testid="stSidebar"] a[data-testid^="stPageLink"]:hover { background: #F1EEE7; }
        section[data-testid="stSidebar"] a[data-testid^="stPageLink"][aria-current="page"] {
            color: var(--ink) !important; background: #EBE6DC; font-weight: 600;
        }

        .logout-row {
            display: flex; align-items: center; gap: 10px; cursor: pointer;
            color: #57534A; font-size: 14px; font-weight: 500; margin-top: 16px;
            transition: color 0.2s;
        }
        .logout-row:hover { color: var(--accent); }

        /* ---------------- MAIN TOP BAR ---------------- */
        .topbar-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--line); }
        .breadcrumb { font-size: 14px; font-weight: 500; color: var(--accent); }
        .topbar-right { display: flex; align-items: center; gap: 14px; color: var(--ink-soft); font-size: 13.5px; }
        .avatar { width: 34px; height: 34px; border-radius: 50%; background: #EFECE6; color: var(--ink); display: flex; align-items: center; justify-content: center; font-size: 12.5px; font-weight: 600; }

        .page-title { font-family: 'Fraunces', serif; font-size: 34px; font-weight: 600; color: var(--ink); margin: 0 0 6px 0; line-height: 1.2; }
        .page-subtitle { color: var(--ink-soft); font-size: 15px; margin: 0 0 24px 0; }

        /* ---------------- LIST PANELS & CARDS (Reports List) ---------------- */
        .repertoire-panel { background: #FFFFFF; border-radius: 12px; padding: 18px 16px; height: 100%; }
        .tree-item { display: flex; align-items: center; gap: 8px; padding: 8px 6px; font-size: 13.5px; color: #4A4640; border-radius: 6px; cursor: pointer;}
        .tree-item:hover { background: #F5F2EC; }
        .tree-item.tree-active { color: var(--accent); font-weight: 600; }
        .tree-item.tree-parent-active { color: var(--accent); font-weight: 600; }
        .tree-item .tree-chevron { color: #B4AFA6; flex-shrink: 0; }
        .tree-item .tree-icon { color: #C9A227; flex-shrink: 0; }
        .tree-item.tree-active .tree-icon, .tree-item.tree-parent-active .tree-icon { color: var(--accent); }
        .tree-indent-1 { padding-left: 24px; }
        
        .report-grid-card { border: 1px solid var(--line); border-radius: 12px; padding: 16px; background: #FFFFFF; transition: box-shadow 0.2s; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
        .report-grid-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .rgc-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .rgc-fav { display: inline-flex; align-items: center; gap: 4px; font-size: 11px; font-weight: 600; color: var(--accent); background: var(--accent-bg); padding: 4px 8px; border-radius: 4px; }
        .rgc-kebab { color: #B4AFA6; cursor: pointer; }
        .rgc-id { font-size: 12px; color: var(--ink-soft); margin-top: 4px; margin-bottom: 16px; }
        .rgc-footer { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--ink-soft); margin-top: auto; padding-top: 16px; border-top: 1px solid var(--line); }
        
        /* Reset button styling inside cards to make them text-like */
        [class*="st-key-open_"][class*="_title_btn"] button { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; height: auto !important; min-height: 0 !important; text-align: left !important; justify-content: flex-start !important; white-space: normal !important; line-height: 1.4 !important; }
        [class*="st-key-open_"][class*="_title_btn"] button p { font-size: 15px !important; font-weight: 600 !important; color: var(--ink) !important; }
        [class*="st-key-open_"][class*="_title_btn"] button:hover p { color: var(--accent) !important; text-decoration: underline !important; }

        /* Custom segmented Tabs styling */
        .stButton > button[key^="tab_"] { border-radius: 12px 12px 0 0; padding: 12px 24px; border: 1px solid var(--line); border-bottom: none; font-weight: 600; font-size: 14px; background: #F8F6F2; color: #6E6A63; transition: all 0.2s; }
        .stButton > button[key^="tab_"]:hover { background: #FFFFFF; }
        .stButton > button[key^="tab_"][data-testid="stBaseButton-primary"] { background: #FFFFFF; color: var(--ink); position: relative; }
        .stButton > button[key^="tab_"][data-testid="stBaseButton-primary"]::after { content: ''; position: absolute; bottom: -1px; left: 0; right: 0; height: 3px; background: var(--accent); }

        /* Secondary Outline Buttons for Actions */
        button[kind="secondary"][key$="_reinit_btn"], button[kind="secondary"][key$="_exporter_btn"] { border-color: var(--accent) !important; color: var(--accent) !important; font-weight: 500 !important; background: transparent !important; }
        button[kind="secondary"][key$="_reinit_btn"]:hover, button[kind="secondary"][key$="_exporter_btn"]:hover { background: var(--accent-bg) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# SHARED CHROME: SIDEBAR + TOP BAR
# ============================================================

def render_sidebar(nav_items):
    with st.sidebar:
        with st.container():
            st.markdown(
                f"""
                <div class="brand-container">
                    <div class="brand-logo-text">HERMÈS<span class="brand-logo-sub">PARIS</div></span>
                    <div class="brand-word">Infocentre</div>
                </div>
                """, 
                unsafe_allow_html=True
            )

        for item in nav_items:
            st.page_link(item["page"], label=item["label"], icon=item["icon"])

        st.markdown('<div style="flex-grow: 1;"></div>', unsafe_allow_html=True)
        st.divider()

        with st.container():
            st.selectbox(
                "Language",
                ["🌐 Français", "🌐 English"],
                label_visibility="collapsed",
                key="lang_select"
            )
            st.markdown(
                f'<div class="logout-row">{ICON_LOGOUT}<span>Déconnexion</div>'</span>,
                unsafe_allow_html=True,
            )

def render_topbar(version_label, breadcrumb="Accueil"):
    st.markdown(
        f"""
        <div class="topbar-container">
            <div class="breadcrumb">{breadcrumb}</div>
            <div class="topbar-right">
                <span>{version_label}</span>
                <div class="avatar">NJ</div>
                {ICON_CHEVRON_DOWN}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_placeholder_page(title, version_label="Version Production 5.2.1"):
    render_topbar(version_label, breadcrumb=f"Accueil / {title}")
    st.markdown(f'<div class="page-title font-serif">{title}</div>', unsafe_allow_html=True)
    st.info("🚧 Cette section n'a pas encore été implémentée.")

# ============================================================
# SNOWFLAKE DATA
# ============================================================

@st.cache_data(ttl=300)
def load_articles():
    conn = st.connection("snowflake", type="snowflake")
    return conn.query("SELECT * FROM INFOCENTRE_DB.PUBLIC.ARTICLES", ttl=300)

@st.cache_data(ttl=300)
def load_mesures_produits():
    conn = st.connection("snowflake", type="snowflake")
    return conn.query("SELECT * FROM INFOCENTRE_DB.PUBLIC.MESURES_NOUVEAUX_PRODUITS", ttl=300)

@st.cache_data(ttl=300)
def load_commandes_detail():
    conn = st.connection("snowflake", type="snowflake")
    return conn.query("SELECT * FROM INFOCENTRE_DB.PUBLIC.COMMANDES_DETAIL", ttl=300)

# ============================================================
# EMAIL SENDING
# ============================================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "noahsamueljubain@gmail.com"

def send_email_with_attachment(to_email, subject, body, attachment_bytes=None, attachment_filename=None):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body or "", "plain"))

    if attachment_bytes is not None and attachment_filename:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{attachment_filename}"')
        msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SENDER_EMAIL, st.secrets["smtp_password"])
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())