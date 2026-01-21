from django.shortcuts import render
from rest_framework import viewsets
from django.core.cache import cache  # Import cache
from django.conf import settings  # Import settings to get CACHE_TTL
from rest_framework.response import Response  # Import Response
from rest_framework.decorators import api_view  # Import decorator for simple views
import functools  # For creating decorators
import time  # For measuring time
import logging  # For logging performance

from users.models import User, Passenger
from users.serializers import UserSerializer, PassengerSerializer

# Setup logger for cache performance tracking
logger = logging.getLogger(__name__)


# Helper functions for cache tagging
def cache_with_tags(key, data, tags, timeout=300):
    """Store data in cache and tag it for easier invalidation"""
    # First, cache the actual data
    cache.set(key, data, timeout)
    
    # Then, for each tag, keep track of which keys have that tag
    for tag in tags:
        # Get existing keys with this tag (or empty set if none)
        tagged_keys = cache.get(f'tag_{tag}', set())
        # Add this key to the set
        tagged_keys.add(key)
        # Save the updated set back to cache
        cache.set(f'tag_{tag}', tagged_keys, timeout)


def invalidate_by_tag(tag):
    """Delete all cached items with a specific tag"""
    # Get all keys that have this tag
    tagged_keys = cache.get(f'tag_{tag}', set())
    
    # Delete each key
    for key in tagged_keys:
        cache.delete(key)
    
    # Delete the tag itself
    cache.delete(f'tag_{tag}')


# Simple decorator to measure cache performance
def cache_performance(cache_name):
    """Decorator to track how long cached methods take"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Record start time
            start_time = time.time()
            
            # Run the actual function
            result = func(*args, **kwargs)
            
            # Record end time and calculate duration
            end_time = time.time()
            duration = end_time - start_time
            
            # Log the performance
            logger.info(f"{cache_name}: {duration:.4f}s")
            
            return result
        return wrapper
    return decorator


# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    # Override the list method to add caching
    @cache_performance("user_list_cache")
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
    @cache_performance("user_detail_cache")
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
    
    # Override update to use write-through pattern
    def perform_update(self, serializer):
        # Update the user in database first
        super().perform_update(serializer)
        
        # Write-through: immediately update cache with new data
        # Instead of deleting, we update the cache right away
        user_data = self.get_serializer(serializer.instance).data
        cache_key = f"user_{serializer.instance.id}"
        cache.set(cache_key, user_data, timeout=settings.CACHE_TTL)
        
        # Still need to clear the user list cache
        cache.delete('user_list')
    
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


# ViewSet for Passenger model with caching
class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    
    # Cache the passenger list
    @cache_performance("passenger_list_cache")
    def list(self, request, *args, **kwargs):
        # Create cache key
        cache_key = 'passenger_list'
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        
        # Return cached data if available
        if cached_data is not None:
            return Response(cached_data)
        
        # Get fresh data from database
        response = super().list(request, *args, **kwargs)
        
        # Save to cache
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        return response
    
    # Cache individual passenger retrieval
    @cache_performance("passenger_detail_cache")
    def retrieve(self, request, *args, **kwargs):
        # Get passenger ID
        passenger_id = kwargs.get('pk')
        
        # Create cache key
        cache_key = f'passenger_{passenger_id}'
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        
        # Return cached data if available
        if cached_data is not None:
            return Response(cached_data)
        
        # Get fresh data from database
        response = super().retrieve(request, *args, **kwargs)
        
        # Save to cache
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        return response
    
    # Clear cache when creating new passenger
    def perform_create(self, serializer):
        # Clear the passenger list cache
        cache.delete('passenger_list')
        # Create the passenger
        super().perform_create(serializer)
    
    # Use write-through pattern for updates
    def perform_update(self, serializer):
        # Update in database first
        super().perform_update(serializer)
        
        # Write-through: update cache immediately
        passenger_data = self.get_serializer(serializer.instance).data
        cache_key = f"passenger_{serializer.instance.id}"
        cache.set(cache_key, passenger_data, timeout=settings.CACHE_TTL)
        
        # Clear list cache
        cache.delete('passenger_list')
    
    # Clear cache when deleting passenger
    def perform_destroy(self, instance):
        # Get passenger ID before deleting
        passenger_id = instance.id
        
        # Clear caches
        cache.delete('passenger_list')
        cache.delete(f'passenger_{passenger_id}')
        
        # Delete the passenger
        super().perform_destroy(instance)

