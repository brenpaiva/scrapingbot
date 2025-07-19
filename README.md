# Legalbot Scraper

## Visão Geral

Este projeto implementa dois spiders Scrapy para extração de notícias:

- **noticias_fazenda**: coleta notícias do site da Fazenda (https://www.gov.br/fazenda/pt-br/assuntos/noticias), navegando até a segunda página.
- **noticias_justice**: coleta resultados de busca de notícias relacionadas ao FCPA no site do Departamento de Justiça dos EUA (https://search.justice.gov), até a página 2.

Cada spider captura:
1. **Título**  
2. **Data**  
3. **Link da notícia**  
4. **Tags**  
5. **Texto completo**  

O resultado é exportado como um arquivo JSON Lines (`.json`), com um objeto por linha.

## Pré-requisitos

- Docker  
- Python 3.7 ou superior  
- Scrapy >= 2.13.3  
- requests  
- PyPDF2  

## Instalação

### Usando Docker

1. Construa a imagem Docker:
   ```bash
   docker build -t legalbot-scraper .
   ```
2. Execute o container para coletar notícias da Fazenda:
   ```bash
   docker run --rm -v $(pwd)/output:/app/output legalbot-scraper scrapy crawl noticias_fazenda -o output/noticias_fazenda.json
   ```
3. Execute o container para coletar notícias do Justice.gov:
   ```bash
   docker run --rm -v $(pwd)/output:/app/output legalbot-scraper scrapy crawl noticias_justice -o output/noticias_justice.json
   ```

### Local (sem Docker)

1. Clone este repositório:  
   ```bash
   git clone <URL_DO_REPO>
   cd legalbot
   ```
2. Crie e ative um ambiente virtual:  
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. Instale as dependências:  
   ```bash
   pip install -r requirements.txt
   ```

## Estrutura do Projeto

```
legalbot/
├── Dockerfile
├── items.py
├── pipelines.py
├── middlewares.py
├── pdf_parser.py
├── text_work.py
├── settings.py
└── spiders/
    ├── noticias_fazenda.py
    └── noticias_justice.py
```

### Dockerfile

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Define o comando padrão (pode ser sobrescrito)
CMD ["scrapy", "crawl", "noticias_fazenda"]
```

### items.py

Define a classe `NormItem` e o `NormItemLoader` para padronização dos campos:
- origem  
- titulo  
- data_emissao  
- categoria  
- tags_norma  
- tipo  
- link  
- assunto  
- texto  

### text_work.py

Funções utilitárias:
- `get_date(data_str: str, formato: str)`: normaliza datas para `dd/mm/YYYY`. fileciteturn0file0  

### pdf_parser.py

- `parse_pdf_from_link(url: str)`: faz download e extrai texto do PDF.  
- `correct_pdf_text(text: str)`: corrige quebras de linhas (`-
`, `
`). fileciteturn0file1  

### spiders/

Cada spider segue o mesmo padrão:
1. **Imports** essenciais (re, time, requests, datetime, Scrapy, pdf_parser, text_work).  
2. **parse_text(response)** (fora da classe): extrai o conteúdo HTML ou PDF com base no `Content-Type`.  
3. **Classe Spider** (`Spider`):
   - `name`: nome do spider.  
   - `start_urls`: URL inicial.  
   - `parse()`: identifica elementos de notícias, extrai campos e agenda `Request` para `parse_text`.  
   - Paginação: identifica link da página seguinte e faz `yield` para `self.parse`.  

## Execução dos Spiders

Como mostrado acima, use Docker ou execute localmente:

```bash
# Via Docker (exemplo para Justiça)
docker run --rm -v $(pwd)/output:/app/output legalbot-scraper scrapy crawl noticias_justice -o output/noticias_justice.json
```

## Decisões Técnicas

- **ItemLoader**: uso do `NormItemLoader` para limpeza e padronização dos campos.  
- **Tratamento de PDF**: detecção de `Content-Type` e parsing via `PyPDF2` para PDFs.  
- **Normalização de Data**: uso de `get_date` para unificação de formatos.  
- **Delay e Concurrency**: respeita `DOWNLOAD_DELAY = 1` e `CONCURRENT_REQUESTS_PER_DOMAIN = 1` para gentileza com o servidor. fileciteturn0file5  
- **Limite de Páginas**: spiders parametrizadas para coletar apenas até a segunda página.  

## Boas Práticas

- Obediência ao `robots.txt` (`ROBOTSTXT_OBEY = True`).  
- Logging em nível DEBUG para rastreabilidade.  
- Modularidade: funções auxiliares fora da classe spider.  
- Verificação de duplicatas via pipeline ou método `have_in_mdb` (caso aplicado).  
- Estrutura de código consistente e legível.

## Formato de Saída JSON

Cada linha do arquivo `.json` corresponde a um objeto com os campos padronizados:
```json
{
  "origem": ["noticias_justice"],
  "titulo": ["Exemplo de Título"],
  "data_emissao": ["16/07/2025"],
  "categoria": ["Exemplo"],
  "tags_norma": ["TAG1, TAG2"],
  "tipo": ["Notícia"],
  "link": ["https://..."],
  "assunto": ["Exemplo"],
  "texto": "Texto completo da notícia..."
}
```

## Licença

This project is licensed under the MIT License.
