from __future__ import annotations

from app.application.dtos import LoginIn, TokenOut
from app.application.ports import IAuthGateway
from app.domain.exceptions import AutenticacaoError
from app.domain.repositories import IUsuarioRepository


class LoginUseCase:
    def __init__(
        self,
        usuarios: IUsuarioRepository,
        auth: IAuthGateway,
    ) -> None:
        self._usuarios = usuarios
        self._auth = auth

    def execute(self, body: LoginIn) -> TokenOut:
        u = self._usuarios.get_by_email(body.email)
        if u is None or not u.is_active or not self._auth.verify_password(body.senha, u.senha_hash):
            raise AutenticacaoError("Credenciais inválidas.")
        if u.id is None:
            raise AutenticacaoError("Usuário inválido.")
        token = self._auth.create_token(user_id=u.id, email=u.email, is_admin=u.is_admin)
        return TokenOut(access_token=token, token_type="bearer")
