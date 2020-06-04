import requests_async

from urllib.parse import urljoin
from dateutil.parser import parse

from app.config import BSADMIN_BASE_URL
from .exceptions import InconsistentPublicationFetchError


async def fetch_banners_from_admin(last_published_at=None):
    url = urljoin(BSADMIN_BASE_URL, 'v1/banners/live/')
    response = await requests_async.get(url)
    response.raise_for_status()

    response_json = response.json()
    if not response_json:
        banners = []
        publication_id = None
        published_at = None
    else:
        banners = response_json['banners']
        publication_id = response_json['id']
        published_at = parse(response_json['published_at'])

        if last_published_at is None or last_published_at < published_at:
            # if we are interested in this Publication - fetch with pagination.
            while response_json and response_json['next'] is not None:
                response = await requests_async.get(response_json['next'])
                response.raise_for_status()
                response_json = response.json()
                if not response_json or response_json['id'] != publication_id:
                    raise InconsistentPublicationFetchError()
                banners.extend(response_json['banners'])

    return banners, publication_id, published_at
