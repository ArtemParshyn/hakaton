from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class ApiUser(AbstractUser):

    telegram_chat_id = models.CharField(max_length=30, blank=True, null=True)
    can_publish = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    can_write = models.BooleanField(default=True)
    subscribed = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Source(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class NewsItem(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
    ]
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(
        default=timezone.now,  # Значение по умолчанию, но можно переопределить
        blank=True,  # Разрешить не передавать поле в формах/API
        null=True  # Разрешить NULL в базе данных (опционально)
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    is_organization_news = models.BooleanField(default=False)
    author = models.ForeignKey(ApiUser, on_delete=models.CASCADE, related_name='authored_news')
    tags = models.ManyToManyField(Tag, related_name='news_items')
    sources = models.URLField(blank=False)
    cover = models.URLField(default=0)

    def __str__(self):
        return self.title


class UserNewSubscription(models.Model):
    user = models.ForeignKey(ApiUser, on_delete=models.CASCADE, related_name='subscriptions')
    new = models.ForeignKey(NewsItem, on_delete=models.CASCADE, related_name='subscribed_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} subscribed to {self.new.title}"
