from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreateTicketAPIView, TicketListAPIView, UpdateTicketAPIView

app_name = 'ticket'

router = DefaultRouter()
# We'll use router if we need to add more endpoints later

urlpatterns = [
    path('', include(router.urls)),
    path('create/', CreateTicketAPIView.as_view(), name='create-ticket'),
    path('list/', TicketListAPIView.as_view(), name='ticket-list'),
    path('<int:pk>/update/', UpdateTicketAPIView.as_view(), name='update-ticket'),  # New update endpoint
]