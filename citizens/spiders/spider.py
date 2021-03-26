import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CitizensItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class CitizensSpider(scrapy.Spider):
	name = 'citizens'
	start_urls = ['https://www.cbbank.com/about-us/news-media/']

	def parse(self, response):
		articles = response.xpath('//ul[@class="news-list"]/li')
		for article in articles:
			date = article.xpath('.//small[@class="date"]/text()').get()
			post_links = article.xpath('.//a[@class="btn"]/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="col-md-9"]/h3/text()').get()
		content = response.xpath('//div[@class="col-md-9"]//text()[not (ancestor::h3)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CitizensItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
