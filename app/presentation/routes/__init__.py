from app.presentation.routes.auth import router as auth_router
from app.presentation.routes.clientes import router as clientes_router
from app.presentation.routes.health import router as health_router
from app.presentation.routes.integrations import router as integrations_router
from app.presentation.routes.ordem import router as ordem_router
from app.presentation.routes.pecas import router as pecas_router
from app.presentation.routes.public import router as public_router
from app.presentation.routes.servicos import router as servicos_router
from app.presentation.routes.veiculos import router as veiculos_router

all_routers = [
    health_router,
    auth_router,
    public_router,
    integrations_router,
    ordem_router,
    clientes_router,
    veiculos_router,
    servicos_router,
    pecas_router,
]

__all__ = ["all_routers"]
