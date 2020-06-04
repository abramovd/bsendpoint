import datetime
from typing import List

from .models import Banner, RequestContext
from .storage import get_dismissed_banners_storage


def check_country_valid(
        banner: Banner, context: RequestContext) -> bool:
    return bool(
        not banner.countries or
        context.country in banner.countries
    )


def check_start_time_end_time_valid(
        banner: Banner, context: RequestContext) -> bool:
    now = datetime.datetime.now(datetime.timezone.utc)
    too_early = banner.start_time is not None and now < banner.start_time
    too_late = banner.end_time is not None and now > banner.end_time
    return not (bool(too_early) or bool(too_late))


def check_languages_valid(
        banner: Banner, context: RequestContext) -> bool:
    return bool(
        not banner.languages or
        context.language in banner.languages
    )


def check_not_dismissed_yet(
        banner: Banner, context: RequestContext) -> bool:
    storage = get_dismissed_banners_storage()
    return bool(
        not banner.dismissible or
        not storage.is_dismissed_by(
            banner.id, context.user_id
        )
    )


def check_not_stopped_yet(
        banner: Banner, context: RequestContext) -> bool:
    return not banner.stopped


def check_segments_valid(
        banner: Banner, context: RequestContext) -> bool:
    return bool(
        not banner.segments,
    )


def order_by_priority(
        banners: List[Banner], context: RequestContext) -> List[Banner]:
    return sorted(banners, key=lambda b: b.priority, reverse=True)
