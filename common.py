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

# Add these rules inside the <style> block of your inject_global_css() function in common.py

'''
/* --- DASHBOARD HERO & KPIS --- */
.hero-section {
    background: linear-gradient(180deg, #EBE4D8 0%, #FAF8F4 100%);
    padding: 40px;
    border-radius: 16px;
    margin-bottom: 30px;
}
.hero-title { font-family: 'Fraunces', serif; font-size: 36px; font-weight: 600; color: #4A453E; margin-bottom: 8px; }
.hero-subtitle { font-size: 16px; color: #6E6A63; margin-bottom: 30px; }

.kpi-container { display: flex; gap: 20px; }
.kpi-card-modern {
    background: #FFFFFF;
    border: 1px solid #EAE5DC;
    border-radius: 16px;
    padding: 24px;
    flex: 1;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}
.kpi-title-modern { font-size: 14px; color: #6E6A63; font-weight: 500; margin-bottom: 12px; }
.kpi-value-modern { font-family: 'Inter', sans-serif; font-size: 42px; font-weight: 600; color: #1C1B19; line-height: 1; }
.kpi-delta-modern { font-size: 13px; font-weight: 500; margin-top: 10px; }
.delta-pos { color: #1E8A5F; }
.delta-neg { color: #D9642A; }

/* --- REPORT CARDS (GRID VIEW) --- */
.report-card {
    background: #FFFFFF;
    border: 1px solid #EAE5DC;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.01);
    transition: box-shadow 0.2s;
}
.report-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); cursor: pointer; }
.rc-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.rc-tag { background: #FBEAE0; color: #D9642A; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; }
.rc-title { font-size: 15px; font-weight: 600; color: #1C1B19; margin-bottom: 4px; line-height: 1.3; }
.rc-id { font-size: 13px; color: #6E6A63; margin-bottom: 16px; }
.rc-footer { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #8A857B; }

/* --- BUTTONS --- */
.btn-outline {
    border: 1px solid #D9642A;
    color: #D9642A;
    background: transparent;
    padding: 8px 24px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
.btn-solid {
    border: 1px solid #D9642A;
    background: #D9642A;
    color: white;
    padding: 8px 24px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
'''

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


def render_topbar(version_label):
    st.markdown(
        f"""
        <div class="topbar">
            <span>{version_label}</span>
            <div class="avatar">NJ</div>
            {ICON_CHEVRON_DOWN}
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