"""
Serializers for Chemical Equipment Parameter Visualizer API.
"""
from rest_framework import serializers
from .models import Dataset, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment model."""
    
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for Dataset model."""
    
    type_distribution_dict = serializers.SerializerMethodField()
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'uploaded_at', 'total_equipment',
            'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'type_distribution_dict', 'equipment_count'
        ]
    
    def get_type_distribution_dict(self, obj):
        return obj.get_type_distribution()
    
    def get_equipment_count(self, obj):
        return obj.equipment.count()


class DatasetDetailSerializer(DatasetSerializer):
    """Detailed serializer for Dataset with equipment list."""
    
    equipment = EquipmentSerializer(many=True, read_only=True)
    
    class Meta(DatasetSerializer.Meta):
        fields = DatasetSerializer.Meta.fields + ['equipment']


class SummarySerializer(serializers.Serializer):
    """Serializer for dataset summary statistics."""
    
    total_equipment = serializers.IntegerField()
    avg_flowrate = serializers.FloatField()
    avg_pressure = serializers.FloatField()
    avg_temperature = serializers.FloatField()
    type_distribution = serializers.DictField()
    equipment_list = EquipmentSerializer(many=True)


class FileUploadSerializer(serializers.Serializer):
    """Serializer for file upload."""
    
    file = serializers.FileField()
    
    def validate_file(self, value):
        """Validate that the uploaded file is a CSV."""
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")
        return value
