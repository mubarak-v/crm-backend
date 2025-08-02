from rest_framework import serializers
from .models import Ticket
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email','first_name','last_name','phone_number']
        read_only_fields = ['id', 'username', 'email','first_name','last_name','phone_number']

class TicketSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'name', 'description', 'status', 'source', 'priority',
            'owner', 'phone_number', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the owner to the current user if not provided
        if 'owner' not in validated_data:
            validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
