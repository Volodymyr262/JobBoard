# jobs/admin.py
from django.contrib import admin
from .models import Job, CompanyProfile, Location

admin.site.register(Job)
admin.site.register(CompanyProfile)
admin.site.register(Location)
