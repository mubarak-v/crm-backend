from django.contrib import admin

# Register your models here.
from .models import Employee
from .models import VerificationCode

admin.site.register(Employee)
admin.site.register(VerificationCode)


