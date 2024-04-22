# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import asyncio
import json
import logging
from datetime import datetime
import aiohttp


def datetime_serializer(obj):
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class HttpPipeline(object):
    def __init__(self, endpoint_uri):
        self.endpoint_uri = endpoint_uri

    @classmethod
    def from_crawler(cls, crawler):
        return cls(endpoint_uri=crawler.settings.get('BASE_URL'))

    async def post_item(self, item):
        # Asynchronous POST request using aiohttp
        data = json.dumps(item, default=datetime_serializer)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint_uri + "/api/v1/scrapy/update", data=data,
                                        headers={"Content-Type": "application/json"}) as response:
                    if response.status != 200:
                        # You can adjust logging according to your needs
                        response_text = await response.text()
                        print(f"Failed to post item to endpoint: {response_text}")
                        logging.error(f"Failed to post item to endpoint")
        except Exception as e:
            logging.error(f"Failed to post item to endpoint: {e}")

    def process_item(self, item, spider):
        # Convert the item to a dict and schedule the post_item coroutine
        asyncio.create_task(self.post_item(dict(item)))
        return {"status": "ok"}
