import datetime
import logging

from typing import List
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class Banner(BaseModel):
    id: str
    name: str
    priority: int

    body: str

    dismissible: bool
    stopped: bool
    languages: List[str]
    countries: List[str]
    start_time: datetime.datetime = None
    end_time: datetime.datetime = None

    segments: List[str]

    def __hash__(self):
        return self.id


class Slot(BaseModel):
    id: str
    name: str

    def __hash__(self):
        return self.id


class RequestContext(BaseModel):
    request_id: str
    user_id: str = None
    language: str = None
    country: str = None
    segments: List[str] = []
