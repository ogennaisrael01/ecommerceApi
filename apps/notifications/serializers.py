from rest_framework import serializers
from apps.notifications.models  import Notifications

class NotificationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.email")
    
    class Meta:
        model = Notifications
        fields = ["id", "owner", "message", "created_at", "is_read", "slug"]
    