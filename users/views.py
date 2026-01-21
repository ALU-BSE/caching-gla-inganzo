from django.shortcuts import render
from rest_framework import viewsets
from django.core.cache import cache  # Import cache
from django.conf import settings  # Import settings to get CACHE_TTL
from rest_framework.response import Response  # Import Response
from rest_framework.decorators import api_view  # Import decorator for simple views

from users.models import User, Passenger
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
    
    # Override retrieve to add caching for individual users
    def retrieve(self, request, *args, **kwargs):
        # Step 1: Get the user ID from the URL
        user_id = kwargs.get('pk')
        
        # Step 2: Create a cache key for this specific user
        cache_key = f'user_{user_id}'
        
        # Step 3: Try to get data from cache
        cached_data = cache.get(cache_key)
        
        # Step 4: If we found cached data, return it
        if cached_data is not None:
            return Response(cached_data)
        
        # Step 5: If no cached data, get fresh data from database
        response = super().retrieve(request, *args, **kwargs)
        
        # Step 6: Save the data to cache for next time
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        # Step 7: Return the response
        return response
    
    # Override create to clear cache when new user is added
    def perform_create(self, serializer):
        # Clear the user list cache because we're adding a new user
        cache.delete('user_list')
        # Create the user
        super().perform_create(serializer)
    
    # Override update to clear cache when user is updated
    def perform_update(self, serializer):
        # Get the user ID
        user_id = serializer.instance.id
        
        # Clear the user list cache
        cache.delete('user_list')
        # Also clear the cache for this specific user
        cache.delete(f'user_{user_id}')
        
        # Update the user
        super().perform_update(serializer)
    
    # Override delete to clear cache when user is deleted
    def perform_destroy(self, instance):
        # Get the user ID before deleting
        user_id = instance.id
        
        # Clear the user list cache
        cache.delete('user_list')
        # Also clear the cache for this specific user
        cache.delete(f'user_{user_id}')
        
        # Delete the user
        super().perform_destroy(instance)


# Simple view to show cache statistics
@api_view(['GET'])
def cache_stats(request):
    # Try to get some info about what's in cache
    # This is a simple version - just showing if our main caches exist
    
    # Check if user_list is cached
    user_list_cached = cache.get('user_list') is not None
    
    # Count how many users we have (for reference)
    total_users = User.objects.count()
    
    # Return the stats
    return Response({
        'user_list_cached': user_list_cached,
        'total_users_in_db': total_users,
        'cache_timeout_seconds': settings.CACHE_TTL,
        'message': 'Cache statistics - shows if data is currently cached'
    })
