from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .Locais import LocalEstoqueManager

DB_FILE = Path(__file__).resolve().parent / 'dados_produtos.json'

@dataclass
class Categoria:
    nome: str
    descricao: str = ''

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Categoria':
        return cls(**data)


@dataclass
class Produto:
    codigo: str
    nome: str
    descricao: str
    peso: float
    codigobarra: str
    embalagem: str
    composicao_embalagem: str
    data_validade: str
    dimensoes: str
    categoria: str
    dun: str
    ean: str
    quantidade: int = 0
    local_id: Optional[str] = None
    preco_unitario: float = 0.0
    ativo: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Produto':
        return cls(**data)


class EstoqueManager:
    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path) if db_path else DB_FILE
        self.locais = LocalEstoqueManager()
        self._load()

    def _load(self) -> None:
        if not self.db_path.exists():
            self._data = {'produtos': [], 'categorias': [], 'locais': []}
            self._save()
        else:
            raw_text = self.db_path.read_text(encoding='utf-8')
            self._data = json.loads(raw_text) if raw_text.strip() else {'produtos': [], 'categorias': [], 'locais': []}
            self._data.setdefault('produtos', [])
            self._data.setdefault('categorias', [])
            self._data.setdefault('locais', [])
        self.locais._load_from_data(self._data)

    def _save(self) -> None:
        self._data['locais'] = self.locais.listar_locais_dicts()
        self.db_path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding='utf-8')

    def criar_produto(self, produto: Produto) -> None:
        if self.consultar_produto(produto.codigo) is not None:
            raise ValueError(f'Produto com código "{produto.codigo}" já existe.')
        self._data['produtos'].append(produto.to_dict())
        self._save()

    def listar_produtos(self) -> List[Produto]:
        return [Produto.from_dict(item) for item in self._data.get('produtos', [])]

    def consultar_produto(self, codigo: str) -> Optional[Produto]:
        produto = next((item for item in self._data.get('produtos', []) if item.get('codigo') == codigo), None)
        return Produto.from_dict(produto) if produto else None

    def atualizar_produto(self, codigo: str, novos_dados: Dict[str, Any]) -> None:
        for index, item in enumerate(self._data.get('produtos', [])):
            if item.get('codigo') == codigo:
                item.update(novos_dados)
                self._data['produtos'][index] = item
                self._save()
                return
        raise ValueError(f'Produto com código "{codigo}" não encontrado.')

    def remover_produto(self, codigo: str) -> None:
        produtos = self._data.get('produtos', [])
        atualizados = [item for item in produtos if item.get('codigo') != codigo]
        if len(atualizados) == len(produtos):
            raise ValueError(f'Produto com código "{codigo}" não encontrado.')
        self._data['produtos'] = atualizados
        self._save()

    def criar_categoria(self, categoria: Categoria) -> None:
        if any(item.get('nome') == categoria.nome for item in self._data.get('categorias', [])):
            raise ValueError(f'Categoria "{categoria.nome}" já existe.')
        self._data['categorias'].append(categoria.to_dict())
        self._save()

    def listar_categorias(self) -> List[Categoria]:
        return [Categoria.from_dict(item) for item in self._data.get('categorias', [])]

    def obter_local(self, local_id: Optional[str]) -> Optional[Dict[str, Any]]:
        local = self.locais.obter_local(local_id)
        return local.to_dict() if local else None
