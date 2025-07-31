from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'name', 'description', 'status', 'source',
            'priority', 'owner', 'phone_number', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'description': {'required': True, 'allow_blank': False},
            'source': {'required': True},
        }

    def validate_phone_number(self, value):
        # Add phone number validation if needed
        return value
