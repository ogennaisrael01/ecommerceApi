from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from apps.notifications.models import Notifications
from apps.notifications.serializers import NotificationSerializer
from rest_framework.response import Response

class NotificationViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                             mixins.RetrieveModelMixin):
    
    serializer_class = NotificationSerializer
    queryset = Notifications.objects.all()
    lookup_field = "slug"

    def list(self, request, *args, **kwargs):
        """ A queryset to list all notication where the owner is the loggged in user"""

        queryset = self.filter_queryset(super().get_queryset())
        notifications = queryset.filter(owner=request.user)[:10]
        if not notifications.exists():
            return Response({
                "success":False,
                "message": "No Notifications found"
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(notifications)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrive a single notification object and mark as read """
        object = self.get_object()

        if object.owner == request.user:
            queryset = self.filter_queryset(super().get_queryset())
            object.is_read = True
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)
