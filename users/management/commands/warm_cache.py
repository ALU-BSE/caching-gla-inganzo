# This is a Django management command to warm up the cache

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from users.models import User, Passenger
from users.serializers import UserSerializer, PassengerSerializer


class Command(BaseCommand):
    # This shows up when you run python manage.py help
    help = 'Pre-load frequently accessed data into cache'

    def handle(self, *args, **options):
        # This is the main function that runs when you call the command
        
        # Print a message to show we're starting
        self.stdout.write('Starting cache warm-up...')
        
        # Step 1: Get all users from database
        users = User.objects.all()
        
        # Step 2: Convert users to JSON format
        serializer = UserSerializer(users, many=True)
        
        # Step 3: Cache the user list
        cache.set('user_list', serializer.data, timeout=settings.CACHE_TTL)
        self.stdout.write(f'Cached user list ({len(users)} users)')
        
        # Step 4: Cache each individual user
        cached_count = 0
        for user in users:
            # Serialize individual user
            user_data = UserSerializer(user).data
            # Cache it with user_id in the key
            cache.set(f'user_{user.id}', user_data, timeout=settings.CACHE_TTL)
            cached_count += 1
        
        # Step 5: Print success message
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cached {cached_count} individual users')
        )
        
        # Step 6: Now cache passengers
        passengers = Passenger.objects.all()
        
        # Step 7: Convert passengers to JSON format
        passenger_serializer = PassengerSerializer(passengers, many=True)
        
        # Step 8: Cache the passenger list
        cache.set('passenger_list', passenger_serializer.data, timeout=settings.CACHE_TTL)
        self.stdout.write(f'Cached passenger list ({len(passengers)} passengers)')
        
        # Step 9: Cache each individual passenger
        passenger_cached_count = 0
        for passenger in passengers:
            # Serialize individual passenger
            passenger_data = PassengerSerializer(passenger).data
            # Cache it with passenger_id in the key
            cache.set(f'passenger_{passenger.id}', passenger_data, timeout=settings.CACHE_TTL)
            passenger_cached_count += 1
        
        # Step 10: Print final success message
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cached {passenger_cached_count} individual passengers')
        )
        self.stdout.write(self.style.SUCCESS('Cache warm-up complete!'))

