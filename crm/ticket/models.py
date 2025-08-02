from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator

User = get_user_model()

class Ticket(models.Model):
    name = models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    description = models.TextField()
    status = models.CharField(max_length=20, default='new')
    source = models.CharField(max_length=20)
    priority = models.CharField(max_length=20, default='low')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_owned')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.status}"
