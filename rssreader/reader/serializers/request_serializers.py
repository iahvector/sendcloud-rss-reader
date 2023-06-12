from rest_framework import serializers
from reader.serializers import FeedListItemSerializer, ItemSerializer


class FollowFeedRequestBodySerializer(serializers.Serializer):
    url = serializers.URLField(required=True, allow_blank=False)


class MarkItemAsReadRequestBodySerializer(serializers.Serializer):
    is_read = serializers.BooleanField(required=True)


class UnreadOnlyQueryParamSerializer(serializers.Serializer):
    unread_only = serializers.BooleanField(required=False, default=False)


class PaginationQueryParamsSerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=0, default=0)
    page_size = serializers.IntegerField(
        min_value=1, max_value=100, default=100
    )


class ListItemsQueryParamsSerializer(
    UnreadOnlyQueryParamSerializer, PaginationQueryParamsSerializer
):
    pass


class PaginatedResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    class Meta:
        read_only_fields = ['count']

    
class PaginatedFeedsSerializer(PaginatedResponseSerializer):
    results = FeedListItemSerializer(many=True)

    class Meta(PaginatedResponseSerializer.Meta):
        read_only_fields = \
            PaginatedResponseSerializer.Meta.read_only_fields + ['results']

    
class PaginatedItemsSerializer(PaginatedResponseSerializer):
    results = ItemSerializer(many=True)

    class Meta(PaginatedResponseSerializer.Meta):
        read_only_fields = \
            PaginatedResponseSerializer.Meta.read_only_fields + ['results']