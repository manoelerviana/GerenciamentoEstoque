from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

@dataclass
class LocalEstoque:
    id: str
    nome: str
    corredor: str = ''
    prateleira: str = ''
    descricao: str = ''

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LocalEstoque':
        return cls(**data)


class LocalEstoqueManager:
    def __init__(self) -> None:
        self._locais: List[LocalEstoque] = []

    def _load_from_data(self, data: Dict[str, Any]) -> None:
        self._locais = [LocalEstoque.from_dict(item) for item in data.get('locais', [])]

    def criar_local(self, local: LocalEstoque) -> None:
        if any(item.id == local.id for item in self._locais):
            raise ValueError(f'Local de estoque com ID "{local.id}" já existe.')
        self._locais.append(local)

    def listar_locais(self) -> List[LocalEstoque]:
        return list(self._locais)

    def listar_locais_dicts(self) -> List[Dict[str, Any]]:
        return [item.to_dict() for item in self._locais]

    def obter_local(self, local_id: Optional[str]) -> Optional[LocalEstoque]:
        if local_id is None:
            return None
        return next((item for item in self._locais if item.id == local_id), None)
