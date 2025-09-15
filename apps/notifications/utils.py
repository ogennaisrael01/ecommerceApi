from apps.notifications.models import Notifications

def send_notification(user, message):
    if not user:
        return ({"success": False, "message": "No user was found to deviver this message to!"})
    Notifications.objects.create(owner=user, message=message)
    return ({"success": True, "message": "Notification sent"})    