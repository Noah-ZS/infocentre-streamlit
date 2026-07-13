"""
Shared building blocks for the Infocentre multi-page app...
"""

import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st

# ============================================================
# ICONS  (unchanged)
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

        #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
        .stApp { background: #FFFFFF; }
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--ink); }
        .font-serif { font-family: 'Fraunces', serif; }

        section.main .block-container {
            max-width: 1320px;
            margin: 0 auto;
            padding: 2.0rem 3rem 4rem 3rem;
        }

        /* ---------------- SIDEBAR ---------------- */

        section[data-testid="stSidebar"] {
            background: var(--cream);
            border-right: 1px solid var(--line);
            min-width: 272px;
            max-width: 272px;
        }
        section[data-testid="stSidebar"] > div { padding: 1.6rem 1.3rem; }

        .brand-word {
            font-family: 'Fraunces', serif;
            font-size: 28px; font-weight: 600; color: var(--ink);
            line-height: 1.1; margin: 4px 0 2px 0;
        }
        .brand-sub {
            font-size: 11px; font-weight: 600; letter-spacing: 0.14em;
            color: var(--accent); margin-bottom: 22px;
        }

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
        }

        /* ---- Dynamic in-app tabs, inserted under a sidebar nav item ---- */
        [class*="st-key-dyntab_"] {
            margin-left: 14px;
            margin-bottom: 2px;
        }
        [class*="st-key-dyntab_"] .stButton button {
            justify-content: flex-start !important;
            text-align: left !important;
            padding: 7px 10px !important;
            border-radius: 8px !important;
            font-size: 13.5px !important;
            font-weight: 500 !important;
        }
        [class*="st-key-dynclose_"] .stButton button {
            padding: 4px 8px !important;
            min-height: unset !important;
            border: none !important;
            background: transparent !important;
            color: #A39D91 !important;
            font-size: 12px !important;
        }
        [class*="st-key-dynclose_"] .stButton button:hover {
            color: var(--accent) !important;
            background: #F1EEE7 !important;
        }

        /* ---------------- MAIN TOP BAR ---------------- */

        .topbar {
            display: flex; align-items: center; justify-content: flex-end;
            gap: 14px; color: var(--ink-soft); font-size: 13.5px; margin-bottom: 26px;
        }
        .avatar {
            width: 34px; height: 34px; border-radius: 50%;
            background: #EFECE6; color: var(--ink);
            display: flex; align-items: center; justify-content: center;
            font-size: 12.5px; font-weight: 600;
        }

        .page-title { font-family: 'Fraunces', serif; font-size: 38px; font-weight: 600; color: var(--ink); margin-bottom: 6px; }
        .page-subtitle { color: var(--ink-soft); font-size: 15px; margin-bottom: 30px; }

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

        .lr-search-btn button {
            background: var(--accent) !important; color: white !important;
            border: none !important; font-weight: 600 !important;
        }
        .lr-search-btn button:hover { background: #C15720 !important; }

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

        /* Trimmed to 5 columns: Rapport / Numéro / Dossier / star / kebab
           (propriétaire, dernière modif., utilisations removed) */
        .rl-table-header {
            display: grid;
            grid-template-columns: minmax(280px,4fr) 90px minmax(200px,2.2fr) 34px 26px;
            gap: 10px; padding: 0 4px 10px 4px; border-bottom: 1px solid var(--line);
            font-size: 12.5px; font-weight: 600; color: var(--ink-soft);
        }
        .rl-row {
            display: grid;
            grid-template-columns: minmax(280px,4fr) 90px minmax(200px,2.2fr) 34px 26px;
            gap: 10px; padding: 14px 4px; border-bottom: 1px solid var(--line);
            align-items: center;
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

        /* Overlay click target for the "open as in-app tab" row.
/* Row-as-button: title cell for the clickable "open as tab" row */
        [class*="st-key-row_"] {
            border-bottom: 1px solid var(--line);
            padding: 10px 4px;
        }
        [class*="st-key-row_"] .stButton button {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            min-height: unset !important;
            text-align: left !important;
            justify-content: flex-start !important;
            font-size: 14.5px !important;
            font-weight: 600 !important;
            color: var(--ink) !important;
        }
        [class*="st-key-row_"] .stButton button:hover {
            color: var(--accent) !important;
            text-decoration: underline;
        }
        .rl-report-desc-inline { font-size: 12.5px; color: var(--ink-soft); margin-top: 1px; }
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

def render_sidebar(nav_items, dynamic_tabs_after="Liste des rapports"):
    """nav_items: list of dicts {"page": st.Page, "label": str, "icon": str}

    Any tabs in st.session_state.dynamic_tabs are rendered directly under
    the nav item whose label matches `dynamic_tabs_after`, each with a
    close (✕) button. Pages open/close tabs by writing to
    st.session_state.dynamic_tabs / active_dynamic_tab — this function
    only renders whatever state currently holds.
    """
    dynamic_tabs = st.session_state.get("dynamic_tabs", [])
    active_tab_key = st.session_state.get("active_dynamic_tab")

    with st.sidebar:
        try:
            st.image("image.png", width=170)
        except Exception:
            st.markdown('<div class="brand-word">Infocentre</div>', unsafe_allow_html=True)

        st.markdown('<div class="brand-sub">HERMÈS PARIS</div>', unsafe_allow_html=True)

        for item in nav_items:
            st.page_link(item["page"], label=item["label"], icon=item["icon"])

            if item["label"] == dynamic_tabs_after and dynamic_tabs:
                for tab in dynamic_tabs:
                    is_active = tab["key"] == active_tab_key
                    with st.container(key=f"dyntab_{tab['key']}"):
                        label_col, close_col = st.columns([5, 1], gap="small")
                        with label_col:
                            if st.button(
                                tab["label"],
                                key=f"dyntab_btn_{tab['key']}",
                                use_container_width=True,
                                type="primary" if is_active else "secondary",
                            ):
                                st.session_state.active_dynamic_tab = tab["key"]
                                st.switch_page(tab["target_page"])
                        with close_col:
                            with st.container(key=f"dynclose_{tab['key']}"):
                                if st.button("✕", key=f"dyntab_close_{tab['key']}"):
                                    st.session_state.dynamic_tabs = [
                                        t for t in dynamic_tabs if t["key"] != tab["key"]
                                    ]
                                    if st.session_state.get("active_dynamic_tab") == tab["key"]:
                                        st.session_state.active_dynamic_tab = None
                                    st.rerun()

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

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


def render_topbar(version_label):
    st.markdown(
        f"""
        <div class="topbar">
            <span>{version_label}</span>
            <div class="avatar">MM</div>
            {ICON_CHEVRON_DOWN}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder_page(title, version_label="Version Production 5.2.1"):
    render_topbar(version_label)
    st.markdown(f'<div class="page-title font-serif">{title}</div>', unsafe_allow_html=True)
    st.info("🚧 Cette section n'a pas encore été implémentée.")

# ============================================================
# SNOWFLAKE DATA  (unchanged)
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

# ============================================================
# EMAIL SENDING  (unchanged)
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