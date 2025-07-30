import uuid
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Employee(AbstractUser):
    class EmployeeType(models.TextChoices):
        LEADS = 'leads', _('Leads')
        DEALS = 'deals', _('Deals')
        COMPANIES = 'companies', _('Companies')
        TICKETS = 'tickets', _('Tickets')
        ALL = 'all', _('All')
    
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    industry_type = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    employee_type = models.CharField(
        max_length=20,
        choices=EmployeeType.choices,
        default=EmployeeType.LEADS,
        help_text=_("Type of employee access level")
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'employee_type']
    # Optional: If you want to login using email, set USERNAME_FIELD = 'email'
    # USERNAME_FIELD = 'email'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_employee_type_display()})"


class VerificationCode(models.Model):
    """
    Model to store verification codes that expire after 5 minutes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    reset_token = models.UUIDField(null=True, blank=True, unique=True)
    
    # Expiration time in minutes
    EXPIRATION_MINUTES = 5
    
    def is_valid(self):
        """Check if the code is still valid (not used and not expired)"""
        if self.is_used:
            return False
            
        expiration_time = self.created_at + timedelta(minutes=self.EXPIRATION_MINUTES)
        return timezone.now() <= expiration_time
    
    def mark_as_used(self):
        """Mark this code as used"""
        self.is_used = True
        self.save()
    
    @classmethod
    def generate_code(cls, email):
        """Generate a new verification code for the given email"""
        # Invalidate any existing codes for this email
        cls.objects.filter(email=email).update(is_used=True)
        
        # Generate a 6-digit code
        import random
        code = str(random.randint(100000, 999999))
        
        # Create and return the new code
        return cls.objects.create(email=email, code=code)
    
    def __str__(self):
        return f"{self.email} - {self.code} (Expires in {self.EXPIRATION_MINUTES} min)"
