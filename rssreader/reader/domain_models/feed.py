from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from .item import Item

@dataclass
class Feed:
    id: UUID
    title: str
    description: str
    link: str
    rss_link: str
    publication_time: datetime
    update_time: datetime
    is_automatic_update_enabled: bool
    items: list[Item] | None
    owner: int