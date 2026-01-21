# Cache invalidation using Django signals
# This automatically clears cache when users are created, updated, or deleted

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User, Passenger


@receiver(post_save, sender=User)
def invalidate_user_cache(sender, instance, **kwargs):
    """Clear cache when a user is saved (created or updated)"""
    # Clear the user list cache
    cache.delete('user_list')
    
    # Clear the cache for this specific user
    cache.delete(f'user_{instance.id}')


@receiver(post_delete, sender=User)
def invalidate_user_cache_on_delete(sender, instance, **kwargs):
    """Clear cache when a user is deleted"""
    # Clear the user list cache
    cache.delete('user_list')
    
    # Clear the cache for this specific user
    cache.delete(f'user_{instance.id}')


@receiver(post_save, sender=Passenger)
def invalidate_passenger_cache(sender, instance, **kwargs):
    """Clear cache when a passenger is saved (created or updated)"""
    # Clear the passenger list cache
    cache.delete('passenger_list')
    
    # Clear the cache for this specific passenger
    cache.delete(f'passenger_{instance.id}')


@receiver(post_delete, sender=Passenger)
def invalidate_passenger_cache_on_delete(sender, instance, **kwargs):
    """Clear cache when a passenger is deleted"""
    # Clear the passenger list cache
    cache.delete('passenger_list')
    
    # Clear the cache for this specific passenger
    cache.delete(f'passenger_{instance.id}')

