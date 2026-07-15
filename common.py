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
# Small inline SVGs (Lucide-style outline icons), no external
# icon-font dependency. Each accepts currentColor.
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
            --card: #F8F6F2;
            --line: #EAE5DC;
            --success: #1E8A5F;
        }

        /* ---------------- STREAMLIT CHROME RESET (FIXES TOP DEAD SPACE) ---------------- */
        #MainMenu, footer { visibility: hidden; height: 0; }
        div[data-testid="stDecoration"] { display: none; }
        div[data-testid="stToolbar"] { visibility: hidden; }
        
        /* Force clear hidden headers that take up blank vertical viewport room */
        header[data-testid="stHeader"] {
            display: none !important;
            height: 0px !important;
            min-height: 0px !important;
        }
        
        .stApp { background: #FFFFFF; padding-top: 0 !important; }
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--ink); }
        .font-serif { font-family: 'Fraunces', serif; }

        section.main {
            padding-top: 0 !important;
        }
        
        /* Strict adjustments to move top bars, layout titles, and metrics beautifully upward */
        section.main .block-container {
            max-width: 1320px;
            margin: 0 auto;
            padding: 1rem 3rem 4rem 3rem !important; /* Brought padding-top to 1rem to perfectly align main page with sidebar top */
        }

        /* ---------------- SIDEBAR POLISHING ---------------- */

        section[data-testid="stSidebar"] {
            background: var(--cream);
            border-right: 1px solid var(--line);
            min-width: 272px;
            max-width: 272px;
        }
        section[data-testid="stSidebar"] > div:first-child { 
            padding: 1.5rem 1.3rem !important; /* Snug top-padding grid alignment */
        }

        .brand-word {
            font-family: 'Fraunces', serif;
            font-size: 28px; font-weight: 600; color: var(--ink);
            line-height: 1.1; margin: 0px 0 2px 0;
        }
        .brand-sub {
            font-family: 'Inter', sans-serif;
            font-size: 11px; font-weight: 600; letter-spacing: 0.14em;
            color: var(--accent); margin-bottom: 22px;
        }

        /* Custom alignment for native st.page_link anchors */
        section[data-testid="stSidebar"] a[data-testid^="stPageLink"] {
            display: flex; align-items: center; gap: 10px;
            padding: 9px 12px !important; border-radius: 8px;
            font-size: 14.5px !important; font-weight: 500;
            color: #57534A !important;
            border-left: 3px solid transparent;
            margin-bottom: 2px;
        }
        section[data-testid="stSidebar"] a[data-testid^="stPageLink"]:hover {
            background: #F1EEE7;
        }
        section[data-testid="stSidebar"] a[data-testid^="stPageLink"][aria-current="page"] {
            color: var(--accent) !important;
            background: var(--accent-bg);
            border-left: 3px solid var(--accent);
        }

        .sidebar-divider { height: 1px; background: var(--line); margin: 18px 0; }

        .logout-row {
            display: flex; align-items: center; gap: 10px;
            color: #57534A; font-size: 14px; font-weight: 500; margin-top: 16px;
            font-family: 'Inter', sans-serif;
        }

        /* ---------------- MAIN TOP BAR ---------------- */

        .topbar {
            display: flex; align-items: center; justify-content: space-between;
            gap: 14px; color: var(--ink-soft); font-size: 13.5px; margin: 0 0 12px 0;
            padding-top: 0;
        }
        .topbar-right { display: flex; align-items: center; gap: 14px; }
        .breadcrumb { font-size: 13.5px; color: var(--ink-soft); }
        .breadcrumb .crumb-current { color: var(--ink); font-weight: 500; }
        .breadcrumb .crumb-sep { margin: 0 6px; color: #C9C4B8; }
        .avatar {
            width: 34px; height: 34px; border-radius: 50%;
            background: #EFECE6; color: var(--ink);
            display: flex; align-items: center; justify-content: center;
            font-size: 12.5px; font-weight: 600;
        }

        .page-title { 
            font-family: 'Fraunces', serif; 
            font-size: 38px; 
            font-weight: 600; 
            color: var(--ink); 
            margin: 0 0 4px 0; 
            line-height: 1.15;
        }
        .page-subtitle { color: var(--ink-soft); font-size: 15px; margin: 0 0 20px 0; }

        /* ---------------- KPI CARDS (accueil) ---------------- */

        .kpi-card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 22px 22px 20px 22px; height: 100%; }
        .kpi-icon { width: 42px; height: 42px; border-radius: 10px; background: #FFFFFF; border: 1px solid var(--line); display: flex; align-items: center; justify-content: center; color: var(--accent); margin-bottom: 14px; }
        .kpi-label { font-size: 13.5px; color: var(--ink-soft); margin-bottom: 6px; }
        .kpi-value { font-family: 'Fraunces', serif; font-size: 30px; font-weight: 600; color: var(--ink); margin-bottom: 8px; }
        .kpi-delta { display: flex; align-items: center; gap: 5px; font-size: 12.5px; color: var(--success); font-weight: 500; }

        /* ---------------- LIST PANELS (accueil) ---------------- */

        .panel { background: #FFFFFF; border: 1px solid var(--line); border-radius: 14px; padding: 22px 22px 12px 22px; height: 100%; }
        .panel-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
        .panel-title { font-family: 'Fraunces', serif; font-size: 19px; font-weight: 600; color: var(--ink); }
        .panel-link { display: flex; align-items: center; gap: 3px; color: var(--accent); font-size: 13px; font-weight: 600; }
        .panel-divider { height: 1px; background: var(--line); margin: 10px 0 2px 0; }
        .list-row { display: flex; align-items: center; gap: 12px; padding: 13px 2px; border-bottom: 1px solid var(--line); }
        .list-row:last-child { border-bottom: none; }
        .list-icon { width: 30px; height: 30px; border-radius: 7px; background: var(--card); border: 1px solid var(--line); display: flex; align-items: center; justify-content: center; color: #8A857B; flex-shrink: 0; }
        .list-icon.starred { color: var(--accent); background: var(--accent-bg); border-color: var(--accent-bg); }
        .list-title { font-size: 14.5px; font-weight: 500; color: var(--ink); }
        .list-category { font-size: 12.5px; color: var(--ink-soft); margin-top: 1px; }
        .list-meta { margin-left: auto; font-size: 12.5px; color: var(--ink-soft); white-space: nowrap; }
        .list-kebab { margin-left: auto; color: #B4AFA6; }
        .panel-footer { display: flex; align-items: center; gap: 4px; color: var(--accent); font-size: 13.5px; font-weight: 600; padding: 14px 2px 4px 2px; }

        /* ---------------- LISTE DES RAPPORTS ---------------- */

        .repertoire-panel { background: #FFFFFF; border: 1px solid var(--line); border-radius: 14px; padding: 18px 16px; }
        .repertoire-title { font-family: 'Fraunces', serif; font-size: 17px; font-weight: 600; margin-bottom: 12px; }
        .tree-item { display: flex; align-items: center; gap: 7px; padding: 6px 4px; font-size: 13.5px; color: #4A4640; border-radius: 6px; }
        .tree-item:hover { background: #F5F2EC; }
        .tree-item.tree-active { color: var(--accent); font-weight: 600; }
        .tree-item.tree-parent-active { color: var(--accent); font-weight: 600; }
        .tree-item .tree-chevron { color: #B4AFA6; flex-shrink: 0; }
        .tree-item .tree-icon { color: #C9A227; flex-shrink: 0; }
        .tree-item.tree-active .tree-icon, .tree-item.tree-parent-active .tree-icon { color: var(--accent); }
        .tree-indent-1 { padding-left: 22px; }
        .tree-footer { display: flex; align-items: center; gap: 8px; color: #57534A; font-size: 13px; font-weight: 500; padding: 12px 4px 2px 4px; margin-top: 8px; border-top: 1px solid var(--line); }

        .rl-count { font-family: 'Fraunces', serif; font-size: 17px; font-weight: 600; color: var(--ink); }

        .rl-table-header {
            display: grid;
            grid-template-columns: minmax(260px,3fr) 90px minmax(220px,2fr) 34px 26px;
            gap: 10px; padding: 0 4px 10px 4px; border-bottom: 1px solid var(--line);
            font-size: 12.5px; font-weight: 600; color: var(--ink-soft);
        }
        .rl-row {
            display: grid;
            grid-template-columns: minmax(260px,3fr) 90px minmax(220px,2fr) 34px 26px;
            gap: 10px; padding: 14px 4px; border-bottom: 1px solid var(--line);
            align-items: center; min-height: 62px;
        }
        .rl-row:last-child { border-bottom: none; }
        .rl-report-cell { display: flex; align-items: flex-start; gap: 11px; }
        .rl-report-icon { width: 30px; height: 30px; border-radius: 7px; background: var(--card); border: 1px solid var(--line); display: flex; align-items: center; justify-content: center; color: #8A857B; flex-shrink: 0; margin-top: 1px; }
        .rl-report-title { font-size: 14.5px; font-weight: 600; color: var(--ink); }
        .rl-report-desc { font-size: 12.5px; color: var(--ink-soft); margin-top: 1px; }
        .rl-cell { font-size: 13.5px; color: #4A4640; }
        .rl-star { color: #C9C4B8; }
        .rl-star.filled { color: var(--accent); }
        .rl-kebab { color: #B4AFA6; }

        .rl-title-link {
            font-size: 14.5px; font-weight: 600; color: var(--ink);
        }

        [class*="st-key-open_"][class*="_title_btn"] button {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            height: auto !important;
            min-height: 0 !important;
            text-align: left !important;
            justify-content: flex-start !important;
        }
        [class*="st-key-open_"][class*="_title_btn"] button p {
            font-size: 14.5px !important;
            font-weight: 600 !important;
            color: var(--ink) !important;
        }
        [class*="st-key-open_"][class*="_title_btn"] button:hover p {
            color: var(--accent) !important;
            text-decoration: underline !important;
        }
        [class*="st-key-open_"][class*="_title_btn"] { margin-bottom: 0 !important; }

        .rl-th { font-size: 12.5px; font-weight: 600; color: var(--ink-soft); padding-bottom: 8px; }
        .rl-row-hr { border: none; border-top: 1px solid var(--line); margin: 4px 0 10px 0; }

        /* ---------------- REPORT CARDS (grid view of "Liste des rapports") ---------------- */

        .report-card {
            background: #FFFFFF; border: 1px solid var(--line); border-radius: 14px;
            padding: 18px 20px 16px 20px; height: 100%;
        }
        .report-card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
        .report-badge {
            display: inline-flex; align-items: center; gap: 5px;
            background: var(--accent-bg); color: var(--accent);
            font-size: 12px; font-weight: 600; padding: 4px 10px 4px 8px; border-radius: 20px;
        }
        .report-badge svg { width: 12px; height: 12px; }
        .report-card-kebab { color: #B4AFA6; }
        .report-card-number { font-size: 13px; color: var(--ink-soft); margin: 2px 0 10px 0; }
        .report-card-folder-row { display: flex; align-items: center; justify-content: space-between; margin-top: 6px; }
        .report-card-folder { font-size: 12.5px; color: var(--ink-soft); }
        .report-card-date { font-size: 12.5px; color: var(--ink-soft); }

        /* ---------------- TAB BAR (multi-tab manager on "Liste des rapports") ---------------- */

        .tab-bar-wrap { border-bottom: 1px solid var(--line); margin-bottom: 14px; }

        [class*="st-key-tab_"] button {
            background: transparent !important;
            border: none !important;
            border-bottom: 2px solid transparent !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            color: var(--ink-soft) !important;
            font-weight: 500 !important;
            padding: 10px 4px !important;
        }
        [class*="st-key-tab_"] button:hover { color: var(--ink) !important; }
        [class*="st-key-tab_"] button[kind="primary"] {
            color: var(--accent) !important;
            border-bottom: 2px solid var(--accent) !important;
            font-weight: 600 !important;
        }
        [class*="st-key-tab_"][class*="_close_btn"] button {
            color: #B4AFA6 !important;
            font-weight: 400 !important;
            border-bottom: none !important;
            text-align: center !important;
        }

        /* ---------------- DATA TABLE WRAPPER (report views) ---------------- */

        div[data-testid="stDataFrameResizable"] {
            border: 1px solid var(--line) !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }

        .pill-btn {
            display: inline-flex; align-items: center; justify-content: center;
            padding: 6px 12px; border-radius: 7px; font-size: 13px; font-weight: 600;
            border: 1px solid var(--line); color: var(--ink); background: #FFFFFF;
        }
        .pill-btn.active { border-color: var(--accent); color: var(--accent); background: var(--accent-bg); }

        .pagination-row { display: flex; align-items: center; gap: 6px; }
        .page-pill {
            display: inline-flex; align-items: center; justify-content: center;
            width: 30px; height: 30px; border-radius: 7px; font-size: 13px; font-weight: 600;
            border: 1px solid transparent; color: var(--ink-soft);
        }
        .page-pill.current { border-color: var(--accent); color: var(--accent); }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# SHARED CHROME: SIDEBAR + TOP BAR
# ============================================================

def render_sidebar(nav_items):
    """nav_items: list of dicts {"page": st.Page, "label": str, "icon": str}"""
    with st.sidebar:
        # Group Branding tightly at the top container
        with st.container():
            try:
                st.image("image.png", width=170)
            except Exception:
                st.markdown('<div class="brand-word">Infocentre</div>', unsafe_allow_html=True)

            st.markdown('<div class="brand-sub">HERMÈS PARIS</div>', unsafe_allow_html=True)

        # Render Premium Navigation Links
        for item in nav_items:
            st.page_link(item["page"], label=item["label"], icon=item["icon"])

        # Soft, clean visual layout separator
        st.divider()

        # Group Language Selector and Logout action cleanly at bottom
        with st.container():
            st.selectbox(
                "Langue",
                ["🌐 Français", "🌐 English"],
                label_visibility="collapsed",
                key="lang_select"
            )

            st.markdown(
                f'<div class="logout-row">{ICON_LOGOUT}<span>Déconnexion</span></div>',
                unsafe_allow_html=True,
            )


def render_topbar(version_label, breadcrumb=None):
    """Renders the shared top bar. `breadcrumb`, if given, is the label
    of the current page and is shown as 'Accueil / {breadcrumb}' on the
    left; pages that don't pass it keep the previous right-only layout."""
    if breadcrumb:
        left_html = (
            f'<div class="breadcrumb">'
            f'<span>Accueil</span><span class="crumb-sep">/</span>'
            f'<span class="crumb-current">{breadcrumb}</span>'
            f'</div>'
        )
    else:
        left_html = '<div></div>'

    st.markdown(
        f"""
        <div class="topbar">
            {left_html}
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
    """Generic stub for sidebar sections that don't have a real page yet."""
    render_topbar(version_label)
    st.markdown(f'<div class="page-title font-serif">{title}</div>', unsafe_allow_html=True)
    st.info("🚧 Cette section n'a pas encore été implémentée.")

# ============================================================
# SNOWFLAKE DATA (shared by pages that need the TABLES)
# ============================================================

@st.cache_data(ttl=300)
def load_articles():
    conn = st.connection("snowflake", type="snowflake")
    data = conn.query(
        """
        SELECT *
        FROM INFOCENTRE_DB.PUBLIC.ARTICLES
        """,
        ttl=300
    )
    return data


@st.cache_data(ttl=300)
def load_mesures_produits():
    conn = st.connection("snowflake", type="snowflake")
    data = conn.query(
        """
        SELECT *
        FROM INFOCENTRE_DB.PUBLIC.MESURES_NOUVEAUX_PRODUITS
        """,
        ttl=300
    )
    return data


@st.cache_data(ttl=300)
def load_commandes_detail():
    conn = st.connection("snowflake", type="snowflake")
    data = conn.query(
        """
        SELECT *
        FROM INFOCENTRE_DB.PUBLIC.COMMANDES_DETAIL
        """,
        ttl=300
    )
    return data

# ============================================================
# EMAIL SENDING (Gmail SMTP)
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