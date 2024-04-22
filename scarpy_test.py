import unittest
from unittest.mock import patch, MagicMock
from scrapy.http import TextResponse, Request
from default.spiders.amazon import AmazonSpider


class AmazonSpiderTest(unittest.TestCase):

    def setUp(self):
        self.spider = AmazonSpider(url='https://www.amazon.com/Apple-iPhone-11-64GB-Unlocked/dp/B07ZPKZSSC', job_id='1')

    @patch('scrapy.Spider.start_requests')
    def test_spider_with_mocked_response(self, mock_start_requests):
        with open('./fixtures/test0.html', 'r') as file:
            mock_response_content = file.read()

        # Create a mocked response object
        url = 'https://www.amazon.com/Apple-iPhone-11-64GB-Unlocked/dp/B07ZPKZSSC'
        request = Request(url=url)
        response = TextResponse(url=url, request=request, body=mock_response_content, encoding='utf-8')

        # Replace the start_requests method to yield our mocked response
        mock_start_requests.return_value = [response]

        # You can now test your spider's parsing logic
        result_items = []
        for item in self.spider.parse(response):
            result_items.append(item.meta)
        job = result_items[0]['job']
        product_data = job['result']
        self.assertTrue(product_data['image_url'] != '' and product_data['image_url'] is not None)
        self.assertTrue(product_data['description'] != '' and product_data['description'] is not None)
        self.assertTrue(product_data['title'] != '' and product_data['title'] is not None)
        self.assertTrue(product_data['specs'] != '' and product_data['specs'] is not None)
        self.assertTrue(product_data['price'] != '' and product_data['price'] is not None)
        self.assertTrue(product_data['features'] != '' and product_data['features'] is not None)
        self.assertTrue(len(product_data['reviews']) > 0 and product_data['reviews'] is not None)
        self.assertTrue(product_data['rating'] > 0 and product_data['rating'] is not None)

    @patch('scrapy.Spider.start_requests')
    def test_spider_with_mocked_response1(self, mock_start_requests):
        with open('./fixtures/test1.html', 'r') as file:
            mock_response_content = file.read()

        # Create a mocked response object
        url = ('https://www.amazon.com/Lenovo-IdeaPad-Display-Processor-82K20015US/dp/B08YKHGKTV?dchild=1&keywords'
               '=lenovo%2B5600H&qid=1631664165&sr=8-3&linkCode=sl1&tag=e074d-20&linkId'
               '=51930c39fb2d5742b7004cef85888197&language=en_US&ref_=as_li_ss_tl&th=1')
        request = Request(url=url)
        response = TextResponse(url=url, request=request, body=mock_response_content, encoding='utf-8')

        # Replace the start_requests method to yield our mocked response
        mock_start_requests.return_value = [response]

        # You can now test your spider's parsing logic
        result_items = []
        for item in self.spider.parse(response):
            result_items.append(item.meta)
        job = result_items[0]['job']
        product_data = job['result']
        self.assertTrue(product_data['image_url'] != '' and product_data['image_url'] is not None)
        self.assertTrue(product_data['description'] != '' and product_data['description'] is not None)
        self.assertTrue(product_data['title'] != '' and product_data['title'] is not None)
        self.assertTrue(product_data['specs'] != '' and product_data['specs'] is not None)
        self.assertTrue(product_data['price'] != '' and product_data['price'] is not None)
        self.assertTrue(product_data['features'] != '' and product_data['features'] is not None)
        self.assertTrue(len(product_data['reviews']) > 0 and product_data['reviews'] is not None)
        self.assertTrue(product_data['rating'] > 0 and product_data['rating'] is not None)

    @patch('scrapy.Spider.start_requests')
    def test_spider_with_mocked_response2(self, mock_start_requests):
        with open('./fixtures/test2.html', 'r') as file:
            mock_response_content = file.read()

        # Create a mocked response object
        url = ('https://www.amazon.com/Lenovo-IdeaPad-Display-Processor-82K20015US/dp/B08YKHGKTV?dchild=1&keywords'
               '=lenovo%2B5600H&qid=1631664165&sr=8-3&linkCode=sl1&tag=e074d-20&linkId'
               '=51930c39fb2d5742b7004cef85888197&language=en_US&ref_=as_li_ss_tl&th=1')
        request = Request(url=url)
        response = TextResponse(url=url, request=request, body=mock_response_content, encoding='utf-8')

        # Replace the start_requests method to yield our mocked response
        mock_start_requests.return_value = [response]

        # You can now test your spider's parsing logic
        result_items = []
        for item in self.spider.parse(response):
            result_items.append(item.meta)
        job = result_items[0]['job']
        product_data = job['result']
        self.assertTrue(product_data['image_url'] != '' and product_data['image_url'] is not None)
        self.assertTrue(product_data['description'] != '' and product_data['description'] is not None)
        self.assertTrue(product_data['title'] != '' and product_data['title'] is not None)
        self.assertTrue(product_data['specs'] != '' and product_data['specs'] is not None)
        self.assertTrue(product_data['price'] != '' and product_data['price'] is not None)
        self.assertTrue(product_data['features'] != '' and product_data['features'] is not None)
        self.assertTrue(len(product_data['reviews']) > 0 and product_data['reviews'] is not None)
        self.assertTrue(product_data['rating'] > 0 and product_data['rating'] is not None)


    @patch('scrapy.Spider.start_requests')
    def test_spider_with_mocked_response3(self, mock_start_requests):
        with open('./fixtures/test3.html', 'r') as file:
            mock_response_content = file.read()

        # Create a mocked response object
        url = 'https://www.amazon.com/dp/B0CP129FCR?th=1'
        request = Request(url=url)
        response = TextResponse(url=url, request=request, body=mock_response_content, encoding='utf-8')

        # Replace the start_requests method to yield our mocked response
        mock_start_requests.return_value = [response]

        # You can now test your spider's parsing logic
        result_items = []
        for item in self.spider.parse(response):
            result_items.append(item.meta)
        job = result_items[0]['job']
        product_data = job['result']
        self.assertTrue(product_data['image_url'] != '' and product_data['image_url'] is not None)
        self.assertTrue(product_data['description'] != '' and product_data['description'] is not None)
        self.assertTrue(product_data['title'] != '' and product_data['title'] is not None)
        self.assertTrue(product_data['specs'] != '' and product_data['specs'] is not None)
        self.assertTrue(product_data['price'] != '' and product_data['price'] is not None)
        self.assertTrue(product_data['features'] != '' and product_data['features'] is not None)
        self.assertTrue(len(product_data['reviews']) > 0 and product_data['reviews'] is not None)
        self.assertTrue(product_data['rating'] > 0 and product_data['rating'] is not None)
    # @patch('scraper.spiders.amazon.AmazonSpider.parse_critical_reviews')
    def test_parse_critical_reviews(self):
        # Load your HTML fixture
        with open('./fixtures/critical_reviews.html', 'r', encoding='utf-8') as file:
            mock_response_content = file.read()

        # Create a mocked response object to simulate the critical reviews page
        url = 'https://www.amazon.com/product-reviews/B08YKHGKTV/?filterByStar=critical'
        request = Request(url=url)
        response = TextResponse(url=url, request=request, body=mock_response_content.encode('utf-8'), encoding='utf-8')

        # Directly call parse_critical_reviews with the mocked response
        results = []
        for item in self.spider.parse_critical_reviews(response):
            results.append(item)

        # Perform your assertions
        # Since you know the structure of your fixture, you can assert specific aspects of the parsed data
        # For example, checking if the critical reviews list is not empty
        self.assertTrue(len(results) > 0, "No results returned from parse_critical_reviews")

        # You can add more assertions here based on the expected structure of your items
        # For example, checking for the presence of specific fields in the returned items
        for review in results:
            self.assertIn('review_text', review, "Review text is missing in the parsed item")
            self.assertNotEqual(review['review_text'], '', "Parsed review text is empty")

    def test_extract_questions_and_answers(self):
        # Load your HTML fixture
        with open('./fixtures/qa.html', 'r', encoding='utf-8') as file:
            mock_response_content = file.read()

        # Create a mocked response object to simulate the critical reviews page
        url = 'https://www.amazon.com/ask/questions/asin/B07K8WHH5J'
        request = Request(url=url)
        response = TextResponse(url=url, request=request, body=mock_response_content.encode('utf-8'), encoding='utf-8')

        # Directly call parse_critical_reviews with the mocked response
        results = []
        for item in self.spider.extract_questions_and_answers(response):
            results.append(item)

        # Perform your assertions
        # Since you know the structure of your fixture, you can assert specific aspects of the parsed data
        # For example, checking if the critical reviews list is not empty
        self.assertTrue(len(results) > 0, "No results returned from parse_critical_reviews")

        # You can add more assertions here based on the expected structure of your items
        # For example, checking for the presence of specific fields in the returned items
        for review in results:
            self.assertIn('review_text', review, "Review text is missing in the parsed item")
            self.assertNotEqual(review['review_text'], '', "Parsed review text is empty")


if __name__ == '__main__':
    unittest.main()
