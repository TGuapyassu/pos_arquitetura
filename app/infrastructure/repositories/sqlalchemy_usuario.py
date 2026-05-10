from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Usuario
from app.infrastructure.database.models import UsuarioOrm
from app.infrastructure.mappers.entity_mappers import usuario_orm_to_domain


class SqlAlchemyUsuarioRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, u: Usuario) -> Usuario:
        m = UsuarioOrm(
            email=u.email,
            senha_hash=u.senha_hash,
            is_admin=u.is_admin,
            is_active=u.is_active,
        )
        self._s.add(m)
        self._s.flush()
        self._s.refresh(m)
        u.id = m.id
        u.created_at = m.created_at
        return u

    def get_by_id(self, id: int) -> Optional[Usuario]:
        m = self._s.get(UsuarioOrm, id)
        return None if m is None else usuario_orm_to_domain(m)

    def get_by_email(self, email: str) -> Optional[Usuario]:
        st = self._s.execute(
            select(UsuarioOrm).where(UsuarioOrm.email == email)
        )
        m = st.scalars().first()
        return None if m is None else usuario_orm_to_domain(m)
