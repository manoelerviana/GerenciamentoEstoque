from pathlib import Path
import streamlit as st

from Locais import LocalEstoque
from Produtos import Categoria, EstoqueManager, Produto

DATA_PATH = Path(__file__).resolve().parent / 'dados_produtos.json'

st.set_page_config(page_title='Cadastro de Produtos', layout='wide')

manager = EstoqueManager(DATA_PATH)

st.title('Gerenciamento de Cadastro de Produtos')

st.markdown(
    'Este sistema usa um arquivo JSON local como banco de dados, mantendo cadastro, estoque e organização de locais de estocagem.'
)

categories = manager.listar_categorias()
category_names = [c.nome for c in categories]

local_options = manager.locais.listar_locais()
local_names = [f'{loc.id} - {loc.nome}' for loc in local_options]

tab1, tab2, tab3, tab4 = st.tabs(
    ['Cadastro / Atualização', 'Consulta', 'Remoção', 'Locais e Categorias']
)

# ===================== ABA 1 =====================
with tab1:
    st.header('Criar ou atualizar produto')

    modo = st.radio(
        'Operação',
        ['Criar novo produto', 'Atualizar produto'],
        horizontal=True
    )

    codigo = st.text_input('Código do produto', max_chars=50)
    nome = st.text_input('Nome', max_chars=120)
    descricao = st.text_area('Descrição', height=120)
    peso = st.number_input('Peso (kg)', min_value=0.0, step=0.01)
    codigobarra = st.text_input('Código de barras')
    embalagem = st.text_input('Embalagem')
    composicao_embalagem = st.text_input('Composição da embalagem')
    data_validade = st.date_input('Data de validade').isoformat()
    dimensoes = st.text_input('Dimensões (ex: 10x20x30 cm)')

    categoria = st.selectbox(
        'Categoria',
        ['<Nova categoria>'] + category_names
    )

    if categoria == '<Nova categoria>':
        nova_categoria = st.text_input('Nome da nova categoria')
        descricao_categoria = st.text_area('Descrição da categoria')
        if nova_categoria.strip():
            categoria = nova_categoria.strip()

    dun = st.text_input('DUN')
    ean = st.text_input('EAN')
    quantidade = st.number_input('Quantidade', min_value=0, step=1)
    preco_unitario = st.number_input('Preço unitário (R$)', min_value=0.0)

    local_id = None
    if local_options:
        selected_local = st.selectbox(
            'Local de estocagem',
            ['Nenhum'] + local_names
        )
        if selected_local != 'Nenhum':
            local_id = selected_local.split(' - ')[0]

    if st.button('Salvar produto'):
        try:
            produto = Produto(
                codigo=codigo.strip(),
                nome=nome.strip(),
                descricao=descricao.strip(),
                peso=peso,
                codigobarra=codigobarra.strip(),
                embalagem=embalagem.strip(),
                composicao_embalagem=composicao_embalagem.strip(),
                data_validade=data_validade,
                dimensoes=dimensoes.strip(),
                categoria=categoria.strip(),
                dun=dun.strip(),
                ean=ean.strip(),
                quantidade=int(quantidade),
                preco_unitario=preco_unitario,
                local_id=local_id,
            )

            if not produto.codigo or not produto.nome:
                st.warning('Código e nome são obrigatórios.')
                st.stop()

            if modo == 'Criar novo produto':
                manager.criar_produto(produto)
                st.success('Produto cadastrado com sucesso.')
            else:
                manager.atualizar_produto(produto.codigo, produto.to_dict())
                st.success('Produto atualizado com sucesso.')

        except Exception as exc:
            st.error(str(exc))

# ===================== ABA 2 =====================
with tab2:
    st.header('Consultar produtos')

    produtos = manager.listar_produtos()
    if produtos:
        codigo = st.selectbox(
            'Selecione o produto',
            [p.codigo for p in produtos]
        )
        produto = manager.consultar_produto(codigo)

        if produto:
            st.json(produto.to_dict())
    else:
        st.info('Nenhum produto cadastrado.')

# ===================== ABA 3 =====================
with tab3:
    st.header('Remover produto')

    produtos = manager.listar_produtos()
    if produtos:
        codigo = st.selectbox(
            'Produto a remover',
            [p.codigo for p in produtos]
        )

        if st.button('Remover'):
            try:
                manager.remover_produto(codigo)
                st.success('Produto removido com sucesso.')
            except Exception as exc:
                st.error(str(exc))
    else:
        st.info('Nenhum produto disponível.')

# ===================== ABA 4 =====================
with tab4:
    st.header('Locais de estocagem')

    local_id = st.text_input('ID do local')
    local_nome = st.text_input('Nome do local')
    corredor = st.text_input('Corredor')
    prateleira = st.text_input('Prateleira')
    descricao_local = st.text_area('Descrição do local')

    if st.button('Cadastrar local'):
        try:
            novo_local = LocalEstoque(
                id=local_id.strip(),
                nome=local_nome.strip(),
                corredor=corredor.strip(),
                prateleira=prateleira.strip(),
                descricao=descricao_local.strip()
            )
            manager.locais.criar_local(novo_local)
            manager._save()
            st.success('Local cadastrado com sucesso.')
        except Exception as exc:
            st.error(str(exc))

    st.divider()
    st.subheader('Categorias')

    nome_cat = st.text_input('Nova categoria')
    desc_cat = st.text_area('Descrição da categoria')

    if st.button('Salvar categoria'):
        try:
            manager.criar_categoria(
                Categoria(nome=nome_cat.strip(), descricao=desc_cat.strip())
            )
            st.success('Categoria cadastrada.')
        except Exception as exc:
            st.error(str(exc))
