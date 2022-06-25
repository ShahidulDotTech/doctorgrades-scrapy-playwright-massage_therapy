import scrapy
from scrapy.loader import ItemLoader
from healthgrades.items import HealthgradesItem
from scrapy_playwright.page import PageMethod 

# make the header elements like they are in a dictionary
def get_headers(s, sep=': ', strip_cookie=True, strip_cl=True, strip_headers: list = []) -> dict():
    d = dict()
    for kv in s.split('\n'):
        kv = kv.strip()
        if kv and sep in kv:
            v=''
            k = kv.split(sep)[0]
            if len(kv.split(sep)) == 1:
                v = ''
            else:
                v = kv.split(sep)[1]
            if v == '\'\'':
                v =''
            # v = kv.split(sep)[1]
            if strip_cookie and k.lower() == 'cookie': continue
            if strip_cl and k.lower() == 'content-length': continue
            if k in strip_headers: continue
            d[k] = v
    return d

# spider class
class DoctorSpider(scrapy.Spider):
    name = 'doctor'
    allowed_domains = ['healthgrades.com']
    url = 'https://www.healthgrades.com/usearch?what=Massage%20Therapy&entityCode=PS444&where=New%20York&pageNum={}&sort.provider=bestmatch&='

# change the header of bot to look like a browser
    def start_requests(self):
        h = get_headers(
            '''
            accept: */*
            accept-encoding: gzip, deflate, br
            accept-language: en-US,en;q=0.9
            dnt: 1
            origin: https://www.healthgrades.com
            referer: https://www.healthgrades.com/
            sec-ch-ua: ".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"
            sec-ch-ua-mobile: ?0
            sec-ch-ua-platform: "Windows"
            sec-fetch-dest: empty
            sec-fetch-mode: cors
            sec-fetch-site: cross-site
            user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36
            '''
        )

        for i in range(1, 6): # Change the range to the page numbers. more improvement can be done
            # GET request. url to first page
            yield scrapy.Request(self.url.format(i), headers =h, meta=dict(
                playwright = True,
                playwright_include_page = True,
                playwright_page_methods =[PageMethod('wait_for_selector', 'h3.card-name a')] # for waiting for a particular element to load 
            )) 

    def parse(self, response):
        for link in response.css('div h3.card-name a::attr(href)'): # individual doctor's link
            yield response.follow(link.get(), callback = self.parse_categories) # enter into the website
            
    def parse_categories(self, response):
        l = ItemLoader(item  = HealthgradesItem(), selector = response)

        l.add_xpath('name', '//*[@id="summary-section"]/div[1]/div[2]/div/div/div[1]/div[1]/h1')
        l.add_xpath('specialty', '//*[@id="summary-section"]/div[1]/div[2]/div/div/div[1]/div[1]/div[2]/p/span[1]')
        l.add_xpath('practice_name', '//*[@id="summary-section"]/div[1]/div[2]/div/div/div[2]/div[1]/p')
        l.add_xpath('address', 'string(//*[@id="summary-section"]/div[1]/div[2]/div/div/div[2]/div[1]/address)')

        yield l.load_item()

