from rest_framework import serializers

from users.models import User, Passenger


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 'user_type']


class PassengerSerializer(serializers.ModelSerializer):
    # Include user info in the passenger data
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Passenger
        fields = ['id', 'user', 'user_email', 'passenger_id', 'preferred_payment_method', 'home_address']