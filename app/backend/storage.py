import datetime
import logging

from typing import List
from collections import defaultdict

from .models import Banner, Slot
from .fetcher import fetch_banners_from_admin
from .exceptions import InconsistentPublicationFetchError


logger = logging.getLogger(__name__)


class InMemoryBannersStorage(object):

    def __init__(self):
        self._last_publication_id = None
        self._banners_hierarchy = {}
        self._last_publish_time = None
        self._last_fetch_time = None
        self._last_publication_id = None

    @property
    def last_publish_time(self):
        return self._last_publish_time

    @property
    def last_publication_id(self):
        return self._last_publication_id

    @property
    def last_fetch_time(self):
        return self._last_fetch_time

    def _update_hierarchy(self, hierarchy):
        logger.info('Updating hierarchy')
        self._banners_hierarchy = hierarchy

    def _update_last_publish_time(self, publication_id, publish_time):
        logger.info('Updating last publish time to %s', publish_time)
        self._last_publication_id = publication_id
        self._last_publish_time = publish_time

    def _update_last_fetch_time(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        logger.info('Updating last fetch time to %s', now)
        self._last_fetch_time = now

    def _build_hierarchy(self, banners_json):
        """{slot: [banner1, banner2]}"""
        logger.info('Building new banners hierarchy')
        hierarchy = defaultdict(list)
        for banner in banners_json:
            slot = banner.pop('slot')
            slot = Slot(**slot)
            banner = Banner(**banner)

            hierarchy[slot.id].append(banner)

        logger.info('Built new banners hierarchy')
        return hierarchy

    async def sync_banners(self):
        try:
            banners_json, publication_id, published_at = \
                await fetch_banners_from_admin(self.last_publish_time)
        except InconsistentPublicationFetchError:
            logger.info('Publication changed during paginated fetch. Skipping.')
            return

        if (
                self.last_publish_time is not None and
                published_at is not None and
                self.last_publish_time >= published_at
        ):
            logger.info('No new publishes. Skipping.')
        else:
            hierarchy = self._build_hierarchy(banners_json)
            self._update_hierarchy(hierarchy)
            self._update_last_publish_time(publication_id, published_at)
        self._update_last_fetch_time()

    def get_banners(self, slot_id: str) -> List[Banner]:
        banners = self._banners_hierarchy.get(slot_id, [])
        return banners

    def show_hierarchy(self):
        result = {
            slot_id: [
                banner.dict()
                for banner in banners
            ]
            for slot_id, banners in self._banners_hierarchy.items()
        }
        return result


class InMemoryDismissedBannerStorage(object):
    def __init__(self):
        self._data = defaultdict(list)

    def is_dismissed_by(self, banner_id, user_id):
        return banner_id in self._data.get(user_id, [])

    def mark_dismissed(self, banner_id, user_id):
        self._data[user_id].append(banner_id)


_dismissed_banners_storage = None
_banners_storage = None


def initialize_storage():
    global _banners_storage, _dismissed_banners_storage
    _banners_storage = InMemoryBannersStorage()
    _dismissed_banners_storage = InMemoryDismissedBannerStorage()
    logger.info('Storage Initialized')


def get_banners_storage():
    if _banners_storage is None:
        raise RuntimeError('Banners storage is not initialized')
    return _banners_storage


def get_dismissed_banners_storage():
    if _dismissed_banners_storage is None:
        raise RuntimeError('Dismissed Banners storage is not initialized')
    return _dismissed_banners_storage
