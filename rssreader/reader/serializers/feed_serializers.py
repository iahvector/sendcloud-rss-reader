from rest_framework import serializers
from reader.serializers.item_serializers import FeedItemSerializer


class FeedListItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(format='hex_verbose')
    title = serializers.CharField(max_length=120, allow_blank=False)
    description = serializers.CharField(max_length=300, allow_blank=True)
    link = serializers.URLField(allow_blank=False)
    rss_link = serializers.URLField(allow_blank=False)
    publication_time = serializers.DateTimeField()
    update_time = serializers.DateTimeField()

    class Meta:
        read_only_fields = [
            'id', 'title', 'description', 'link', 'rss_link',
            'publication_time', 'update_time'
        ]


class FeedSerializer(FeedListItemSerializer):
    items = FeedItemSerializer(many=True, read_only=True)

    class Meta(FeedListItemSerializer.Meta):
        read_only_fields = FeedListItemSerializer.Meta.read_only_fields + \
            ['items']
