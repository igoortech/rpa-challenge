# RPA Challenge

Automação do formulário dinâmico do [rpachallenge.com](https://rpachallenge.com) usando Python e Selenium via Selenoid.

## O que faz

- Baixa a planilha Excel do site com os dados dos formulários
- Preenche o formulário 10 vezes automaticamente
- A cada round os campos mudam de posição — o script localiza pelo **label**, não por ID ou XPath posicional
- Tira screenshot da tela de congratulações ao final

## Stack

- Python 3 + Selenium
- Chrome via Selenoid (Docker)
- openpyxl para leitura do Excel

## Como rodar

1. Suba o Selenoid com Docker Compose:

```bash
docker-compose up -d
```

2. Execute o script:

```bash
pip install -r requirements.txt
python main.py
```

O screenshot final é salvo em `screenshot.png`.
