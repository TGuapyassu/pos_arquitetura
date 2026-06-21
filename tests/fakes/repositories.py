from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import List, Optional

from app.domain.entities import (
    Cliente,
    OrdemServico,
    Peca,
    ServicoOficina,
    Usuario,
    Veiculo,
)
from app.domain.enums import OrdemServicoStatus
from app.domain.exceptions import NotFoundError
from app.domain.services.ordem_servico_listagem import eh_status_ativo


class _IdSequence:
    def __init__(self, start: int = 1) -> None:
        self._next = start

    def next(self) -> int:
        n = self._next
        self._next += 1
        return n


class FakeClienteRepository:
    def __init__(self) -> None:
        self._store: dict[int, Cliente] = {}
        self._ids = _IdSequence()

    def add(self, c: Cliente) -> Cliente:
        stored = copy.deepcopy(c)
        stored.id = self._ids.next()
        self._store[stored.id] = stored
        c.id = stored.id
        return copy.deepcopy(stored)

    def update(self, c: Cliente) -> Cliente:
        if c.id is None:
            raise ValueError("id obrigatório")
        self._store[c.id] = copy.deepcopy(c)
        return copy.deepcopy(c)

    def get_by_id(self, id: int) -> Optional[Cliente]:
        c = self._store.get(id)
        return copy.deepcopy(c) if c else None

    def listar(self) -> List[Cliente]:
        return [copy.deepcopy(c) for c in self._store.values()]

    def delete(self, id: int) -> None:
        if id not in self._store:
            raise NotFoundError("Cliente não encontrado.")
        del self._store[id]


class FakeVeiculoRepository:
    def __init__(self) -> None:
        self._store: dict[int, Veiculo] = {}
        self._ids = _IdSequence()

    def add(self, v: Veiculo) -> Veiculo:
        stored = copy.deepcopy(v)
        stored.id = self._ids.next()
        self._store[stored.id] = stored
        v.id = stored.id
        return copy.deepcopy(stored)

    def update(self, v: Veiculo) -> Veiculo:
        if v.id is None:
            raise ValueError("id obrigatório")
        self._store[v.id] = copy.deepcopy(v)
        return copy.deepcopy(v)

    def get_by_id(self, id: int) -> Optional[Veiculo]:
        v = self._store.get(id)
        return copy.deepcopy(v) if v else None

    def listar_por_cliente(self, cliente_id: int) -> List[Veiculo]:
        return [
            copy.deepcopy(v)
            for v in self._store.values()
            if v.cliente_id == cliente_id
        ]

    def listar(self) -> List[Veiculo]:
        return [copy.deepcopy(v) for v in self._store.values()]

    def delete(self, id: int) -> None:
        if id not in self._store:
            raise NotFoundError("Veículo não encontrado.")
        del self._store[id]


class FakeServicoOficinaRepository:
    def __init__(self) -> None:
        self._store: dict[int, ServicoOficina] = {}
        self._ids = _IdSequence()

    def add(self, s: ServicoOficina) -> ServicoOficina:
        stored = copy.deepcopy(s)
        stored.id = self._ids.next()
        self._store[stored.id] = stored
        s.id = stored.id
        return copy.deepcopy(stored)

    def update(self, s: ServicoOficina) -> ServicoOficina:
        if s.id is None:
            raise ValueError("id obrigatório")
        self._store[s.id] = copy.deepcopy(s)
        return copy.deepcopy(s)

    def get_by_id(self, id: int) -> Optional[ServicoOficina]:
        s = self._store.get(id)
        return copy.deepcopy(s) if s else None

    def listar(self) -> List[ServicoOficina]:
        return [copy.deepcopy(s) for s in self._store.values()]

    def delete(self, id: int) -> None:
        if id not in self._store:
            raise NotFoundError("Serviço não encontrado.")
        del self._store[id]


class FakePecaRepository:
    def __init__(self) -> None:
        self._store: dict[int, Peca] = {}
        self._ids = _IdSequence()

    def add(self, p: Peca) -> Peca:
        stored = copy.deepcopy(p)
        stored.id = self._ids.next()
        self._store[stored.id] = stored
        p.id = stored.id
        return copy.deepcopy(stored)

    def update(self, p: Peca) -> Peca:
        if p.id is None:
            raise ValueError("id obrigatório")
        self._store[p.id] = copy.deepcopy(p)
        return copy.deepcopy(p)

    def get_by_id(self, id: int) -> Optional[Peca]:
        p = self._store.get(id)
        return copy.deepcopy(p) if p else None

    def listar(self) -> List[Peca]:
        return [copy.deepcopy(p) for p in self._store.values()]

    def listar_por_ids(self, ids: List[int]) -> List[Peca]:
        return [copy.deepcopy(self._store[i]) for i in ids if i in self._store]

    def delete(self, id: int) -> None:
        if id not in self._store:
            raise NotFoundError("Peça não encontrada.")
        del self._store[id]


class FakeOrdemServicoRepository:
    def __init__(self) -> None:
        self._store: dict[int, OrdemServico] = {}
        self._ids = _IdSequence()

    def add(self, o: OrdemServico) -> OrdemServico:
        stored = copy.deepcopy(o)
        stored.id = self._ids.next()
        self._store[stored.id] = stored
        o.id = stored.id
        return copy.deepcopy(stored)

    def update(self, o: OrdemServico) -> OrdemServico:
        if o.id is None:
            raise ValueError("id obrigatório")
        self._store[o.id] = copy.deepcopy(o)
        return copy.deepcopy(o)

    def get_by_id(self, id: int) -> Optional[OrdemServico]:
        o = self._store.get(id)
        return copy.deepcopy(o) if o else None

    def listar(self) -> List[OrdemServico]:
        return sorted(
            [copy.deepcopy(o) for o in self._store.values()],
            key=lambda x: x.id or 0,
            reverse=True,
        )

    def listar_ativas(self) -> List[OrdemServico]:
        return [
            copy.deepcopy(o)
            for o in self._store.values()
            if eh_status_ativo(o.status)
        ]


class FakeUsuarioRepository:
    def __init__(self) -> None:
        self._store: dict[int, Usuario] = {}
        self._by_email: dict[str, Usuario] = {}
        self._ids = _IdSequence()

    def add(self, u: Usuario) -> Usuario:
        stored = copy.deepcopy(u)
        stored.id = self._ids.next()
        self._store[stored.id] = stored
        self._by_email[stored.email] = stored
        u.id = stored.id
        return copy.deepcopy(stored)

    def get_by_id(self, id: int) -> Optional[Usuario]:
        u = self._store.get(id)
        return copy.deepcopy(u) if u else None

    def get_by_email(self, email: str) -> Optional[Usuario]:
        u = self._by_email.get(email)
        return copy.deepcopy(u) if u else None


@dataclass
class FakeRepositories:
    clientes: FakeClienteRepository
    veiculos: FakeVeiculoRepository
    servicos: FakeServicoOficinaRepository
    pecas: FakePecaRepository
    ordens: FakeOrdemServicoRepository
    usuarios: FakeUsuarioRepository

    @classmethod
    def vazio(cls) -> FakeRepositories:
        return cls(
            clientes=FakeClienteRepository(),
            veiculos=FakeVeiculoRepository(),
            servicos=FakeServicoOficinaRepository(),
            pecas=FakePecaRepository(),
            ordens=FakeOrdemServicoRepository(),
            usuarios=FakeUsuarioRepository(),
        )
