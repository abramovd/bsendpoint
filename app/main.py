import logging
import uvicorn
import asyncio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.config import (
    DEBUG, LOCAL_PORT, SYNC_BANNERS_SECONDS,
    ALLOWED_ORIGINS,
)
from app.backend.storage import initialize_storage, get_banners_storage

from .routers import banners

app = FastAPI(
    title='bsendpoint',
    description='bsendpoint app.',
    version='0.01'
)
app.add_middleware(
    CORSMiddleware, allow_methods=['OPTIONS', 'GET', 'POST'],
    allow_origins=ALLOWED_ORIGINS.split(','), allow_headers=['*'],
    expose_headers=[
        'X-Bs-Dismissible', 'X-Bs-Slot-Id', 'X-Bs-Banner-Id',
        'X-Bs-Total-Banners',
    ]
)
app.debug = DEBUG
app.include_router(
    banners.router,
    prefix='/banners'
)


logger = logging.getLogger(__name__)


async def sync_banners_periodic(every):
    """Syncing banners periodically to inmemory storage"""
    while True:
        logger.info('Running periodic task')
        try:
            await get_banners_storage().sync_banners()
        except Exception:
            logger.exception('Error syncing banners')
        else:
            logger.info('Successfully synced banners')
        await asyncio.sleep(every)


@app.on_event("startup")
async def startup_event():
    initialize_storage()
    loop = asyncio.get_event_loop()
    loop.create_task(sync_banners_periodic(every=SYNC_BANNERS_SECONDS))


@app.get('/health_check')
def health_check():
    if get_banners_storage().last_fetch_time is None:
        message = 'Not ready yet'
        status_code = 503
    else:
        message = 'All good'
        status_code = 200
    return Response(message, status_code=status_code, media_type='text/plain')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=LOCAL_PORT)
