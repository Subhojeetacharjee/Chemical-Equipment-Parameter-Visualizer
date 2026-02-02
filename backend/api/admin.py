"""
Admin configuration for Chemical Equipment Parameter Visualizer.
"""
from django.contrib import admin
from .models import Dataset, Equipment


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'uploaded_at', 'total_equipment', 'avg_flowrate', 'avg_pressure', 'avg_temperature']
    list_filter = ['uploaded_at']
    search_fields = ['name']
    ordering = ['-uploaded_at']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'dataset']
    list_filter = ['equipment_type', 'dataset']
    search_fields = ['name', 'equipment_type']
    ordering = ['name']
