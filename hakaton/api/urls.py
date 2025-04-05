from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import NewsFilterAPIView, NewsItemViewSet, UserProfileView, id_userAPIView

router = DefaultRouter()
router.register('news', NewsItemViewSet)
router.register('users', views.ApiUserItemViewSet)
router.register('tags', views.TagViewSet)
router.register('sources', views.SourceItemViewSet)
router.register('subscriptions', views.UserTagSubscriptionViewSet, basename='subscription')


urlpatterns = [
    path('news/', NewsFilterAPIView.as_view(), name='news-filter'),
    path('id_user/', id_userAPIView.as_view()),
]

urlpatterns.extend(router.urls)
