# CLAUDE.md — RPA Challenge (rpachallenge.com)

## Objetivo

Automatizar o preenchimento de formulário dinâmico no site https://rpachallenge.com usando Python + Selenium via Selenoid.

---

## O que é o RPA Challenge

- O site apresenta um formulário com **7 campos** para preencher
- Os dados vêm de uma planilha Excel disponível para download no próprio site
- O formulário deve ser submetido **10 vezes** (10 rounds)
- A cada submissão, os campos **mudam de posição e ordem** na tela
- Os **IDs e XPaths dos campos também mudam** a cada round — não confiar neles
- O cronômetro começa quando o botão **"Start"** é clicado
- Antes de clicar em Start, é possível testar o formulário sem penalidade

---

## Campos do formulário (colunas do Excel)

| Campo no HTML (label) | Coluna no Excel |
|---|---|
| First Name | First Name |
| Last Name | Last Name |
| Company Name | Company Name |
| Role in Company | Role in Company |
| Address | Address |
| Email | Email |
| Phone Number | Phone Number |

---

## Regra crítica de localização dos campos

**NUNCA usar ID, XPath posicional ou ordem dos campos para localizar inputs.**

A única forma confiável é localizar pelo **label** do campo:

```python
# Estratégia correta: buscar o label e pegar o input associado
label = driver.find_element(By.XPATH, f"//label[contains(text(), '{field_name}')]")
input_field = label.find_element(By.XPATH, "./following-sibling::input | ../input")
```

Ou via atributo `ng-reflect-name` que corresponde ao nome do campo:

```python
input_field = driver.find_element(By.XPATH, f"//input[@ng-reflect-name='{field_key}']")
```

---

## Fluxo de execução

```
1. Abrir https://rpachallenge.com
2. Clicar em "Download" para baixar o Excel
3. Ler os dados do Excel (10 linhas de dados)
4. Clicar em "Start" para iniciar o cronômetro
5. Para cada uma das 10 linhas:
   a. Localizar cada campo pelo LABEL (não por posição)
   b. Preencher com o valor correspondente da linha
   c. Clicar em "Submit"
6. Capturar screenshot da tela de congratulações
```

---

## Stack técnica

- **Linguagem:** Python 3
- **Automação browser:** Selenium WebDriver
- **Browser:** Chrome via Selenoid (`http://192.168.56.101:4444/wd/hub`)
- **Leitura Excel:** openpyxl ou pandas
- **Selenoid configurado em:** Ubuntu Server (VirtualBox)

---

## Configuração do WebDriver com Selenoid

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.set_capability("browserName", "chrome")
options.set_capability("browserVersion", "110.0")
options.set_capability("selenoid:options", {
    "name": "RPA Challenge",
    "sessionTimeout": "5m"
})

driver = webdriver.Remote(
    command_executor="http://192.168.56.101:4444/wd/hub",
    options=options
)
```

---

## O que NÃO fazer (anti-alucinações)

- ❌ NÃO usar `find_element(By.ID, ...)` — IDs mudam a cada round
- ❌ NÃO usar XPath com posição numérica como `//input[1]`
- ❌ NÃO usar `find_elements` e pegar por índice
- ❌ NÃO assumir que a ordem dos campos no HTML é a mesma da planilha
- ❌ NÃO hardcodar valores do Excel — sempre ler dinamicamente do arquivo
- ❌ NÃO clicar em Start antes de baixar e ler o Excel
- ❌ NÃO inventar URLs ou endpoints — usar apenas `https://rpachallenge.com`

---

## Estrutura de arquivos esperada

```
rpa-challenge/
├── main.py          # script principal
├── challenge.xlsx   # planilha baixada do site (gerada em runtime)
└── screenshot.png   # resultado final (gerada em runtime)
```

---

## Resultado esperado

Ao final das 10 submissões o site exibe uma tela de **congratulações** com:
- Porcentagem de acerto
- Tempo total gasto

O script deve tirar um **screenshot** dessa tela e salvar como `screenshot.png`.

---

## Notas importantes

- O Excel tem exatamente **10 linhas de dados** (1 por round)
- O botão de download tem o texto **"Download Excel"**
- O botão de início tem o texto **"Start"**
- O botão de submissão tem o tipo `type="submit"`
- A tela de congratulações tem a classe CSS `congratulations`
