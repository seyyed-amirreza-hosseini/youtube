from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Video(models.Model):
    class Privacy(models.TextChoices):
        PUBLIC = 'public', _('Public')
        PRIVATE = 'private', _('Private')
        ULISTED = 'unlisted', _('Unlisted')

    class Status(models.TextChoices):
        PROCESSING = 'processing', _('Processing')
        PUBLISHED = 'published', _('Published')
        FAILED = 'failed', _('Failed')

    title = models.CharField(max_length=255)
    description = models.TextField()
    file_path = models.URLField()
    thumbnail = models.ImageField()
    duration = models.DurationField()
    views = models.IntegerField()
    uploaded_at = models.DateTimeField()
    privacy = models.CharField(max_length=8, choices=Privacy)
    status = models.CharField(max_length=10, choices=Status)


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