"""Exceções de regra de negócio (domínio e aplicação)."""


class DomainError(Exception):
    """Base para erros de regra de negócio."""


class EstoqueInsuficienteError(DomainError):
    def __init__(self, peca_id: int, solicitado: int, disponivel: int) -> None:
        self.peca_id = peca_id
        self.solicitado = solicitado
        self.disponivel = disponivel
        super().__init__(
            f"Estoque insuficiente para a peça {peca_id}: "
            f"solicitado {solicitado}, disponível {disponivel}."
        )


class TransicaoStatusInvalidaError(DomainError):
    pass


class AprovacaoNecessariaError(DomainError):
    pass


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class AutenticacaoError(DomainError):
    pass
