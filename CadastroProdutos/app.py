from pathlib import Path

import streamlit as st

from Locais import LocalEstoque
from Produtos import Categoria, EstoqueManager, Produto

DATA_PATH = Path(__file__).resolve().parent / 'dados_produtos.json'

st.set_page_config(page_title='Cadastro de Produtos', layout='wide')
manager = EstoqueManager(DATA_PATH)

st.title('Gerenciamento de Cadastro de Produtos')

st.markdown('Este sistema usa um arquivo JSON local como banco de dados, mantendo cadastro, estoque e organização de locais de estocagem.')

categories = manager.listar_categorias()
category_names = [c.nome for c in categories]
local_options = manager.locais.listar_locais()
local_names = [f'{loc.id} - {loc.nome}' for loc in local_options]

tab1, tab2, tab3, tab4 = st.tabs(['Cadastro / Atualização', 'Consulta', 'Remoção', 'Locais e Categorias'])

with tab1:
    st.header('Criar ou atualizar produto')
    modo = st.radio('Operação', ['Criar novo produto', 'Atualizar produto'], horizontal=True)
    codigo = st.text_input('Código do produto', max_chars=50)
    nome = st.text_input('Nome', max_chars=120)
    descricao = st.text_area('Descrição', height=120)
    peso = st.number_input('Peso (kg)', min_value=0.0, step=0.01, format='%.2f')
    codigobarra = st.text_input('Código de barras', max_chars=80)
    embalagem = st.text_input('Embalagem', max_chars=80)
    composicao_embalagem = st.text_input('Composição da embalagem', max_chars=120)
    data_validade = st.date_input('Data de validade').isoformat()
    dimensoes = st.text_input('Dimensões', help='Ex: 10x20x30 cm')
    categoria = st.selectbox('Categoria', ['<Nova categoria>'] + category_names)
    if categoria == '<Nova categoria>':
        nova_categoria = st.text_input('Nome da nova categoria', max_chars=80)
        descricao_categoria = st.text_area('Descrição da nova categoria', height=100)
        if nova_categoria:
            categoria = nova_categoria
    dun = st.text_input('DUN', max_chars=80)
    ean = st.text_input('EAN', max_chars=80)
    quantidade = st.number_input('Quantidade em estoque', min_value=0, step=1)
    preco_unitario = st.number_input('Preço unitário (R$)', min_value=0.0, step=0.01, format='%.2f')
    local_id = None
    if local_options:
        selected_local = st.selectbox('Local de estocagem', ['Nenhum'] + local_names)
        if selected_local != 'Nenhum':
            local_id = selected_local.split(' - ', 1)[0]
    else:
        st.info('Nenhum local cadastrado. Cadastre um local na aba Locais e Categorias.')

    if st.button('Salvar produto'):
        try:
            produto = Produto(
                codigo=codigo.strip(),
                nome=nome.strip(),
                descricao=descricao.strip(),
                peso=float(peso),
                codigobarra=codigobarra.strip(),
                embalagem=embalagem.strip(),
                composicao_embalagem=composicao_embalagem.strip(),
                data_validade=data_validade,
                dimensoes=dimensoes.strip(),
                categoria=categoria.strip(),
                dun=dun.strip(),
                ean=ean.strip(),
                quantidade=int(quantidade),
                local_id=local_id,
                preco_unitario=float(preco_unitario),
            )
            if not produto.codigo or not produto.nome:
                st.warning('Preencha ao menos o código e o nome do produto.')
            else:
                if modo == 'Criar novo produto':
                    manager.criar_produto(produto)
                    st.success(f'Produto {produto.nome} cadastrado com sucesso.')
                else:
                    if manager.consultar_produto(produto.codigo) is None:
                        st.warning(f'Produto com código {produto.codigo} não existe. Use criação ou verifique o código.')
                    else:
                        manager.atualizar_produto(produto.codigo, produto.to_dict())
                        st.success(f'Produto {produto.codigo} atualizado com sucesso.')
        except Exception as exc:
            st.error(str(exc))

with tab2:
    st.header('Consultar produtos')
    produtos = manager.listar_produtos()
    if produtos:
        codigos = [produto.codigo for produto in produtos]
        codigo_consulta = st.selectbox('Selecione o produto', [''] + codigos)
        if codigo_consulta:
            produto = manager.consultar_produto(codigo_consulta)
            if produto:
                st.subheader('Dados do produto')
                st.write('**Nome:**', produto.nome)
                st.write('**Descrição:**', produto.descricao)
                st.write('**Peso:**', produto.peso)
                st.write('**Código de barras:**', produto.codigobarra)
                st.write('**Embalagem:**', produto.embalagem)
                st.write('**Composição da embalagem:**', produto.composicao_embalagem)
                st.write('**Validade:**', produto.data_validade)
                st.write('**Dimensões:**', produto.dimensoes)
                st.write('**Categoria:**', produto.categoria)
                st.write('**DUN:**', produto.dun)
                st.write('**EAN:**', produto.ean)
                st.write('**Quantidade em estoque:**', produto.quantidade)
                st.write('**Preço unitário:**', f'R$ {produto.preco_unitario:.2f}')
                if produto.local_id:
                    local = manager.obter_local(produto.local_id)
                    st.write('**Local:**', local.get('nome') if local else produto.local_id)
    else:
        st.info('Nenhum produto cadastrado ainda.')

with tab3:
    st.header('Remover produto')
    produtos = manager.listar_produtos()
    if produtos:
        codigos = [produto.codigo for produto in produtos]
        codigo_remover = st.selectbox('Produto a remover', [''] + codigos)
        if codigo_remover and st.button('Apagar produto'):
            try:
                manager.remover_produto(codigo_remover)
                st.success(f'Produto {codigo_remover} removido com sucesso.')
            except Exception as exc:
                st.error(str(exc))
    else:
        st.info('Nenhum produto disponível para remoção.')

with tab4:
    st.header('Locais de estocagem')
    st.subheader('Cadastrar novo local')
    local_id = st.text_input('ID do local', max_chars=40)
    local_nome = st.text_input('Nome do local')
    corredor = st.text_input('Corredor')
    prateleira = st.text_input('Prateleira')
    descricao_local = st.text_area('Descrição do local', height=100)
    if st.button('Salvar local'):
        try:
            if not local_id.strip() or not local_nome.strip():
                st.warning('Preencha o ID e o nome do local.')
            else:
                novo_local = LocalEstoque(
                    id=local_id.strip(),
                    nome=local_nome.strip(),
                    corredor=corredor.strip(),
                    prateleira=prateleira.strip(),
                    descricao=descricao_local.strip(),
                )
                manager.locais.criar_local(novo_local)
                manager._save()
                st.success(f'Local {novo_local.nome} cadastrado com sucesso.')
        except Exception as exc:
            st.error(str(exc))

    st.subheader('Locais cadastrados')
    locais = manager.locais.listar_locais()
    if locais:
        for local in locais:
            st.write(f'**{local.id} - {local.nome}**')
            st.write('Corredor:', local.corredor, ' | Prateleira:', local.prateleira)
            st.write(local.descricao)
            st.markdown('---')
    else:
        st.info('Ainda não há locais cadastrados.')

    st.header('Categorias')
    nova_categoria = st.text_input('Nome da categoria')
    descricao_categoria = st.text_area('Descrição da categoria', height=100)
    if st.button('Salvar categoria'):
        try:
            if not nova_categoria.strip():
                st.warning('Informe o nome da categoria.')
            else:
                manager.criar_categoria(Categoria(nome=nova_categoria.strip(), descricao=descricao_categoria.strip()))
                st.success(f'Categoria {nova_categoria} registrada com sucesso.')
        except Exception as exc:
            st.error(str(exc))

    categorias = manager.listar_categorias()
    if categorias:
        for categoria in categorias:
            st.write(f'**{categoria.nome}** - {categoria.descricao}')
    else:
        st.info('Ainda não há categorias cadastradas.')
