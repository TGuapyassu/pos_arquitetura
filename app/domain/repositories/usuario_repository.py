from __future__ import annotations

from typing import Optional, Protocol

from app.domain.entities import Usuario


class IUsuarioRepository(Protocol):
    def add(self, u: Usuario) -> Usuario: ...
    def get_by_id(self, id: int) -> Optional[Usuario]: ...
    def get_by_email(self, email: str) -> Optional[Usuario]: ...
