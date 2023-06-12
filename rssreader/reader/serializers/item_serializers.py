from rest_framework import serializers


class FeedItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(format='hex_verbose')
    guid = serializers.CharField(max_length=60, allow_blank=False)
    title = serializers.CharField(max_length=120, allow_blank=False)
    description = serializers.CharField(max_length=300, allow_blank=True)
    link = serializers.URLField(allow_blank=False)
    publication_time = serializers.DateTimeField()
    is_read = serializers.BooleanField()

    class Meta:
        read_only_fields = [
            'id', 'guid', 'title', 'description', 'link', 'publication_time',
            'is_read'
        ]

class ItemSerializer(FeedItemSerializer):
    feed = serializers.UUIDField(format='hex_verbose')

    class Meta(FeedItemSerializer.Meta):
        read_only_fields = FeedItemSerializer.Meta.read_only_fields + ['feed']
