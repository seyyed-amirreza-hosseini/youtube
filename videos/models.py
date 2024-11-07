from django.db import models
from django.conf import settings


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Playlist(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Subscription(models.Model):
    subscribed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscribers')
    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    created_at = models.DateTimeField(auto_now_add=True)

    
class Notification(models.Model):
    content = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)