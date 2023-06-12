from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class Item:
    id: UUID
    guid: str
    title: str
    description: str
    link: str
    publication_time: datetime
    is_read: bool
    feed: UUID
    owner: UUID
