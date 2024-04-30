import unittest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from default.spiders.amazon import AmazonSpider
from dotenv import load_dotenv

from default.spiders.amazon_search import AmazonSearchSpider
from default.spiders.amazon_get_details import AmazonGetDetailsSpider

load_dotenv()


class AmazonSpiderTest(unittest.TestCase):
    def setUp(self):
        self.crawler_process = CrawlerProcess(get_project_settings())

    def test_spider(self):
        self.crawler_process.crawl(AmazonSpider,
                                   url='https://www.amazon.com/dp/B0CRDDWTX3',
                                   job_id='123')
        self.crawler_process.start()


class AmazonSearchSpiderTest(unittest.TestCase):
    def setUp(self):
        self.crawler_process = CrawlerProcess(get_project_settings())

    def test_spider(self):
        self.crawler_process.crawl(AmazonSearchSpider,
                                   url='https://www.amazon.com/s?k=fish%20bowl%20for%20a%20gold%20fish%20made%20of%20glass',
                                   job_id='123')
        self.crawler_process.start()


class AmazonGetDetailSpider(unittest.TestCase):
    def setUp(self):
        self.crawler_process = CrawlerProcess(get_project_settings())

    def test_spider(self):
        self.crawler_process.crawl(AmazonGetDetailsSpider,
                                   url=['https://www.amazon.com/dp/B0CRDDWTX3', 'https://www.amazon.com/dp/B09LYHV61V'],
                                   job_id='123')
        self.crawler_process.start()


if __name__ == '__main__':
    unittest.main()
