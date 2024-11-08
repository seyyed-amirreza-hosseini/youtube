from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)


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
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    file_path = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/')
    duration = models.PositiveIntegerField(help_text='Duration in seconds')
    views = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    privacy = models.CharField(max_length=8, choices=Privacy)
    status = models.CharField(max_length=10, choices=Status)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='videos')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_videos', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_videos', blank=True)
    tags = models.ManyToManyField(Tag, related_name='videos', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def increment_views(self):
        self.views += 1
        self.save()
    
    def like(self, user):
        self.likes.add(user)
        self.dislikes.remove(user)

    def dislike(self, user):
        self.dislikes.add(user)
        self.likes.remove(user)


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Playlist(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)


class Subscription(models.Model):
    subscribed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscribers')
    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    created_at = models.DateTimeField(auto_now_add=True)

    
class Notification(models.Model):
    content = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)