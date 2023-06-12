from uuid import UUID
from reader.repositories import ItemsRepository
from reader.domain_models import Item


class ItemsService:
    items_repo: ItemsRepository
    
    def __init__(self, items_repo: ItemsRepository):
        self.items_repo = items_repo

    def get_user_items(
        self,
        user_id: UUID,
        unread_items_only: bool = False,
        page: int = 0,
        page_size: int = 100
    ) -> tuple[list[Item], int]:
        offset = page * page_size
        return self.items_repo.get_all_user_items(
            user_id, unread_items_only, offset, page_size
        )
    
    def mark_item_as_read(
        self, user_id: UUID, item_id: UUID, is_read: bool
    ) -> Item:
        return self.items_repo.mark_user_item_as_read(user_id, item_id, is_read)