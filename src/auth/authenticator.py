import streamlit as st
import hashlib
import hmac
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)


class Authenticator:
    """Gerenciador de autenticacao basica para o dashboard."""

    def __init__(self):
        self.logger: logging.Logger = logging.getLogger(__name__)

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _get_credentials(self) -> dict[str, str]:
        try:
            credentials = st.secrets.get("credentials", {})
            return dict(credentials)
        except Exception:
            self.logger.warning("Credenciais nao configuradas em secrets.toml")
            return {}

    def verify_credentials(self, username: str, password: str) -> bool:
        credentials = self._get_credentials()
        if not credentials:
            self.logger.warning("Nenhuma credencial configurada, acesso liberado")
            return True

        stored_hash = credentials.get(username)
        if stored_hash is None:
            self.logger.warning("Usuario nao encontrado: %s", username)
            return False

        password_hash = self._hash_password(password)
        is_valid = hmac.compare_digest(password_hash, stored_hash)

        if is_valid:
            self.logger.info("Login bem-sucedido: %s", username)
        else:
            self.logger.warning("Senha incorreta para: %s", username)

        return is_valid

    def render_login_form(self) -> Optional[str]:
        if st.session_state.get("authenticated"):
            return st.session_state.get("username")

        st.header("Acesso ao Dashboard")
        st.markdown("Informe suas credenciais para acessar o sistema.")

        with st.form("login_form"):
            username = st.text_input("Usuario", key="login_user")
            password = st.text_input("Senha", type="password", key="login_pass")
            submitted = st.form_submit_button("Entrar")

            if submitted:
                if self.verify_credentials(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error("Credenciais invalidas.")

        return None

    def require_auth(self) -> bool:
        credentials = self._get_credentials()
        if not credentials:
            return True
        return st.session_state.get("authenticated", False)

    def logout(self) -> None:
        username = st.session_state.get("username", "desconhecido")
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        self.logger.info("Logout realizado: %s", username)
        st.rerun()
