# GerenciamentoEstoque
Sistema de gerenciamento de estoque com CRUD de produtos e armazenamento em arquivo JSON.

## Como executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie a interface web com Streamlit:
   ```bash
   streamlit run CadastroProdutos/app.py
   ```

## Funcionalidades

- Cadastro de produtos com atributos como código, nome, descrição, peso, código de barras,
  embalagem, composição da embalagem, validade, dimensões, categoria, DUN, EAN e estoque.
- Consulta, atualização e exclusão de produtos.
- Cadastro de locais de estocagem e categorias.
- Persistência em `CadastroProdutos/dados_produtos.json`.

