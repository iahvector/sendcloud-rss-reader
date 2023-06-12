from uuid import UUID
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from knox.auth import TokenAuthentication
from drf_spectacular.utils import extend_schema
from reader.repositories import ItemsRepository
from reader.services import ItemsService
from reader.serializers import (
    ItemSerializer,
    ListItemsQueryParamsSerializer,
    MarkItemAsReadRequestBodySerializer,
    PaginatedItemsSerializer
)


class ItemsApi(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]
    
    items_repo =  ItemsRepository()
    items_service = ItemsService(items_repo)

    @extend_schema(
        responses={200: PaginatedItemsSerializer},
        parameters=[ListItemsQueryParamsSerializer],
        operation_id='List items'
    )
    def list(self, request):
        user = request.user

        query_serializer = ListItemsQueryParamsSerializer(
            data=request.query_params
        )
        if not query_serializer.is_valid():
            raise ValidationError(detail=query_serializer.errors)
        
        unread_only = query_serializer.validated_data['unread_only']
        page = query_serializer.validated_data['page']
        page_size = query_serializer.validated_data['page_size']
        
        items, items_count = self.items_service.get_user_items(
            user.id, unread_only, page, page_size
        )
        return Response(PaginatedItemsSerializer({
                'count': items_count,
                'results': items
            }).data)

    @extend_schema(
        request=MarkItemAsReadRequestBodySerializer,
        responses={201: ItemSerializer},
        operation_id='Mark item as read'
    )
    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk: UUID):
        user = request.user
        req_serializer = MarkItemAsReadRequestBodySerializer(data=request.data)
        if not req_serializer.is_valid():
            raise ValidationError(detail=req_serializer.errors)
        
        is_read = req_serializer.validated_data['is_read']
        item = self.items_service.mark_item_as_read(user.id, pk, is_read)
        return Response(ItemSerializer(item).data)
