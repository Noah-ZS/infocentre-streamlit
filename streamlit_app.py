import streamlit as st
from common import render_topbar, ICON_STAR, ICON_DOC, ICON_KEBAB

render_topbar("Version Production 5.2.1")

st.markdown("""
<div class="hero-section">
    <div class="hero-title">Bienvenue sur votre Infocentre</div>
    <div class="hero-subtitle">Votre portail de Business Intelligence dédié à la performance.</div>
    
    <div class="kpi-container">
        <div class="kpi-card-modern">
            <div class="kpi-title-modern">Rapports générés ce mois</div>
            <div class="kpi-value-modern">142</div>
            <div class="kpi-delta-modern delta-pos">+12% vs mois précédent</div>
        </div>
        <div class="kpi-card-modern">
            <div class="kpi-title-modern">Temps moyen d'exécution</div>
            <div class="kpi-value-modern">1.8 s</div>
            <div class="kpi-delta-modern delta-pos" style="color: #6E6A63;">-0.4 s vs mois précédent</div>
        </div>
        <div class="kpi-card-modern">
            <div class="kpi-title-modern">Rapports favoris</div>
            <div class="kpi-value-modern">18</div>
            <div class="kpi-delta-modern delta-pos">+3 vs mois précédent</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="panel-title" style="margin-bottom:15px;">Rapports récents <span style="float:right; font-size:13px; color:#6E6A63; cursor:pointer;">Voir tout</span></div>', unsafe_allow_html=True)
    # Loop to generate recent report lists
    for _ in range(4):
        st.markdown(f"""
        <div class="list-row" style="background: #F8F6F2; border-radius: 12px; margin-bottom: 10px; padding: 15px;">
            <div class="list-icon">{ICON_DOC}</div>
            <div>
                <div class="list-title">Commandes - Détail</div>
                <div class="list-category">Gestion Commerciale</div>
            </div>
            <div class="list-meta">Il y a 2 h</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="panel-title" style="margin-bottom:15px;">Vos favoris <span style="float:right; font-size:13px; color:#6E6A63; cursor:pointer;">Voir tout</span></div>', unsafe_allow_html=True)
    # Loop to generate favorite cards (2x2 grid approach)
    fav_cols = st.columns(2)
    for i in range(4):
        with fav_cols[i%2]:
            st.markdown(f"""
            <div class="report-card" style="padding: 15px; margin-bottom:10px;">
                <div class="rc-header" style="margin-bottom:8px;">
                    <div style="color:#D9642A;">{ICON_STAR}</div>
                    <div class="rl-kebab">{ICON_KEBAB}</div>
                </div>
                <div class="rc-title" style="font-size:14px;">Commande - Détail</div>
                <div class="rc-id" style="margin-bottom:0;">Département</div>
            </div>
            """, unsafe_allow_html=True)