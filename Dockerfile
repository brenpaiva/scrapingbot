# Dockerfile for the legalbot project
# This Dockerfile sets up a Python environment with Scrapy to scrape legal news
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /usr/src/app/output

CMD ["sh", "-c", "\
    scrapy crawl noticias_fazenda --output=output/noticias_fazenda.json:jsonlines && \
    scrapy crawl noticias_justice --output=output/noticias_justice.json:jsonlines \
"]