from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import NewsItemViewSet, UserProfileView, id_userAPIView, NewsFilterAPIView, tg_userAPIView, \
    subs_userAPIView, checklikeAPIView

router = DefaultRouter()
router.register('news', NewsItemViewSet)
router.register('users', views.ApiUserItemViewSet)
router.register('tags', views.TagViewSet)
router.register('sources', views.SourceItemViewSet)
router.register('subscriptions', views.UserNewSubscriptionViewSet)

urlpatterns = [
    path('news/', NewsFilterAPIView.as_view(), name='news-filter'),
    path('id_user/', id_userAPIView.as_view()),
    path('tg_user/', tg_userAPIView.as_view()),
    path('subs_user', subs_userAPIView.as_view()),
    path('likes', checklikeAPIView.as_view()),
]

urlpatterns.extend(router.urls)
