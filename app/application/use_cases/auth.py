from __future__ import annotations

from sqlalchemy.orm import Session

from app.application.dtos import LoginIn, TokenOut
from app.domain.exceptions import AutenticacaoError
from app.infrastructure.repositories.sqlalchemy_usuario import SqlAlchemyUsuarioRepository
from app.infrastructure.security import create_token, verify_password


def login(s: Session, body: LoginIn) -> TokenOut:
    u = SqlAlchemyUsuarioRepository(s).get_by_email(body.email)
    if u is None or not u.is_active or not verify_password(body.senha, u.senha_hash):
        raise AutenticacaoError("Credenciais inválidas.")
    if u.id is None:
        raise AutenticacaoError("Usuário inválido.")
    token = create_token(user_id=u.id, email=u.email, is_admin=u.is_admin)
    return TokenOut(access_token=token, token_type="bearer")
