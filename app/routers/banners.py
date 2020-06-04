import json
import uuid

from typing import List

from fastapi import APIRouter, Header
from starlette.responses import Response, HTMLResponse

from app.backend import BannersBackend
from app.backend.models import RequestContext, Banner
from app.backend.storage import get_banners_storage
from app.utils import JSONEncoder


router = APIRouter()


@router.get('/slots/{slot_id}/best/')
async def get_best_banner(
        slot_id: str,
        x_user_id: str = Header(None),
        x_request_id: str = Header(None),
        x_bs_language: str = Header(None),
        x_bs_country: str = Header(None),
        x_bs_segments: str = Header(None),
):
    context = RequestContext(
        user_id=x_user_id,
        request_id=x_request_id or str(uuid.uuid4()),
        language=x_bs_language,
        country=x_bs_country,
        segments=(x_bs_segments or '').split(','),
    )
    banners = BannersBackend(get_banners_storage(), context).\
        find_banners(slot_id)
    if len(banners) != 0:
        best_banner = banners[0]
        return HTMLResponse(
            best_banner.body,
            headers={
                'X-Bs-Dismissible': json.dumps(best_banner.dismissible),
                'X-Bs-Slot-Id': slot_id,
                'X-Bs-Banner-Id': best_banner.id,
                'X-Bs-Total-Banners': str(len(banners)),
            }
        )
    else:
        return HTMLResponse(status_code=204)


@router.get(
    '/slots/{slot_id}/all/',
    response_model=List[Banner],
)
async def get_banners(
        slot_id: str,
        x_user_id: str = Header(None),
        x_request_id: str = Header(None),
        x_bs_language: str = Header(None),
        x_bs_country: str = Header(None),
        x_bs_segments: str = Header(None),
):
    context = RequestContext(
        user_id=x_user_id,
        request_id=x_request_id or str(uuid.uuid4()),
        language=x_bs_language,
        country=x_bs_country,
        segments=(x_bs_segments or '').split(','),
    )
    banners = BannersBackend(get_banners_storage(), context).\
        find_banners(slot_id)
    return banners


@router.post(
    '/slots/{slot_id}/banners/{banner_id}/dismiss/',
)
async def dismiss_banner(
        slot_id: str, banner_id: str,
        x_user_id: str = Header(None),
        x_request_id: str = Header(None),
        x_bs_language: str = Header(None),
        x_bs_country: str = Header(None),
        x_bs_segments: str = Header(None),
):
    if x_user_id is None:
        return Response('X-User-Id header required', status_code=400)

    context = RequestContext(
        user_id=x_user_id,
        request_id=x_request_id or str(uuid.uuid4()),
        language=x_bs_language,
        country=x_bs_country,
        segments=(x_bs_segments or '').split(','),
    )
    is_dismissed = BannersBackend(get_banners_storage(), context).\
        dismiss_banner(slot_id, banner_id)
    if is_dismissed:
        return Response('Successfully dismissed')
    else:
        return Response('Could not dismiss banner', status_code=400)


@router.get('/debug/')
async def show_current_hierarchy():
    storage = get_banners_storage()
    return Response(
        'Last publish time: %s' % storage.last_publish_time +
        '\n\n' +
        'Last fetch time: %s' % storage.last_fetch_time +
        '\n\n' +
        'Last Publication ID: %s' % storage.last_publication_id +
        '\n\n' +
        json.dumps(
            storage.show_hierarchy(),
            cls=JSONEncoder,
            indent=4,
        ),
        media_type='text/plain',
    )


@router.get('/preview/{slot_id}/{banner_id}/')
async def preview_banner(
        slot_id: str,
        banner_id: str,
):
    dummy_context = RequestContext(
        request_id=str(uuid.uuid4()),
    )
    banner = BannersBackend(get_banners_storage(), dummy_context). \
        get_banner_preview(slot_id, banner_id)
    if banner is None:
        return HTMLResponse(status_code=204)
    else:
        return HTMLResponse(
            banner.body,
            headers={
                'X-Bs-Dismissible': json.dumps(banner.dismissible),
                'X-Bs-Slot': slot_id,
                'X-Bs-Banner-Id': banner.id,
            },
        )
