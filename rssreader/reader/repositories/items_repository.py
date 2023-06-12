import logging
from uuid import UUID
from django.contrib.auth.models import User
from reader.domain_models import Item as ItemDM
from reader.models import Item
from reader.exceptions import ItemNotFoundExcpetion


logger = logging.getLogger(__name__)


class ItemsRepository:
    def get_all_user_items(
        self,
        user_id: UUID,
        unread_items_only: bool = False,
        offset: int = 0,
        limit: int = 100
    ) -> tuple[list[ItemDM], int]:
        items = Item.objects.filter(owner=User(id=user_id))
        if unread_items_only:
            items = items.filter(is_read=False)

        items_count = items.count()

        return (
            [i.to_domain_model() for i in items[offset:offset+limit]],
            items_count
        )

    def mark_user_item_as_read(
        self, user_id: UUID, item_id: UUID, is_read: bool
    ) -> ItemDM:
        try:
            item = Item.objects.get(id=item_id, owner=User(id=user_id))
        except Item.DoesNotExist as e:
            msg = f'Item {item_id} not found'
            raise ItemNotFoundExcpetion(msg)
        
        item.is_read = is_read
        item.save()
        
        return item.to_domain_model()
        
    def get_user_item(self, user_id: UUID, item_id: UUID) -> ItemDM:
        try:
            item = Item.objects.get(id=item_id, owner=User(id=user_id))
        except Item.DoesNotExist as e:
            msg = f'Item {item_id} not found'
            raise ItemNotFoundExcpetion(msg)
        
        return item.to_domain_model()
        
