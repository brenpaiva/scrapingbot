import re
import time
import requests

from datetime import datetime
from ..items import NormItemLoader
from scrapy import Spider, Request
from scrapy.http import Response
from scrapy.selector import Selector
#from pdf_parser import parse_pdf_from_link, correct_pdf_text
#from text_work import get_date, get_num, get_norm_type_from_title


"""
    Nome do site: Ministério da Fazenda
    Origem: notícias do portal gov.br/fazenda (seletor “Assuntos > Notícias”)
    Obs.: scrape até a segunda página; extrai título, data, link, tags e texto da notícia
"""



def parse_text(response):
    item = response.meta.get("item", {})
    selector = Selector(response)
    paragraphs = selector.xpath('//div[@id="content-core"]//p/text()').getall()
    text = ' '.join(p.strip() for p in paragraphs if p.strip())
    item['texto'] = text
    yield item


class noticias_fazenda(Spider):
    name = 'noticias_fazenda'
    pipeline = None
    start_urls = ['https://www.gov.br/fazenda/pt-br/assuntos/noticias?b_start:int=0']
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'noticias_fazenda.json',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }


    def parse(self, response: Response, *args, **kwargs):
        self.logger.debug(f"====> Start parsing {self.name} <====")
        selector = Selector(response)
        norms = selector.xpath('//ul[contains(@class,"noticias")]/li')
        self.logger.debug(f"====> Encontrou {len(norms)} normas <====")

        for element in selector.xpath('//ul[contains(@class, "noticias")]//li'):
            titulo = element.xpath('.//h2/a/text()').get(default='').strip()
            data = element.xpath('.//span[contains(@class,"data")]/text()').get(default='').strip()
            link = element.xpath('.//h2/a/@href').get(default='').strip()
            tags = element.xpath('.//div[contains(@class,"subject-noticia")]//a/text()').getall()
            tags = [t.strip() for t in tags if t.strip()]
            categoria = element.xpath('.//div[contains(@class,"subtitulo-noticia")]/text()').get(default='').strip()
            if self.pipeline and self.pipeline.have_in_mdb({"link": link}):
                continue

            loader: NormItemLoader = NormItemLoader(selector=element)
            self.logger.debug(f'====> Título: {titulo}  ')
            loader.add_value("origem", self.name)
            loader.add_value("titulo", titulo)
            loader.add_value("data_emissao", data)
            loader.add_value("categoria", categoria)
            loader.add_value("tags_norma", tags)
            loader.add_value("tipo", "Notícia")
            loader.add_value("link", link)
            loader.add_value("assunto", categoria)
            request = Request(link, callback=parse_text)
            request.meta["item"] = loader.load_item()
            yield request

        next_url = selector.xpath('//ul[contains(@class,"paginacao")]//a[contains(.,"Próximo")]/@href').get()
        if next_url and "b_start:int=0" in response.url:
            yield response.follow(next_url, callback=self.parse)
