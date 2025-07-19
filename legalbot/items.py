# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader

class NormItem(scrapy.Item):
    origem = scrapy.Field()
    titulo = scrapy.Field()
    data_emissao = scrapy.Field()
    categoria = scrapy.Field()
    tags_norma = scrapy.Field()
    tipo = scrapy.Field()
    link = scrapy.Field()
    assunto = scrapy.Field()
    texto = scrapy.Field()


class NormItemLoader(ItemLoader):
    default_item_class = NormItem