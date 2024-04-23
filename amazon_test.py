import unittest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from default.spiders.amazon import AmazonSpider
from dotenv import load_dotenv
load_dotenv()


class AmazonSpiderTest(unittest.TestCase):
    def setUp(self):
        self.crawler_process = CrawlerProcess(get_project_settings())

    def test_spider(self):
        self.crawler_process.crawl(AmazonSpider,
                                   url='https://www.amazon.com/dp/B0CRDDWTX3',
                                   job_id='123')
        self.crawler_process.start()


if __name__ == '__main__':
    unittest.main()
