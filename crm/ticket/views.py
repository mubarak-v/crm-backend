from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Ticket
from .serializers import TicketSerializer
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class TicketListAPIView(generics.ListAPIView):
    """
    API endpoint that allows tickets to be viewed.
    """
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally filter tickets by query parameters
        - status: Filter by ticket status
        - owner: Filter by owner ID
        - priority: Filter by priority
        """
        queryset = Ticket.objects.all()
        
        # Filter by status if provided
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status__iexact=status)
            
        # Filter by owner if provided
        owner_id = self.request.query_params.get('owner', None)
        if owner_id is not None:
            queryset = queryset.filter(owner_id=owner_id)
            
        # Filter by priority if provided
        priority = self.request.query_params.get('priority', None)
        if priority is not None:
            queryset = queryset.filter(priority__iexact=priority)
            
        # Order by most recent first
        return queryset.order_by('-created_at')

class CreateTicketAPIView(generics.CreateAPIView):
    """
    API endpoint that allows tickets to be created.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Set the owner to the current user if not provided
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"Processing ticket creation request from user {request.user.email}")
            logger.debug(f"Request data: {request.data}")
            
            # Create a mutable copy of the request data
            data = request.data.copy()
            
            # Ensure the source is lowercase to match our choices
            if 'source' in data:
                data['source'] = data['source'].lower()
                
            # Set default status if not provided
            if 'status' not in data:
                data['status'] = 'open'
                
            # Set default priority if not provided
            if 'priority' not in data:
                data['priority'] = 'medium'
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            logger.info(f"Ticket created successfully. ID: {serializer.data.get('id')}")
            
            return Response(
                {
                    'status': 'success',
                    'message': 'Ticket created successfully',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            logger.error(f"Request data: {request.data}")
            logger.error(f"Validation errors: {serializer.errors if 'serializer' in locals() else 'No serializer'}")
            
            if hasattr(e, 'get_full_details'):
                errors = e.get_full_details()
            elif hasattr(e, 'detail'):
                errors = e.detail
            else:
                errors = str(e)
                
            return Response(
                {
                    'status': 'error',
                    'message': 'Failed to create ticket',
                    'errors': errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class UpdateTicketAPIView(generics.UpdateAPIView):
    """
    API endpoint that allows tickets to be updated.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        try:
            logger.info(f"Processing ticket update request from user {request.user.email}")
            logger.debug(f"Request data: {request.data}")
            
            # Get the ticket instance
            instance = self.get_object()
            
            # Create a mutable copy of the request data
            data = request.data.copy()
            
            # Ensure the source is lowercase to match our choices if provided
            if 'source' in data:
                data['source'] = data['source'].lower()
                
            # Ensure status is lowercase if provided
            if 'status' in data:
                data['status'] = data['status'].lower()
                
            # Ensure priority is lowercase if provided
            if 'priority' in data:
                data['priority'] = data['priority'].lower()
            
            # Partial update (PATCH) is allowed, but we're using PUT for full updates
            partial = kwargs.pop('partial', False)
            
            # Validate and save the data
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            # Get updated instance data
            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to the queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            
            logger.info(f"Ticket updated successfully. ID: {instance.id}")
            
            return Response(
                {
                    'status': 'success',
                    'message': 'Ticket updated successfully',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error updating ticket: {str(e)}")
            logger.error(f"Request data: {request.data}")
            logger.error(f"Validation errors: {serializer.errors if 'serializer' in locals() else 'No serializer'}")
            
            if hasattr(e, 'get_full_details'):
                errors = e.get_full_details()
            elif hasattr(e, 'detail'):
                errors = e.detail
            else:
                errors = str(e)
                
            return Response(
                {
                    'status': 'error',
                    'message': 'Failed to update ticket',
                    'errors': errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
