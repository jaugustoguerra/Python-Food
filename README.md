
# Simulador de Pedido e Rastreamento

Este projeto simula um sistema de pedidos online, inspirado no modelo de delivery de aplicativos como iFood. O sistema permite ao usuário escolher uma loja, fazer um pedido e acompanhar o rastreamento da entrega em tempo real, utilizando a API do Google Maps para calcular a rota do entregador.

## Tecnologias Utilizadas

- **Dash**: Framework Python para criação de aplicações web interativas.
- **Dash Leaflet**: Biblioteca para renderizar mapas interativos.
- **Google Maps API**: Para calcular as rotas de entrega.
- **Python**: Linguagem de programação para lógica de backend.
- **SQLite**: Para armazenar os dados de pedidos e status (não utilizado diretamente neste código, mas recomendado para armazenar dados em uma versão mais robusta).
- **dotenv**: Para carregar variáveis de ambiente, como a chave da API do Google Maps.

## Funcionalidades

- **Escolha de Loja**: O usuário pode selecionar uma loja entre três opções (Hamburgueria, Pizza e Sushi) e fornecer um endereço de entrega.
- **Menu de Pedido**: Após escolher a loja, o usuário pode visualizar o menu e selecionar um item para fazer o pedido.
- **Status do Pedido**: Após o pedido ser realizado, o status de preparação e entrega é atualizado.
- **Rastreamento de Entrega**: O usuário pode visualizar a rota do entregador em tempo real no mapa interativo, que é atualizado a cada 5 segundos.

## Como Executar o Projeto

1. Clone este repositório para sua máquina local:

    ```bash
    git clone https://github.com/jaugustoguerra/Python-Food
    ```

2. Instale as dependências necessárias:

    ```bash
    pip install -r requirements.txt
    ```

3. Crie um arquivo `.env` na raiz do projeto e adicione a chave da API do Google Maps:

    ```bash
    CDS_API_KEY=Sua_Chave_da_API_Do_Google_Maps
    ```

4. Execute o aplicativo:

    ```bash
    python app.py
    ```

5. Abra o navegador e acesse `http://127.0.0.1:8050/` para interagir com a aplicação.

## Estrutura do Projeto

```
Python-Food/
│
├── app.py                # Código principal da aplicação
├── rota_cache.json       # Arquivo de cache para armazenar rotas
├── requirements.txt      # Dependências do projeto
├── .env                  # Variáveis de ambiente (não versionado)
└── assets/               # Pasta para arquivos estáticos (CSS, imagens, etc)
```

## Funcionalidade de Roteamento

A aplicação utiliza a API do Google Maps para calcular a rota de entrega entre a loja selecionada e o endereço de entrega informado pelo usuário. A cada 5 segundos, a posição do entregador é atualizada, e o progresso da entrega é exibido no mapa.

## Personalização

Você pode modificar o comportamento do sistema, como adicionar mais lojas, alterar os menus e personalizar o estilo da aplicação. Para mais informações sobre como interagir com a API do Google Maps, consulte a [documentação oficial](https://developers.google.com/maps/documentation).

## Contribuição

Sinta-se à vontade para contribuir com melhorias para o projeto! Para sugestões, correções de bugs ou novos recursos, por favor, abra uma **issue** ou envie um **pull request**.

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE).
