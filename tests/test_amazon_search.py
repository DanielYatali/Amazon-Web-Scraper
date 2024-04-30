import json
import os
import pytest
from scrapy.http import Response, Request, TextResponse
import cProfile
import pstats

from default.spiders.amazon_search import parse_products


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


@pytest.mark.parametrize('html_file', get_all_html_files('fixtures/search_pages'))
# @pytest.mark.parametrize('html_file', get_all_html_files(single_file='fixtures/search_pages/test1.html'))
def test_parse_products(html_file):
    """
    Tests that get_product_title does not return an empty string for any product page.
    """
    response = mock_response(html_file)
    products = parse_products(response)
    assert len(products) > 0, f"Failed to extract products from {html_file}"
    print(json.dumps(products, indent=4))

