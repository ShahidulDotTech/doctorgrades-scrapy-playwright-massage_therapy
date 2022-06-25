from stringprep import map_table_b2
import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags 

def remove_symbol(value):
    return value.replace('$', '').replace(',', '').strip()

def remove_whitespaces(value):
    return value.strip()

class HealthgradesItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(input_processor = MapCompose(remove_tags, remove_whitespaces), output_processor = TakeFirst())
    specialty = scrapy.Field(input_processor = MapCompose(remove_tags, remove_whitespaces), output_processor = TakeFirst())
    practice_name = scrapy.Field(input_processor = MapCompose(remove_tags, remove_whitespaces), output_processor = TakeFirst())
    address = scrapy.Field(input_processor = MapCompose(remove_tags, remove_whitespaces), output_processor = TakeFirst())
