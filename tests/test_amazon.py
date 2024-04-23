# test_spider.py
import json
import os
import pytest
from scrapy.http import Response, Request, TextResponse
import cProfile
import pstats

# Import the spider functions you want to test
from default.spiders.amazon import get_product_title, extract_table_data, extract_product_details, get_product_specs, \
    get_rating, get_image_url, get_product_description, get_features, get_price, get_reviews, get_number_of_reviews, \
    get_product_variants, get_similar_products, get_stock


def mock_response(file_name, url='http://example.com'):
    """
    Create a Scrapy fake response from a HTML file
    :param file_name: The relative filename from the tests directory,
                      e.g., 'html_files/some_page.html'
    :param url: The URL of the response.
    :returns: A Scrapy HTTP response which can be used for unit testing.
    """
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    request = Request(url=url)
    response = TextResponse(url=url, request=request, body=file_content, encoding='utf-8')
    return response


def get_all_html_files(directory=None, single_file=None):
    """
    Retrieves a list of HTML file paths from the given directory.
    """
    if single_file:
        return [os.path.join(os.path.dirname(__file__), single_file)]
    dir_path = os.path.join(os.path.dirname(__file__), directory)
    return [os.path.join(directory, file) for file in os.listdir(dir_path) if file.endswith('.html')]


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
def test_get_product_title(html_file):
    """
    Tests that get_product_title does not return an empty string for any product page.
    """
    response = mock_response(html_file)
    title = get_product_title(response)
    assert title != '', f"Failed to extract title from {html_file}"
    print(title)


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
# @pytest.mark.parametrize('html_file', get_all_html_files(single_file='fixtures/product_pages/test1.html'))
def test_extract_table_data(html_file):
    """
    Tests that extract_table_data does not return an empty string for any product page.
    """
    response = mock_response(html_file)
    table_data = extract_table_data(response, "//table[@id='productDetails_detailBullets_sections1']")
    assert table_data != '', f"Failed to extract table data from {html_file}"
    print(table_data)


@pytest.mark.parametrize('html_file', get_all_html_files(single_file='fixtures/product_pages/test2.html'))
def test_extract_product_details(html_file):
    """
    Tests that extract_table_data does not return an empty string for any product page.
    """
    response = mock_response(html_file)
    table_data = extract_product_details(response)
    assert table_data != '', f"Failed to extract table data from {html_file}"
    print(table_data)


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
# @pytest.mark.parametrize('html_file', get_all_html_files(single_file='fixtures/product_pages/test2.html'))
def test_get_product_specs(html_file):
    """
    Tests that get_product_specs does not return an empty string for any product page.
    """
    response = mock_response(html_file)
    specs = get_product_specs(response)
    assert specs != '', f"Failed to extract specs from {html_file}"
    # print the json fomatted specs
    print(json.dumps(specs, indent=4))


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
def test_get_rating(html_file):
    """
    Tests that get_rating does not return an empty string for any product page.
    """
    response = mock_response(html_file)
    rating = get_rating(response)
    assert rating != '', f"Failed to extract rating from {html_file}"
    print(rating)


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
def test_get_image_url(html_file):
    """
    Tests that get_image_url does not return an empty string for any product page.
    """
    response = mock_response(html_file)
    image_url = get_image_url(response)
    assert image_url != '', f"Failed to extract image url from {html_file}"
    print(image_url)


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
def test_get_product_description(html_file):
    """
    Tests that get_product_description does not return an empty string for any product page.
    """
    response = mock_response(html_file)
    description = get_product_description(response)
    assert description != '', f"Failed to extract description from {html_file}"
    print(json.dumps(description, indent=4))


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
def test_get_features(html_file):
    """
    Tests that get_product_description does not return an empty string for any product page.
    """
    response = mock_response(html_file)
    description = get_features(response)
    assert description != '', f"Failed to extract description from {html_file}"
    print(description)


# @pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
@pytest.mark.parametrize('html_file', get_all_html_files(single_file='fixtures/product_pages/test1.html'))
def test_get_product_title(html_file):
    """
    Tests that get_product_title does not return an empty string for any product page.
    """
    response = mock_response(html_file)
    profiler = cProfile.Profile()
    profiler.enable()
    get_product_title(response.selector)
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()

    # title = get_product_title(response)
    # assert title != '', f"Failed to extract title from {html_file}"
    # print(title)


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
# @pytest.mark.parametrize('html_file', get_all_html_files(single_file='fixtures/product_pages/test4.html'))
def test_get_price(html_file):
    """
    Tests that get_price does not return an empty string for any product page.
    :param html_file:
    :return:
    """
    response = mock_response(html_file)
    price, discount = get_price(response)
    assert price != 0.0, f"Failed to extract price from {html_file}"
    assert discount != '', f"Failed to extract discount from {html_file}"
    print(price, discount)


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
def test_get_reviews(html_file):
    """
    Tests that get_reviews does not return an empty string for any product page.
    :param html_file:
    :return:
    """
    response = mock_response(html_file)
    reviews = get_reviews(response, [])
    assert reviews != [], f"Failed to extract reviews from {html_file}"
    print(json.dumps(reviews, indent=4))


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
def test_get_number_of_reviews(html_file):
    """
    Tests that get_number_of_reviews does not return an empty string for any product page.
    :param html_file:
    :return:
    """
    response = mock_response(html_file)
    reviews = get_number_of_reviews(response)
    assert reviews != '', f"Failed to extract reviews from {html_file}"
    print(reviews)


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
def test_get_product_variants(html_file):
    """
    Tests that get_product_variants does not return an empty string for any product page.
    :param html_file:
    :return:
    """
    response = mock_response(html_file)
    variants = get_product_variants(response)
    assert variants != '', f"Failed to extract variants from {html_file}"
    print(json.dumps(variants, indent=4))


# can be optimized
@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
def test_get_similar_products(html_file):
    """
    Tests that get_similar_products does not return an empty string for any product page.
    :param html_file:
    :return:
    """
    response = mock_response(html_file)
    similar_products = get_similar_products('1234', response)
    assert similar_products != [], f"Failed to extract similar products from {html_file}"
    print(json.dumps(similar_products, indent=4))

@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/product_pages'))
def test_get_stock_status(html_file):
    """
    Tests that get_stock_status does not return an empty string for any product page.
    :param html_file:
    :return:
    """
    response = mock_response(html_file)
    stock_status = get_stock(response)
    assert stock_status != '', f"Failed to extract stock status from {html_file}"
    print(stock_status)