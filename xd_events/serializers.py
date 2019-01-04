from rest_framework import serializers
from xd_events.models import Event


class EventSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field='name', read_only=True)
    entity_content_type = serializers.SlugRelatedField(slug_field='model', read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'created_at', 'type', 'entity_content_type', 'entity_object_id', 'user')
