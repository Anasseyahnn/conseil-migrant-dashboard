"""Porte de connexion pour l'app publique.

L'app Streamlit Cloud est réglée en "public et searchable" (pas de contrôle
d'accès côté Streamlit Cloud) — ce module est donc la SEULE protection avant
d'afficher des données réelles (PII, population vulnérable). Identifiants
définis côté secrets Streamlit Cloud, jamais dans le repo :

    [auth.users]
    paulin = "<sha256 du mot de passe>"
    autreuser = "<sha256 du mot de passe>"

Générer un hash : python -c "import hashlib; print(hashlib.sha256(b'motdepasse').hexdigest())"
"""
from __future__ import annotations

import hashlib
import hmac

import streamlit as st

from . import palette as pal

# CSS scopée à la carte de connexion (clé "login_card" → classe .st-key-login_card,
# Streamlit >= 1.32). Reprend le langage visuel du reste de l'app (Fraunces en
# titrage, palette et rayons de src/palette.py / .streamlit/config.toml) au lieu
# du formulaire Streamlit nu par défaut — aucune nouvelle couleur introduite.
_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

@keyframes login-rise {{
    from {{ opacity: 0; transform: translateY(14px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@media (prefers-reduced-motion: reduce) {{
    @keyframes login-rise {{ from {{ opacity: 1; }} to {{ opacity: 1; }} }}
}}

.stApp {{
    background:
        radial-gradient(ellipse 900px 520px at 50% -10%, {pal.CATEGORICAL[0]}12, transparent 60%),
        radial-gradient(ellipse 700px 460px at 100% 100%, {pal.CATEGORICAL[6]}0f, transparent 55%),
        {pal.PAGE};
}}

.st-key-login_card {{
    max-width: 420px;
    margin: 6vh auto 0 auto;
    animation: login-rise 0.55s cubic-bezier(0.16, 1, 0.3, 1) both;
}}

.login-badge {{
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    border-radius: 16px;
    margin: 0 auto 18px auto;
    background: linear-gradient(160deg, {pal.CATEGORICAL[0]}, {pal.CATEGORICAL[6]});
    box-shadow: 0 8px 20px -8px {pal.CATEGORICAL[0]}70;
}}
.login-title {{
    font-family: {pal.DISPLAY_FONT};
    font-size: 1.7rem;
    font-weight: 600;
    color: {pal.INK_PRIMARY};
    text-align: center;
    letter-spacing: -0.01em;
    margin: 0;
}}
.login-sub {{
    text-align: center;
    color: {pal.INK_MUTED};
    font-size: 0.9rem;
    margin: 0.3rem 0 1.5rem 0;
}}
.login-trust {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: fit-content;
    margin: 0 auto 1.4rem auto;
    padding: 6px 14px;
    border-radius: 999px;
    background: {pal.SURFACE};
    border: 1px solid {pal.GRID};
    color: {pal.INK_SECONDARY};
    font-size: 0.78rem;
    font-weight: 600;
}}
.login-footnote {{
    text-align: center;
    color: {pal.INK_MUTED};
    font-size: 0.78rem;
    margin-top: 1rem;
}}

.st-key-login_card div[data-testid="stForm"] {{
    background: {pal.SURFACE};
    border: 1px solid {pal.GRID};
    border-radius: 18px;
    padding: 28px 26px 22px 26px;
    box-shadow: 0 1px 2px rgba(11,11,11,0.04), 0 20px 40px -24px rgba(11,11,11,0.28);
}}
.st-key-login_card div[data-testid="stTextInput"] label {{
    font-weight: 600;
    font-size: 0.82rem;
    color: {pal.INK_SECONDARY};
}}
.st-key-login_card div[data-testid="stTextInput"] input {{
    border-radius: 10px !important;
    border-color: {pal.GRID} !important;
    background: {pal.PAGE} !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}}
.st-key-login_card div[data-testid="stTextInput"] input::placeholder {{
    color: {pal.INK_SECONDARY};
}}
.st-key-login_card div[data-testid="stTextInput"]:focus-within input {{
    border-color: {pal.CATEGORICAL[0]} !important;
    box-shadow: 0 0 0 3px {pal.CATEGORICAL[0]}22 !important;
}}
.st-key-login_card div[data-testid="stFormSubmitButton"] button {{
    width: 100%;
    border-radius: 10px !important;
    border: none !important;
    background: {pal.CATEGORICAL[0]} !important;
    color: #fff !important;
    font-weight: 600 !important;
    padding: 0.55rem 0 !important;
    margin-top: 0.4rem;
    transition: filter 0.15s ease, transform 0.15s ease;
}}
.st-key-login_card div[data-testid="stFormSubmitButton"] button:hover {{
    filter: brightness(0.93);
    transform: translateY(-1px);
}}
.st-key-login_card div[data-testid="stFormSubmitButton"] button:active {{
    transform: translateY(0);
}}
.st-key-login_card div[data-testid="stAlert"] {{
    border-radius: 10px;
    margin-top: 0.9rem;
}}

@media (max-width: 480px) {{
    .st-key-login_card {{ max-width: 92vw; margin-top: 4vh; }}
    .st-key-login_card div[data-testid="stForm"] {{ padding: 22px 18px 18px 18px; }}
}}
</style>
"""


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def check_login() -> bool:
    """Affiche un formulaire de connexion tant que la session n'est pas
    authentifiée. Renvoie True si l'accès est autorisé — l'appelant doit
    `st.stop()` immédiatement si False, pour ne rien afficher derrière."""
    if st.session_state.get("authenticated"):
        return True

    st.markdown(_CSS, unsafe_allow_html=True)
    users: dict = st.secrets.get("auth", {}).get("users", {})

    with st.container(key="login_card"):
        st.markdown('<div class="login-badge">🧭</div>', unsafe_allow_html=True)
        st.markdown('<p class="login-title">Conseil Migrant</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="login-sub">Tableau de bord opérationnel</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="login-trust">🔒 Données réelles — accès protégé</div>',
            unsafe_allow_html=True,
        )

        if not users:
            st.error(
                "Aucun identifiant configuré côté secrets Streamlit Cloud "
                "([auth.users]) — accès bloqué par défaut, jamais ouvert par erreur."
            )
            return False

        with st.form("login_form"):
            username = st.text_input("Identifiant", placeholder="ex. yahanan")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Se connecter", use_container_width=True)

        if submitted:
            expected_hash = users.get(username)
            # hmac.compare_digest même si l'utilisateur n'existe pas (hash bidon)
            # pour ne pas laisser un timing différent révéler les identifiants valides.
            candidate_hash = _hash(password)
            valid = bool(expected_hash) and hmac.compare_digest(candidate_hash, expected_hash)
            if valid:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")

        st.markdown(
            '<p class="login-footnote">Vos données ne sont accessibles qu\'à l\'équipe autorisée.</p>',
            unsafe_allow_html=True,
        )

    return False


def logout_button() -> None:
    username = st.session_state.get("username", "")
    if st.sidebar.button(f"↪ Déconnexion ({username})" if username else "↪ Déconnexion", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.pop("username", None)
        st.rerun()
