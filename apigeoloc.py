import dash
from dash import dcc, html, Input, Output, State
import dash_leaflet as dl
import googlemaps
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import random

# Carregar variáveis do ambiente
load_dotenv()
CDS_API_KEY = os.getenv("CDS_API_KEY")
if not CDS_API_KEY:
    raise ValueError("Erro: A chave da API não foi encontrada.")

gmaps = googlemaps.Client(key=CDS_API_KEY)

# Definição das lojas com menus e avaliações
lojas = {
    "Hamburgueria Top": {
        "endereco": "Rua José Raimundo de Freitas, Juiz de Fora, MG",
        "avaliacao": 4.8,
        "menu": {
            "🍔 Hambúrguer": 22.00,
            "🍟 Batata Frita": 10.00,
            "🥤 Refrigerante": 7.00,
            "🥪 X-Burger": 25.00,
            "🍗 Frango Frito": 18.00,
            "🍕 Pizza Individual": 32.00,
            "🍺 Cerveja": 8.00,
            "🍩 Donuts": 12.00
        }
    },
    "Pizza Express": {
        "endereco": "Rua São Mateus, Juiz de Fora, MG",
        "avaliacao": 4.5,
        "menu": {
            "🍕 Pizza": 38.00,
            "🧀 Queijo Extra": 5.00,
            "🥤 Suco": 8.00,
            "🍖 Carne de Sol": 28.00,
            "🍝 Lasanha": 35.00,
            "🍅 Salada Caprese": 22.00,
            "🍷 Vinho Tinto": 40.00,
            "🍮 Pudim": 14.00
        }
    },
    "Sushi Master": {
        "endereco": "Shopping Independência, Juiz de Fora, MG",
        "avaliacao": 4.7,
        "menu": {
            "🍣 Sushi": 55.00,
            "🍤 Tempurá": 25.00,
            "🍶 Saquê": 30.00,
            "🍱 Box de Sushi": 80.00,
            "🍙 Onigiri": 15.00,
            "🍜 Ramen": 35.00,
            "🍚 Arroz de Sushi": 12.00,
            "🍥 Tamago": 18.00
        }
    }
}


modo_transporte = "driving"
horario_atual = datetime.now()

# Status do pedido
status_pedido = ["📥 Pedido recebido", "👨‍🍳 Em preparo", "🚴 Saiu para entrega", "✅ Entregue"]
status_atual = 0

# Inicializa o Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "iFood Simulado"

# Estilos CSS
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('🏪 Escolher Loja', href='/lojas', className='nav-link'),
        dcc.Link('🛒 Fazer Pedido', href='/pedido', className='nav-link'),
        dcc.Link('📍 Rastreamento', href='/rastreamento', className='nav-link')
    ], className='navbar'),
    html.Div(id='page-content', className='content'),
    # Adiciona o item-menu ao layout inicial, mas oculta-o
    dcc.Dropdown(id="item-menu", placeholder="Escolha um item", className='dropdown', style={'display': 'none'})
])

# Layout da página de lojas
lojas_layout = html.Div([
    html.H1("🏪 Escolha uma Loja", className='title'),
    dcc.Dropdown(
        id="escolha-loja",
        options=[{"label": f"{loja} - ⭐ {info['avaliacao']}", "value": loja} for loja, info in lojas.items()],
        placeholder="Selecione uma loja",
        className='dropdown'
    ),
    html.Div([
        html.Label("Endereço de Entrega:", className='label-endereco'),
        dcc.Input(
            id="endereco-entrega",
            type="text",
            placeholder="Digite seu endereço de entrega",
            className='input-endereco'
        )
    ], className='container-endereco'),
    html.Button("Selecionar Loja", id="btn-selecionar-loja", n_clicks=0, className='button'),
    html.Div(id="detalhes-loja", className='status')
])

# Layout da página de pedido
pedido_layout = html.Div([
    html.H1("🍽 Faça seu Pedido", className='title'),
    html.Div(id="item-menu-container"),  # Container para o item-menu
    html.Button("Fazer Pedido", id="btn-pedido", n_clicks=0, className='button'),
    html.Div(id="status-pedido", className='status'),
    html.Div(id="mensagem-rastreamento", className='mensagem')
])

# Layout da página de rastreamento
rastreamento_layout = html.Div([
    html.H1("🚚 Rastreamento do Pedido", className='title'),
    dl.Map(
        style={'width': '100%', 'height': '400px'},
        center=[-21.7605, -43.3503],  # Centro de Juiz de Fora
        zoom=14,
        children=[
            dl.TileLayer(),
            dl.Polyline(id="rota", positions=[], color="blue", weight=6, opacity=0.7),
            dl.Marker(id="marker", position=[-21.7605, -43.3503],
                      children=[dl.Tooltip("🚴 Entregador")])
        ]
    ),
    dcc.Interval(id="interval-component", interval=5000, n_intervals=0)
])

# Callback para troca de páginas
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/rastreamento':
        return rastreamento_layout
    elif pathname == '/pedido':
        return pedido_layout
    return lojas_layout

# Callback para atualizar a visibilidade do item-menu
@app.callback(
    [Output("item-menu", "style"), Output("url", "pathname")],
    [Input("btn-selecionar-loja", "n_clicks")],
    [State("escolha-loja", "value"), State("endereco-entrega", "value")]
)
def atualizar_visibilidade_item_menu(n, loja, endereco_entrega):
    if n > 0 and loja and endereco_entrega:
        return {'display': 'block'}, '/pedido'  # Mostra o item-menu e redireciona para a página de pedidos
    return {'display': 'none'}, '/lojas'

# Estado global
loja_selecionada = None
pedido_confirmado = False
rota_entrega = []
posicao_atual = 0

# Função para obter a rota
def obter_rota(origem, destino):
    try:
        with open("rota_cache.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        rota = gmaps.directions(origem, destino, mode=modo_transporte, departure_time=horario_atual)
        with open("rota_cache.json", "w") as f:
            json.dump(rota, f)
        return rota

# Função para excluir o cache da rota
def excluir_cache_rota():
    if os.path.exists("rota_cache.json"):
        os.remove("rota_cache.json")

# Callback para selecionar loja e exibir menu
@app.callback(
    [Output("detalhes-loja", "children"), Output("item-menu", "options")],
    [Input("btn-selecionar-loja", "n_clicks")],
    [State("escolha-loja", "value"), State("endereco-entrega", "value")]
)
def selecionar_loja(n, loja, endereco_entrega):
    global loja_selecionada, rota_entrega, posicao_atual
    if n > 0 and loja and endereco_entrega:
        loja_selecionada = loja
        menu = lojas[loja]['menu']
        # Exclui o cache da rota anterior
        excluir_cache_rota()
        # Obter a rota entre o restaurante e o endereço de entrega
        rota = obter_rota(lojas[loja]['endereco'], endereco_entrega)
        if rota:
            rota_entrega = googlemaps.convert.decode_polyline(rota[0]['overview_polyline']['points'])
            posicao_atual = 0
        return f"Loja selecionada: {loja} ⭐ {lojas[loja]['avaliacao']}", [
            {"label": f"{item} - R$ {preco:.2f}", "value": item} for item, preco in menu.items()
        ]
    return "Selecione uma loja e insira o endereço de entrega para visualizar o menu.", []

# Callback para gerenciar pedido
@app.callback(
    [Output("status-pedido", "children"), Output("mensagem-rastreamento", "children")],
    [Input("btn-pedido", "n_clicks")],
    [State("item-menu", "value")]
)
def atualizar_status_pedido(n, item):
    global pedido_confirmado, status_atual
    if n > 0 and item:
        pedido_confirmado = True
        status_atual = 0
        return f"{item} solicitado! {status_pedido[status_atual]}", html.Div([
            html.P("Seu pedido está sendo preparado. Acompanhe o rastreamento:"),
            dcc.Link('📍 Rastreamento', href='/rastreamento', className='button')
        ])
    return "Escolha um item e clique para fazer o pedido.", ""

# Callback para atualizar posição do entregador
@app.callback(
    [Output("marker", "position"), Output("rota", "positions")],
    [Input("interval-component", "n_intervals")],
    prevent_initial_call=True
)
def atualizar_entrega(n):
    global posicao_atual, rota_entrega
    if pedido_confirmado and posicao_atual < len(rota_entrega) - 1:
        posicao_atual += 1
    elif posicao_atual >= len(rota_entrega) - 1:
        # Entrega finalizada, exclui o cache da rota
        excluir_cache_rota()
    return [rota_entrega[posicao_atual]["lat"], rota_entrega[posicao_atual]["lng"]], [[p["lat"], p["lng"]] for p in rota_entrega]

# Executar a aplicação
if __name__ == "__main__":
    app.run(debug=True)