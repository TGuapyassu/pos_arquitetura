from .base import Base
from .cliente import ClienteOrm
from .ordem_servico import OrdemServicoOrm, OrdemServicoPecaOrm, OrdemServicoServicoOrm
from .peca import PecaOrm
from .servico import ServicoOrm
from .usuario import UsuarioOrm
from .veiculo import VeiculoOrm

__all__ = [
    "Base",
    "ClienteOrm",
    "VeiculoOrm",
    "ServicoOrm",
    "PecaOrm",
    "OrdemServicoOrm",
    "OrdemServicoServicoOrm",
    "OrdemServicoPecaOrm",
    "UsuarioOrm",
]
