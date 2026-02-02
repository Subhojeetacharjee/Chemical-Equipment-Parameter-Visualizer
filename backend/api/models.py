"""
Models for Chemical Equipment Parameter Visualizer.
"""
from django.db import models
from django.utils import timezone
import json


class Dataset(models.Model):
    """Model to store uploaded CSV datasets."""
    
    name = models.CharField(max_length=255, help_text="Name of the uploaded file")
    uploaded_at = models.DateTimeField(default=timezone.now)
    total_equipment = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(default=0.0)
    avg_pressure = models.FloatField(default=0.0)
    avg_temperature = models.FloatField(default=0.0)
    type_distribution = models.TextField(default='{}', help_text="JSON string of equipment type distribution")
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_type_distribution(self):
        """Return type distribution as dictionary."""
        try:
            return json.loads(self.type_distribution)
        except json.JSONDecodeError:
            return {}
    
    def set_type_distribution(self, distribution_dict):
        """Set type distribution from dictionary."""
        self.type_distribution = json.dumps(distribution_dict)


class Equipment(models.Model):
    """Model to store individual equipment records."""
    
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipment')
    name = models.CharField(max_length=255, help_text="Equipment name")
    equipment_type = models.CharField(max_length=100, help_text="Type of equipment")
    flowrate = models.FloatField(help_text="Flowrate value")
    pressure = models.FloatField(help_text="Pressure value")
    temperature = models.FloatField(help_text="Temperature value")
    
    class Meta:
        verbose_name_plural = "Equipment"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.equipment_type})"
