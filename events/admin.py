from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'location', 'start_date', 'end_date']
    list_filter = ['category', 'start_date']
    search_fields = ['name', 'description', 'location']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
