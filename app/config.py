from starlette.config import Config
from starlette.datastructures import Secret

config = Config("../.env")

DEBUG = config('DEBUG', cast=bool, default=False)
ALLOWED_ORIGINS = config(
    'ALLOWED_ORIGINS', default='*')
BSADMIN_BASE_URL = config(
    'BSADMIN_BASE_URL', default='http://host.docker.internal:8009/api/')
SECRET_KEY = config('SECRET_KEY', cast=Secret, default='test_secret')
LOCAL_PORT = config('LOCAL_PORT', default=8089)
SYNC_BANNERS_SECONDS = config('SYNC_BANNERS_SECONDS', default=10)
