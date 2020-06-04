import logging

from typing import Callable, List, Optional, Generator

from .storage import InMemoryBannersStorage
from .storage import get_dismissed_banners_storage
from .models import RequestContext, Banner
from . import rules


logger = logging.getLogger(__name__)


class PrefixAdapter(logging.LoggerAdapter):
    """ Used to provide custom prefix for logs """

    def process(self, msg, kwargs):
        return '[Request %s]: %s' % (
            self.extra['request_id'],
            msg,
        ), kwargs


class BannersBackend(object):
    rules = []
    transformations = []

    def __init__(self,
                 storage: InMemoryBannersStorage,
                 context: RequestContext,
                 ):
        self._storage = storage
        self.context = context
        self.logger = PrefixAdapter(
            logger,
            {'request_id': context.request_id},
        )

    def _get_banners(self, slot_id: str) -> List[Banner]:
        return self._storage.get_banners(slot_id)

    @classmethod
    def register_rule(cls, rule_func: Callable):
        cls.rules.append(rule_func)

    @classmethod
    def register_transformation(cls, transformation_func: Callable):
        cls.transformations.append(transformation_func)

    def apply_rules(
            self, banners: List[Banner]) -> Generator[Banner, None, None]:

        self.logger.info(
            'Applying %s rules to %s objects',
            len(self.rules), len(banners),
        )

        for banner in banners:
            self.logger.info('Applying rules to object: %s',  banner.id)
            for rule_func in self.rules:
                if not rule_func(banner, self.context):
                    self.logger.info(
                        'Rule %s failed for object: %s',
                        rule_func.__name__, banner.id
                    )
                    break
                else:
                    self.logger.info(
                        'Rule %s succeeded for object: %s',
                        rule_func.__name__, banner.id
                    )
            else:
                self.logger.info(
                    'Banner %s matching the request', banner.id,
                )
                yield banner

    def apply_transformations(self, banners:  List[Banner]) -> List[Banner]:
        self.logger.info(
            'Applying transformations for %s objects', len(banners),
        )
        for transformation_func in self.transformations:
            banners = transformation_func(banners, self.context)
        return list(banners)

    def _find_matches(self, banners: List[Banner]) -> List[Banner]:
        if len(banners) == 0:
            return []

        matching_banners = list(self.apply_rules(banners))
        return self.apply_transformations(matching_banners)

    def find_banners(self, slot_id: str) -> List[Banner]:
        banners = self._get_banners(slot_id)
        return self._find_matches(banners)

    def get_banner_preview(self, slot_id: str, banner_id: str) -> Optional[Banner]:
        """Force get banner, does not apply any rules or transformations."""
        banners = self._get_banners(slot_id)
        for banner in banners:
            if banner.id == banner_id:
                return banner

    def dismiss_banner(self, slot_id, banner_id):
        banner = self.get_banner_preview(slot_id, banner_id)
        if banner is None:
            return False

        storage = get_dismissed_banners_storage()
        storage.mark_dismissed(banner_id, self.context.user_id)
        return True


# Order of registration matters
# Checking for each banner
BannersBackend.register_rule(rules.check_not_stopped_yet)
BannersBackend.register_rule(rules.check_country_valid)
BannersBackend.register_rule(rules.check_start_time_end_time_valid)
BannersBackend.register_rule(rules.check_languages_valid)
BannersBackend.register_rule(rules.check_not_dismissed_yet)


# Transforming the final list of banners after filtering
BannersBackend.register_transformation(rules.order_by_priority)
