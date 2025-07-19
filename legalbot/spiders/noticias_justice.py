import json
import html
from scrapy import Spider, Request
from scrapy.http import Response
from scrapy.selector import Selector
from ..items import NormItemLoader
from ..pdf_parser import parse_pdf_from_link, correct_pdf_text
from ..text_work import get_date


def parse_text(response: Response):
    # Recupera o item parcialmente preenchido
    item = response.meta.get("item", {})
    content_type = response.headers.get("Content-Type", b"").decode()

    if content_type.startswith("application/pdf"):
        # Parse de PDF
        pdf_text = parse_pdf_from_link(response.url)
        item['texto'] = correct_pdf_text(pdf_text)
    else:
        # Data de emissão no formato desejado
        iso_date = response.xpath(
            "//time/@datetime"
        ).get(default="")
        item['data_emissao'] = get_date(iso_date, "%Y-%m-%dT%H:%M:%SZ")

        # Categoria
        item['categoria'] = response.xpath(
            "//article//div[contains(@class,'category')]/text()"
        ).get(default="").strip()

        # Tags como lista
        tags = response.xpath(
            "//article//div[contains(@class,'tags')]//text()"
        ).getall()
        item['tags_norma'] = [t.strip() for t in tags if t.strip()]

        # Texto completo como string única
        paragraphs = response.xpath(
            "//article//div[contains(@class,'content')]//p//text()"
        ).getall()
        item['texto'] = ' '.join(p.strip() for p in paragraphs if p.strip())

    yield item


class NoticiasJusticeSpider(Spider):
    name = 'noticias_justice'
    start_urls = [
        'https://search.justice.gov/search?affiliate=justice&page=1&query=fcpa&utf8=%E2%9C%93'
    ]
    custom_settings = {
        # JSON Lines: um objeto por linha, sem array ou quebras de linha internas
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'noticias_justice.json',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def parse(self, response: Response):
        selector = Selector(response)
        raw = selector.xpath(
            "//div[@data-react-class='SearchResultsLayout']/@data-react-props"
        ).get(default="")
        data = json.loads(html.unescape(raw))
        noticias = (
            data.get("additionalResults", {}).get("textBestBets", [])
            + data.get("resultsData", {}).get("results", [])
        )

        for noticia in noticias:
            titulo = noticia.get("title", "").strip()
            link = noticia.get("url", "")
            assunto = noticia.get("description", "").strip()

            loader = NormItemLoader()
            loader.add_value("origem", self.name)
            loader.add_value("titulo", titulo)
            loader.add_value("tipo", "Notícia")
            loader.add_value("link", link)
            loader.add_value("assunto", assunto)
            base_item = loader.load_item()

            yield Request(link, callback=parse_text, meta={"item": base_item})

        # Paginação até página 2
        next_url = selector.xpath('//nav//ul/li[a[text()="2"]]/a/@href').get()
        if next_url:
            yield Request(response.urljoin(next_url), callback=self.parse)
