import datetime
import functools
import json
import logging
import os
import re
import time
from random import randint
import scrapy
from scrapy import Spider


# os.environ['ENABLE_TIMING'] = 'true'
def timeit(method):
    """Decorator to measure the execution time of a method."""

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if os.getenv('ENABLE_TIMING', 'false').lower() == 'true':
            start_time = time.time()
            result = method(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            if isinstance(args[0], Spider):
                args[0].logger.info(f"{method.__name__} took {duration:.4f} seconds")
            else:
                print(f"{method.__name__} took {duration:.4f} seconds")
        else:
            result = method(*args, **kwargs)
        return result

    return wrapper


def clean_text(text):
    """
    Remove unwanted unicode characters, newline characters, excessive whitespace,
    and normalize the text for better usability.
    """
    # Remove Unicode LTR and RTL marks
    text = re.sub(r'[\u200e\u200f]', '', text)
    # Replace multiple whitespace characters including newlines and tabs with a single space
    text = re.sub(r'\s+', ' ', text)  # This pattern includes \n, \r, \t, and regular spaces
    text = text.replace('\\n', '')
    text = text.replace('\\r', '')
    return text.strip()


def safe_extract(response_or_selector, queries, query_type='css', extract_first=True, default_value=None):
    """
    Safely extract data from a given set of queries on a response or selector.
    Tries each query until successful extraction.
    :param response_or_selector: Scrapy Response or Selector object.
    :param queries: List of strings representing the CSS or XPath queries.
    :param query_type: 'css' for CSS queries, 'xpath' for XPath queries. Assumes all queries are of the same type.
    :param extract_first: True to extract the first result, False to extract all results from the first successful query.
    :param default_value: Default value to return if no data is found. Can be of any type.
    :return: Extracted data from the first successful query or default value.
    """
    for query in queries:
        if query_type == 'css':
            data = response_or_selector.css(query)
        elif query_type == 'xpath':
            data = response_or_selector.xpath(query)
        else:
            raise ValueError("Invalid query_type. Use 'css' or 'xpath'.")

        if data:
            if extract_first:
                extracted = data.get()
                if extracted is not None:
                    return clean_text(extracted)
            else:
                all_data = data.getall()
                if all_data:
                    return [clean_text(element) for element in all_data]

    # Return default value if none of the queries return data
    if not extract_first and isinstance(default_value, list):
        return default_value
    return [default_value] if not extract_first else default_value


def extract_price(response):
    price_selector = ".a-price-whole::text"
    price = safe_extract(response, [price_selector], extract_first=True, default_value='0')
    try:
        price = price.replace(',', '').replace('$', '')
        price = float(price)
    except ValueError:
        price = 0
    return price


def extract_title(response):
    title_selector = ['.a-size-medium.a-color-base.a-text-normal::text', 'div[data-cy="title-recipe"] span.a-text-normal::text']
    title = safe_extract(response, title_selector, extract_first=True)
    return title


def extract_rating(response):
    rating_selector = ".a-icon-alt::text"
    rating = safe_extract(response, [rating_selector], extract_first=True, default_value='0')
    try:
        rating = float(rating.split(' ')[0])
    except ValueError:
        rating = 0
    return rating


def extract_image_url(response):
    image_selector = ".s-image::attr(src)"
    image_url = safe_extract(response, [image_selector], extract_first=True)
    return image_url


def extract_brand(response):
    brand_selector = ".a-row.a-color-secondary h2 .a-size-medium::text"
    brand = safe_extract(response, [brand_selector], extract_first=True)
    return brand


def extract_stock(response):
    stock_selector = ".a-size-base.a-color-price::text"
    stock = safe_extract(response, [stock_selector], extract_first=True)
    return stock


def extract_asin_from_url(url):
    asin = re.search(r'/dp/(\w+)/?', url)
    return asin.group(1) if asin else None


def extract_asin_from_response(response):
    product_link_selector = "a.a-link-normal::attr(href)"
    product_link = safe_extract(response, [product_link_selector], extract_first=True, default_value='')
    return extract_asin_from_url(product_link)

def extract_discount(response):
    # Extract discount information, if available. This will look for any visible discount percentage or coupon application.
    discount = safe_extract(response, [
        'span.s-coupon-clipped::text',  # Extracting if coupon already applied
        'span.s-coupon-unclipped::text',
        's-coupon-clipped aok-hidden'# Extracting if coupon is available to be applied
    ], extract_first=True)
    if not discount:
        discount = "No discount information"  # Default text if no discount is found
    return discount


def parse_products(response):
    max_products = 15
    products_selector = "div.puis-card-container > div.a-section > div.puisg-row"
    products_selector2 = "div.puis-card-container > div.a-section"
    product_cards = response.css(products_selector)
    if not product_cards:
        product_cards = response.css(products_selector2)
    product_data = {
        "image_url": '',
        "title": '',
        "price": '',
        "rating": '',
        'brand': '',
        'stock': '',
        'discount': ''
    }
    products = []
    count = 0
    for product in product_cards:
        count += 1
        if count > max_products:
            break
        product_data['product_id'] = extract_asin_from_response(product)
        product_data['image_url'] = extract_image_url(product)
        product_data['title'] = extract_title(product)
        product_data['price'] = extract_price(product)
        product_data['rating'] = extract_rating(product)
        product_data['brand'] = extract_brand(product)
        product_data['stock'] = extract_stock(product)
        product_data['discount'] = extract_discount(product)
        products.append(product_data)
        product_data = {}
    return products


@timeit
def datetime_serializer(obj):
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class AmazonSearchSpider(scrapy.Spider):
    name = 'amazon_search'

    @timeit
    def __init__(self, url=None, job_id=None, *args, **kwargs):
        super(AmazonSearchSpider, self).__init__(*args, **kwargs)
        self.job = {}
        if not url or not job_id:
            logging.error("URL and Job ID are required")
            raise ValueError("URL and Job ID are required")
        self.start_urls = [url]  # This should be the URL you intend to scrape
        self.job_id = job_id
        self.products = []
        username = os.getenv("BRIGHT_DATA_USERNAME")
        password = os.getenv("BRIGHT_DATA_PASSWORD")
        host = os.getenv("BRIGHT_DATA_HOST")
        if not all([username, password, host]):
            logging.error("Missing proxy configuration")
            return
        session_id = randint(0, 1000000)
        proxy_user_pass = f"{username}-session-{session_id}:{password}"
        proxy_url = f"http://{proxy_user_pass}@{host}:22225"
        self.proxy = proxy_url

    @timeit
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'proxy': self.proxy})

    @timeit
    def close_job(self, response):
        # Logic to handle the response and close the job
        self.close(self, reason="Job completed successfully")

    def parse(self, response):
        selector = response.selector
        products = parse_products(selector)

        job = {
            'job_id': self.job_id,
            'status': 'completed',
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": datetime.datetime.now().isoformat(),
            'result': products,
            'url': response.url,
            'error': {}
        }
        data = json.dumps(job, default=datetime_serializer)
        endpoint = os.getenv("SERVICE_URL")
        yield scrapy.Request(url=endpoint + "/api/v1/scrapy/update", callback=self.close_job, body=data,
                             method='POST')
