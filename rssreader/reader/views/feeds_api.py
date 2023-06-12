from uuid import UUID
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from knox.auth import TokenAuthentication
from drf_spectacular.utils import extend_schema
from reader.repositories import FeedsRepository
from reader.utils.feed_parser import FeedParser
from reader.services import FeedsService
from reader.serializers import (
    FeedSerializer,
    PaginatedFeedsSerializer,
    FollowFeedRequestBodySerializer,
    UnreadOnlyQueryParamSerializer,
    PaginationQueryParamsSerializer,
)


class FeedsApi(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]

    feeds_repo = FeedsRepository()
    parser = FeedParser()
    feeds_service = FeedsService(feeds_repo, parser)

    @extend_schema(
        request=FollowFeedRequestBodySerializer,
        responses={201: FeedSerializer},
        operation_id='Follow feed'
    )
    def create(self, request):
        user = request.user

        req_serializer = FollowFeedRequestBodySerializer(data=request.data)
        if not req_serializer.is_valid():
            raise ValidationError(detail=req_serializer.errors)

        url = req_serializer.validated_data['url']

        feed = self.feeds_service.follow_feed(user.id, url)

        res_serializer = FeedSerializer(feed)
        return Response(res_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        responses={200: FeedSerializer},
        operation_id='Refresh feed'
    )
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk: UUID):
        user = request.user
        feed = self.feeds_service.refresh_user_feed(user.id, pk)

        return Response(FeedSerializer(feed).data)

    @extend_schema(
        responses={200: FeedSerializer},
        parameters=[UnreadOnlyQueryParamSerializer],
        operation_id='Get feed'
    )
    def retrieve(self, request, pk: UUID):
        user = request.user

        query_serializer = UnreadOnlyQueryParamSerializer(
            data=request.query_params
        )
        if not query_serializer.is_valid():
            raise ValidationError(detail=query_serializer.errors)
        
        unread_only = query_serializer.validated_data['unread_only']

        feed = self.feeds_service.get_user_feed_by_id(user.id, pk, unread_only)
        
        return Response(FeedSerializer(feed).data)

    @extend_schema(
        responses={200: PaginatedFeedsSerializer},
        parameters=[PaginationQueryParamsSerializer],
        operation_id='List feeds'
    )
    def list(self, request):
        user = request.user

        query_serializer = PaginationQueryParamsSerializer(
            data=request.query_params
        )
        if not query_serializer.is_valid():
            raise ValidationError(detail=query_serializer.errors)
        
        page = query_serializer.validated_data['page']
        page_size = query_serializer.validated_data['page_size']
        
        feeds, feed_count = self.feeds_service.get_user_feeds(
            user.id, page, page_size
        )
        
        return Response(PaginatedFeedsSerializer({
                'count': feed_count,
                'results': feeds
            }).data)

    @extend_schema(
        operation_id='Unfollow feed'
    ) 
    def destroy(self, request, pk: UUID):
        user = request.user
        self.feeds_service.unfollow_feed(user.id, pk)
        return Response()
