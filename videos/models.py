from django.db import models, transaction
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Video(models.Model):
    class Privacy(models.TextChoices):
        PUBLIC = 'public', _('Public')
        PRIVATE = 'private', _('Private')
        UNLISTED = 'unlisted', _('Unlisted')

    class Status(models.TextChoices):
        PROCESSING = 'processing', _('Processing')
        PUBLISHED = 'published', _('Published')
        FAILED = 'failed', _('Failed')

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    file_path = models.FileField(upload_to='videos_uploaded/')
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
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def increment_views(self):
        self.views += 1
        self.save()
    
    def like(self, user):
        with transaction.atomic():
            if not self.likes.filter(id=user.id).exists():
                self.likes.add(user)
                self.like_count += 1
                if self.dislikes.filter(id=user.id).exists():
                    self.dislikes.remove(user)
                    self.dislike_count -= 1
            else:
                self.likes.remove(user)
                self.like_count -= 1

            self.save()    

    def dislike(self, user):
        with transaction.atomic():
            if not self.dislikes.filter(id=user.id).exists():
                self.dislikes.add(user)
                self.dislike_count += 1
                if self.likes.filter(id=user.id).exists():
                    self.likes.remove(user)
                    self.like_count -= 1
            else:
                self.dislikes.remove(user)
                self.dislike_count -= 1

            self.save()

    def __str__(self):
        return self.title        


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_comments', blank=True)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    report_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)

    def edit_comment(self, new_comment):
        self.content = new_comment
        self.save()

    def delete_comment(self):
        self.is_active = False
        self.save() 

    def like(self, user):
        with transaction.atomic():
            if not self.likes.filter(id=user.id).exists():
                self.likes.add(user)
                self.like_count += 1
                if self.dislikes.filter(id=user.id).exists():
                    self.dislikes.remove(user)
                    self.dislike_count -= 1
            else:
                self.likes.remove(user)
                self.like_count -= 1

            self.save()

    def dislike(self, user):
        with transaction.atomic():
            if not self.dislikes.filter(id=user.id).exists():
                self.dislikes.add(user)
                self.dislike_count += 1
                if self.likes.filter(id=user.id).exists():
                    self.likes.remove(user)
                    self.like_count -= 1
            else:
                self.dislikes.remove(user)
                self.dislike_count -= 1

            self.save()

    def count_report(self):
        self.report_count += 1
        self.save()

    def get_all_replies(self):
        all_replies = []
        replies = Comment.objects.filter(parent=self)
        for reply in replies:
            all_replies.append(reply.id)

        return all_replies

    def __str__(self):
        return f"Comment by {self.user.username} on {self.video.title}: {self.content[:50]}"


class Playlist(models.Model):
    class Privacy(models.TextChoices):
        PUBLIC = 'public', _('Public')
        PRIVATE = 'private', _('Private')
        UNLISTED = 'unlisted', _('Unlisted')

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    privacy = models.CharField(max_length=8, choices=Privacy)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='playlists')
    videos = models.ManyToManyField(Video, related_name='playlists', blank=True)

    def add_video(self, video):
        self.videos.add(video)

    def remove_video(self, video):
        self.videos.remove(video)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Subscription(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscribers') 
    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['creator', 'subscriber'], name='unique_creator_subscriber')
        ]

    
class Notification(models.Model):
    content = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)