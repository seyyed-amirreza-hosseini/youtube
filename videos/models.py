from django.db import models


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
