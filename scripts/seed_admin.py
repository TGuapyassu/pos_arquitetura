"""
Cria usuário administrador no banco. Uso (com tabelas já migradas):
  export DATABASE_URL=...
  export JWT_SECRET=...  (opcional para o script; já deve existir na app)
  python scripts/seed_admin.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("JWT_SECRET", "seed-local-somente-script")

if "DATABASE_URL" not in os.environ:
    print("Defina DATABASE_URL.")
    sys.exit(1)

from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.domain.entities import Usuario  # noqa: E402
from app.infrastructure.config import reset_settings_cache  # noqa: E402
from app.infrastructure.database.connection import (  # noqa: E402
    get_engine,
    reset_engine_and_session,
)
from app.infrastructure.database.models import Base  # noqa: E402
from app.infrastructure.repositories.sqlalchemy_usuario import (  # noqa: E402
    SqlAlchemyUsuarioRepository,
)
from app.infrastructure.security import hash_password  # noqa: E402


def main() -> None:
    reset_settings_cache()
    reset_engine_and_session()
    engine = get_engine()
    if "sqlite" in (os.environ.get("DATABASE_URL", "")):
        Base.metadata.create_all(engine)
    S = sessionmaker(
        engine, autocommit=False, autoflush=False, expire_on_commit=False, future=True
    )
    s = S()
    try:
        urep = SqlAlchemyUsuarioRepository(s)
        email = os.environ.get("ADMIN_EMAIL", "admin@oficina.local")
        if urep.get_by_email(email) is not None:
            print("Já existe usuário:", email)
            return
        a = Usuario(
            email=email,
            senha_hash=hash_password(os.environ.get("ADMIN_SENHA", "admin123")),
            is_admin=True,
            is_active=True,
        )
        urep.add(a)
        s.commit()
        print("Administrador criado:", email)
    finally:
        s.close()


if __name__ == "__main__":
    main()
