from django.shortcuts import render
from rest_framework import viewsets
from django.core.cache import cache  # Import cache
from django.conf import settings  # Import settings to get CACHE_TTL
from rest_framework.response import Response  # Import Response

from users.models import User
from users.serializers import UserSerializer


# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    # Override the list method to add caching
    def list(self, request, *args, **kwargs):
        # Step 1: Create a cache key (a unique name for this cached data)
        cache_key = 'user_list'
        
        # Step 2: Try to get data from cache
        cached_data = cache.get(cache_key)
        
        # Step 3: If we found cached data, return it
        if cached_data is not None:
            return Response(cached_data)
        
        # Step 4: If no cached data, get fresh data from database
        response = super().list(request, *args, **kwargs)
        
        # Step 5: Save the data to cache for next time
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        # Step 6: Return the response
        return response
    
    # Override create to clear cache when new user is added
    def perform_create(self, serializer):
        # Clear the user list cache because we're adding a new user
        cache.delete('user_list')
        # Create the user
        super().perform_create(serializer)
    
    # Override update to clear cache when user is updated
    def perform_update(self, serializer):
        # Clear the user list cache
        cache.delete('user_list')
        # Update the user
        super().perform_update(serializer)
    
    # Override delete to clear cache when user is deleted
    def perform_destroy(self, instance):
        # Clear the user list cache
        cache.delete('user_list')
        # Delete the user
        super().perform_destroy(instance)
