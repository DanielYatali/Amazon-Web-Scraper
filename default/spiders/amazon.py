import datetime
import json
import logging
import os
import re
from random import randint
import scrapy

def datetime_serializer(obj):
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

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
                    return extracted.strip()
            else:
                all_data = data.getall()
                if all_data:
                    return [element.strip() for element in all_data]

    # Return default value if none of the queries return data
    if not extract_first and isinstance(default_value, list):
        return default_value
    return [default_value] if not extract_first else default_value


def extract_table_data(response, table_selector):
    table = response.xpath(table_selector)
    data = {}
    key_selectors = [".//th/text()"]
    value_selectors = [".//td/text()"]
    for row in table.xpath(".//tr"):
        key = safe_extract(row, key_selectors, query_type='xpath', extract_first=True, default_value='Unknown Spec')
        value = safe_extract(row, value_selectors, query_type='xpath', extract_first=True,
                             default_value='Not Available')
        if key != 'Unknown Spec':
            # replace all /n and strip out excess space from the font and end of the string
            value = value.replace('\\n', '').strip()
            data[key.strip()] = value
    return data


def get_product_specs(response):
    product_specs = {}
    # Identify the specs table by its ID
    specs_table = response.xpath("//table[@id='productDetails_detailBullets_sections1']")
    tech_specs_table1 = response.xpath("//table[@id='productDetails_techSpec_section_1']")
    tech_spec_table2 = response.xpath("//table[@id='productDetails_techSpec_section_2']")
    product_specs.update(extract_table_data(response, "//table[@id='productDetails_detailBullets_sections1']"))
    product_specs.update(extract_table_data(response, "//table[@id='productDetails_techSpec_section_1']"))
    product_specs.update(extract_table_data(response, "//table[@id='productDetails_techSpec_section_2']"))

    return product_specs


def get_rating(response):
    # Define a list of selectors to try for extracting the rating
    rating_selectors = [
        'a.a-popover-trigger.a-declarative span.a-size-base.a-color-base::text',  # Original selector
        # Add any alternative selectors here as needed
    ]

    # Use the updated safe_extract function with a list of selectors
    rating = safe_extract(response, rating_selectors, query_type='css', extract_first=True, default_value='0.0')

    try:
        # Attempt to convert the extracted rating to a float
        return float(rating)
    except ValueError:
        # Log an error message if the conversion fails
        logging.error(f"Failed to convert rating '{rating}' to float.")
        return 0.0


def get_image_url(response):
    # Define a list of XPath selectors to try for extracting the image URL
    image_url_selectors = [
        "//div[@id='imgTagWrapperId']/img/@src",  # Original selector
        # You can add alternative selectors here as needed
    ]

    # Use the updated safe_extract function with a list of selectors
    return safe_extract(response, image_url_selectors, query_type='xpath', extract_first=True, default_value='')


def get_product_description(response):
    # Define a list of XPath selectors to try for extracting the product description
    description_selectors = [
        "//div[@id='productDescription']/p/span/text()",  # Original selector
        # You can add more selectors here as fallbacks or alternatives
    ]

    # Use the updated safe_extract function with a list of selectors
    return safe_extract(response, description_selectors, query_type='xpath', extract_first=True, default_value='')


def get_product_title(response):
    # Define a list of CSS selectors to try for extracting the product title
    title_selectors = [
        'span#productTitle::text',  # Original selector
        # Additional selectors can be added here as necessary
    ]

    # Use the updated safe_extract function with a list of selectors
    return safe_extract(response, title_selectors, query_type='css', extract_first=True, default_value='')


def get_price(response):
    # Define a list of CSS selectors to try for extracting the price
    price_selectors = [
        'span.a-price span[aria-hidden="true"]::text',  # Original selector
        'span.aok-offscreen::text',  # Alternative selector
    ]

    # Use the updated safe_extract function with a list of selectors
    price_str = safe_extract(response, price_selectors, query_type='css', extract_first=True, default_value='0')

    try:
        # Attempt to convert the extracted price string to a float after cleaning
        return float(price_str.replace('$', '').replace(',', '').strip())
    except ValueError:
        # Log an error message if the conversion fails
        logging.error(f"Failed to convert price '{price_str}' to float.")
        return 0.0


def get_features(response):
    # Define a list of XPath selectors to try for extracting the features list
    features_selectors = [
        "//div[@id='feature-bullets']//li/span[@class='a-list-item']/text()",  # Original selector
        # Additional selectors can be added here as fallbacks or alternatives
    ]

    # Use the updated safe_extract function with a list of selectors
    features = safe_extract(response, features_selectors, query_type='xpath', extract_first=False, default_value=[])

    # Filter out any empty or whitespace-only strings from the extracted features list
    return [feature.strip() for feature in features if feature.strip()]


def get_reviews(response, product_reviews):
    reviews_selector = 'div[data-hook="review"]'
    reviews = response.css(reviews_selector)

    # Define variables for each selector
    rating_selectors = ['i[data-hook="review-star-rating"] > span::text']
    date_selectors = ['span[data-hook="review-date"]::text']
    text_selectors = ['string(.//span[@data-hook="review-body"]//span)']
    author_selectors = ['span.a-profile-name::text']
    collapsed_text_selectors = ['div[data-hook="review-collapsed"] > span::text']

    for review in reviews:
        review_data = {
            'rating': safe_extract(review, rating_selectors, query_type='css', default_value='0'),
            'date': safe_extract(review, date_selectors, query_type='css', default_value='No Date'),
            'text': safe_extract(review, text_selectors, query_type='xpath', default_value='No Review Text'),
            'author': safe_extract(review, author_selectors, query_type='css', default_value='Anonymous'),
        }

        # Attempt to extract review text using an alternative selector if the first attempt returned 'No Review Text'
        if review_data['text'] == 'No Review Text':
            review_data['text'] = safe_extract(review, collapsed_text_selectors, query_type='css',
                                               default_value='No Review Text'),

        # Convert rating to float and handle conversion failure
        try:
            review_data['rating'] = float(review_data['rating'].split(' out of')[0].strip())
        except ValueError:
            logging.error(f"Failed to convert rating '{review_data['rating']}' to float.")
            review_data['rating'] = 0.0

        # Check if the author already exists in the list of reviews to avoid duplicates
        if not any(existing_review['author'] == review_data['author'] for existing_review in product_reviews):
            product_reviews.append(review_data)

    return product_reviews


def extract_asin_from_url(url):
    # Define the regular expression pattern to match an ASIN in the Amazon product URL
    pattern = r'/dp/([A-Z0-9]{10})'

    # Use the re.search() method to find the first occurrence of the pattern
    match = re.search(pattern, url)

    # If a match is found, return the first capturing group (ASIN), otherwise return None
    return match.group(1) if match else None


def get_number_of_reviews(response):
    # First, define the selector for the parent div to narrow down the search scope
    parent_div_selector = 'div#averageCustomerReviews'

    # Define the selector for the span that contains the number of reviews
    number_of_reviews_selectors = ['span#acrCustomerReviewText::text']

    # Use the parent div selector to narrow down the search, and then apply safe_extract with the reviews selector
    parent_div = response.css(parent_div_selector)
    number_of_reviews = safe_extract(parent_div, number_of_reviews_selectors, query_type='css', extract_first=True,
                                     default_value='').strip()

    return number_of_reviews


def get_product_variants(response):
    variants = {}

    # First, select the form that contains variant information
    form_selector = "form#twister"  # Adjust this selector to target the specific form if needed
    form = response.css(form_selector)

    # Then, within this form, look for variant sections such as "Capacity" or "Color"
    variant_sections = form.xpath(".//div[contains(@class, 'a-section') and contains(@class, 'a-spacing-small')]")

    for section in variant_sections:
        # Use safe_extract to get the variant title from each section
        title_selectors = [".//label[@class='a-form-label']/text()"]
        title = safe_extract(section, title_selectors, query_type='xpath', extract_first=True, default_value='').strip()

        if not title:  # Skip sections without a clear title
            continue
        if "\\n" in title:
            title = title.replace("\\n", "").strip()

        variant_options = []

        # Iterate over each option within the current variant section
        option_selectors = [".//li[contains(@class, 'swatchAvailable') or contains(@class, 'swatchSelect')]"]
        for option in section.xpath(option_selectors[0]):
            option_info = {}

            # Use safe_extract to get the option name
            option_name_selectors = ["@title", ".//span/text()"]
            option_name = safe_extract(option, option_name_selectors, query_type='xpath', extract_first=True,
                                       default_value='').strip()
            if "Click to select" in option_name:
                option_name = option_name.replace("Click to select", "").strip()
            option_info['name'] = option_name

            # Use safe_extract to check for and get a color image, if present
            color_image_selectors = [".//img/@src"]
            color_image = safe_extract(option, color_image_selectors, query_type='xpath', extract_first=True,
                                       default_value=None)
            if color_image:
                option_info['color'] = option_name  # Assuming the title or text content represents the color name
                option_info['image'] = color_image

            variant_options.append(option_info)

        # Assign the list of options to the corresponding title in the variants dictionary
        variants[title] = variant_options

    return variants


def get_similar_products(product_asin, response):
    first_row_selector = '._product-comparison-desktop_desktopFaceoutStyle_asin__2eMLv'
    second_row_selector = '._product-comparison-desktop_desktopFaceoutStyle_tableAttribute__2V-c2 > span.a-price'

    first_row = response.css(first_row_selector)
    second_row = response.css(second_row_selector)

    title_selectors = ['img::attr(alt)']
    image_selectors = ['img::attr(src)']
    price_selectors = ['span.a-offscreen::text']

    products = []
    for prod in first_row:
        asin = prod.css('div.a-image-container::attr(id)').re_first(r'B0[A-Z0-9]+')
        product = {
            'title': safe_extract(prod, title_selectors, query_type='css', extract_first=True, default_value=''),
            'image': safe_extract(prod, image_selectors, query_type='css', extract_first=True, default_value=''),
            'asin': asin,
            'url': f'https://www.amazon.com/dp/{asin}'
        }
        products.append(product)

    prices = []
    for prod in second_row:
        prices.append(safe_extract(prod, price_selectors, query_type='css', extract_first=True, default_value=''))

    # Ensure the lengths of products and prices match by removing excess products
    if len(prices) != len(products):
        while len(prices) != len(products):
            products.pop(0)

    # Assign prices to products
    for i, prod in enumerate(products):
        prod['price'] = prices[i]

    # Remove the product that matches the input ASIN
    products = [prod for prod in products if prod['asin'] != product_asin]

    return products


class AmazonSpider(scrapy.Spider):
    name = 'amazon'

    def __init__(self, url=None, job_id=None, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.job = {}
        if not url or not job_id:
            logging.error("URL and Job ID are required")
            raise ValueError("URL and Job ID are required")
        self.start_urls = [url]  # This should be the URL you intend to scrape
        self.job_id = job_id
        self.critical_reviews = []
        self.positive_reviews = []
        self.default_reviews = []
        self.requests_completed = 0
        self.requests_needed = 4
        self.product = {}
        self.qa = []
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

    def start_requests(self):
        for url in self.start_urls:
            domain = url.split('/')[2]
            product_id = extract_asin_from_url(url)
            critical_reviews_url = f"https://{domain}/product-reviews/{product_id}/?filterByStar=critical&reviewerType=avp_only_reviews"
            positive_reviews_url = f"https://{domain}/product-reviews/{product_id}/?filterByStar=positive&reviewerType=avp_only_reviews"
            qa_url = f"https://{domain}/ask/questions/asin/{product_id}"
            yield scrapy.Request(qa_url, callback=self.extract_questions_and_answers, meta={'proxy': self.proxy})
            yield scrapy.Request(url, callback=self.parse, meta={'proxy': self.proxy})
            yield scrapy.Request(critical_reviews_url, callback=self.parse_critical_reviews,
                                 meta={'proxy': self.proxy})
            yield scrapy.Request(positive_reviews_url, callback=self.parse_positive_reviews,
                                 meta={'proxy': self.proxy})

    def generate_job(self) -> dict or None:
        if self.requests_completed != self.requests_needed:
            return
        reviews = self.critical_reviews
        for review in self.positive_reviews:
            if review['author'] not in [r['author'] for r in reviews]:
                reviews.append(review)
        for review in self.default_reviews:
            if review['author'] not in [r['author'] for r in reviews]:
                reviews.append(review)
        qa = self.qa
        product = {
            "product_id": self.product['product_id'],
            "job_id": self.job_id,
            "domain": self.product['domain'],
            "title": self.product['title'],
            "description": self.product['description'],
            "price": self.product['price'],
            "image_url": self.product['image_url'],
            "specs": self.product['specs'],
            "features": self.product['features'],
            "rating": self.product['rating'],
            "reviews": reviews,
            "created_at": self.product['created_at'],
            "updated_at": self.product['updated_at'],
            "similar_products": self.product['similar_products'],
            "variants": self.product['variants'],
            "number_of_reviews": self.product['number_of_reviews'],
            "qa": qa,
            "generated_review": ''
        }

        # merge all the reviews check the author to avoid duplicates


        job = {
            "job_id": self.job_id,
            "status": "completed",
            "end_time": datetime.datetime.utcnow().isoformat(),
            "start_time": datetime.datetime.utcnow().isoformat(),
            "result": product,
            "url": self.start_urls[0],
            "error": {}
        }
        return job

    def close_job(self, response):
        # Logic to handle the response and close the job
        self.close(self, reason="Job completed successfully")

    def parse(self, response):
        self.product = {
            "product_id": extract_asin_from_url(response.url),
            "job_id": self.job_id,
            "domain": response.url.split('/')[2],
            "title": get_product_title(response),
            "description": get_product_description(response),
            "price": get_price(response),
            "image_url": get_image_url(response),
            "specs": get_product_specs(response),
            "features": get_features(response),
            "rating": get_rating(response),
            "number_of_reviews": get_number_of_reviews(response),
            "created_at": datetime.datetime.utcnow().isoformat(),
            "updated_at": datetime.datetime.utcnow().isoformat(),
            "variants": get_product_variants(response),
            "generated_review": '',
        }
        similar_products = get_similar_products(self.product["product_id"], response)
        self.product['similar_products'] = similar_products
        self.default_reviews = get_reviews(response, [])
        self.requests_completed += 1
        if self.requests_completed == self.requests_needed:
            job = self.generate_job()
            data = json.dumps(job, default=datetime_serializer)
            endpoint = os.getenv("SERVICE_URL")
            yield scrapy.Request(url=endpoint + "/api/v1/scrapy/update", callback=self.close_job, body=data, method='POST')

    def parse_critical_reviews(self, response):
        critical_reviews = get_reviews(response, [])
        self.critical_reviews = critical_reviews
        self.requests_completed += 1
        if self.requests_completed == self.requests_needed:
            job = self.generate_job()
            data = json.dumps(job, default=datetime_serializer)
            endpoint = os.getenv("SERVICE_URL")
            yield scrapy.Request(url=endpoint + "/api/v1/scrapy/update", callback=self.close_job, body=data, method='POST')

    def parse_positive_reviews(self, response):
        positive_reviews = get_reviews(response, [])
        self.positive_reviews = positive_reviews
        self.requests_completed += 1
        if self.requests_completed == self.requests_needed:
            job = self.generate_job()
            data = json.dumps(job, default=datetime_serializer)
            endpoint = os.getenv("SERVICE_URL")
            yield scrapy.Request(url=endpoint + "/api/v1/scrapy/update", callback=self.close_job, body=data, method='POST')

    def extract_questions_and_answers(self, response):
        qa_pairs = []

        # Select elements with an id containing 'question'
        question_elements = response.xpath("//*[contains(@id, 'question')]")

        for question_element in question_elements:
            # Using safe_extract to get the question text
            question_selectors = ['div > div > a > span::text']
            question_text = safe_extract(question_element, question_selectors, query_type='css', extract_first=True,
                                         default_value='')
            if question_text:
                question_text = question_text.replace('\\n', '').strip()

            # Finding the sibling div that likely contains the answer
            sibling_div = question_element.xpath("following-sibling::div")

            # Using safe_extract to get potential answer texts, then choosing the second one if available
            answer_selectors = ["div > span::text"]
            answer_texts = safe_extract(sibling_div, answer_selectors, query_type='css', extract_first=False,
                                        default_value=[])

            answer_text = answer_texts[1] if len(answer_texts) > 1 else ''
            if answer_text:
                answer_text = answer_text.replace('\\n', '').strip()

            if question_text and answer_text:
                qa_pairs.append({'question': question_text, 'answer': answer_text})
                answer_text = ''
                question_text = ''

        self.qa = qa_pairs
        self.requests_completed += 1
        if self.requests_completed == self.requests_needed:
            job = self.generate_job()
            data = json.dumps(job, default=datetime_serializer)
            endpoint = os.getenv("SERVICE_URL")
            yield scrapy.Request(url=endpoint + "/api/v1/scrapy/update", callback=self.close_job, body=data, method='POST')
