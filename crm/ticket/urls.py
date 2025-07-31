from django.urls import path
from .views import CreateTicketAPIView

app_name = 'ticket'

urlpatterns = [
    path('create/', CreateTicketAPIView.as_view(), name='create-ticket'),
]
