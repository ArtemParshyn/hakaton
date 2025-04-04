from django.urls import path
from .views import ProtectedView

urlpatterns = [
        path('api/protected-route/', ProtectedView.as_view(), name='protected-route'),
]
