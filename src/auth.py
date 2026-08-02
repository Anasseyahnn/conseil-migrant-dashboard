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


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def check_login() -> bool:
    """Affiche un formulaire de connexion tant que la session n'est pas
    authentifiée. Renvoie True si l'accès est autorisé — l'appelant doit
    `st.stop()` immédiatement si False, pour ne rien afficher derrière."""
    if st.session_state.get("authenticated"):
        return True

    users: dict = st.secrets.get("auth", {}).get("users", {})

    st.title("🧭 Conseil Migrant")
    st.caption("Connexion requise — ce tableau de bord contient des données réelles.")

    if not users:
        st.error(
            "Aucun identifiant configuré côté secrets Streamlit Cloud "
            "([auth.users]) — accès bloqué par défaut, jamais ouvert par erreur."
        )
        return False

    with st.form("login_form"):
        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe", type="password")
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

    return False


def logout_button() -> None:
    username = st.session_state.get("username", "")
    if st.sidebar.button(f"↪ Déconnexion ({username})" if username else "↪ Déconnexion", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.pop("username", None)
        st.rerun()
