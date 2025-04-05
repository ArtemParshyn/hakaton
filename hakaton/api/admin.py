from django.contrib import admin

from .models import ApiUser, UserTagSubscription, NewsItem, Tag

admin.site.register(ApiUser)
admin.site.register(Tag)
admin.site.register(NewsItem)
admin.site.register(UserTagSubscription)


# Register your models here.
