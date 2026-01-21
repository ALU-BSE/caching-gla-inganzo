from django.urls import path, include
from rest_framework import routers

from users.views import UserViewSet, PassengerViewSet, cache_stats

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'passengers', PassengerViewSet, basename='passenger')

urlpatterns = [
    path('cache-stats/', cache_stats, name='cache-stats'),  # New endpoint for cache stats
] + router.urls