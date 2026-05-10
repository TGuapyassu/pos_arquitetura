from .cliente_repository import IClienteRepository
from .peca_repository import IPecaRepository
from .ordem_servico_repository import IOrdemServicoRepository
from .servico_repository import IServicoOficinaRepository
from .usuario_repository import IUsuarioRepository
from .veiculo_repository import IVeiculoRepository

__all__ = [
    "IClienteRepository",
    "IPecaRepository",
    "IOrdemServicoRepository",
    "IServicoOficinaRepository",
    "IUsuarioRepository",
    "IVeiculoRepository",
]
