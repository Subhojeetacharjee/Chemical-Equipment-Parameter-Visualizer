"""
Views for Chemical Equipment Parameter Visualizer API.
"""
import io
import json
import pandas as pd
from django.http import HttpResponse
from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER

from .models import Dataset, Equipment
from .serializers import (
    DatasetSerializer, DatasetDetailSerializer,
    EquipmentSerializer, SummarySerializer, FileUploadSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET'])
def api_root(request):
    """API root endpoint with available endpoints information."""
    return Response({
        'message': 'Chemical Equipment Parameter Visualizer API',
        'version': '1.0.0',
        'endpoints': {
            'upload': '/api/upload/',
            'datasets': '/api/datasets/',
            'history': '/api/history/',
            'report': '/api/report/<dataset_id>/',
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    """
    Upload and process a CSV file containing equipment data.
    Requires authentication - datasets are saved per user.
    
    Expected CSV columns: Equipment Name, Type, Flowrate, Pressure, Temperature
    """
    serializer = FileUploadSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    csv_file = serializer.validated_data['file']
    
    try:
        # Read CSV using pandas
        df = pd.read_csv(csv_file)
        
        # Normalize column names (strip whitespace, handle variations)
        df.columns = df.columns.str.strip()
        
        # Map possible column name variations
        column_mapping = {
            'Equipment Name': ['Equipment Name', 'equipment_name', 'Name', 'name', 'EquipmentName'],
            'Type': ['Type', 'type', 'Equipment Type', 'equipment_type', 'EquipmentType'],
            'Flowrate': ['Flowrate', 'flowrate', 'Flow Rate', 'flow_rate', 'FlowRate'],
            'Pressure': ['Pressure', 'pressure'],
            'Temperature': ['Temperature', 'temperature', 'Temp', 'temp']
        }
        
        # Find actual column names in the dataframe
        actual_columns = {}
        for standard_name, variations in column_mapping.items():
            for var in variations:
                if var in df.columns:
                    actual_columns[standard_name] = var
                    break
        
        # Validate required columns
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        missing_columns = [col for col in required_columns if col not in actual_columns]
        
        if missing_columns:
            return Response({
                'error': f'Missing required columns: {missing_columns}',
                'found_columns': list(df.columns),
                'expected_columns': required_columns
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Rename columns to standard names
        df = df.rename(columns={v: k for k, v in actual_columns.items()})
        
        # Clean numeric columns
        for col in ['Flowrate', 'Pressure', 'Temperature']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with NaN values in numeric columns
        df = df.dropna(subset=['Flowrate', 'Pressure', 'Temperature'])
        
        if df.empty:
            return Response({
                'error': 'No valid data rows found after processing'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate statistics
        total_equipment = len(df)
        avg_flowrate = round(df['Flowrate'].mean(), 2)
        avg_pressure = round(df['Pressure'].mean(), 2)
        avg_temperature = round(df['Temperature'].mean(), 2)
        type_distribution = df['Type'].value_counts().to_dict()
        
        # Create dataset record (associated with authenticated user)
        dataset = Dataset.objects.create(
            user=request.user,
            name=csv_file.name,
            total_equipment=total_equipment,
            avg_flowrate=avg_flowrate,
            avg_pressure=avg_pressure,
            avg_temperature=avg_temperature,
        )
        dataset.set_type_distribution(type_distribution)
        dataset.save()
        
        # Create equipment records
        equipment_list = []
        for _, row in df.iterrows():
            equipment = Equipment.objects.create(
                dataset=dataset,
                name=str(row['Equipment Name']),
                equipment_type=str(row['Type']),
                flowrate=float(row['Flowrate']),
                pressure=float(row['Pressure']),
                temperature=float(row['Temperature'])
            )
            equipment_list.append(equipment)
        
        # Keep only last 5 datasets per user
        user_datasets = Dataset.objects.filter(user=request.user)
        old_datasets = user_datasets[5:]
        for old_dataset in old_datasets:
            old_dataset.delete()
        
        # Prepare response
        response_data = {
            'message': 'File uploaded and processed successfully',
            'dataset_id': dataset.id,
            'summary': {
                'total_equipment': total_equipment,
                'avg_flowrate': avg_flowrate,
                'avg_pressure': avg_pressure,
                'avg_temperature': avg_temperature,
                'type_distribution': type_distribution
            },
            'equipment_list': EquipmentSerializer(equipment_list, many=True).data
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except pd.errors.EmptyDataError:
        return Response({
            'error': 'The CSV file is empty'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'Error processing file: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    """Get the last 5 uploaded datasets for the authenticated user."""
    datasets = Dataset.objects.filter(user=request.user)[:5]
    serializer = DatasetSerializer(datasets, many=True)
    return Response({
        'count': len(serializer.data),
        'datasets': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dataset(request, dataset_id):
    """Get detailed information about a specific dataset (user's own datasets only)."""
    try:
        dataset = Dataset.objects.get(id=dataset_id, user=request.user)
        serializer = DatasetDetailSerializer(dataset)
        return Response(serializer.data)
    except Dataset.DoesNotExist:
        return Response({
            'error': 'Dataset not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_dataset(request, dataset_id):
    """Delete a specific dataset (user's own datasets only)."""
    try:
        dataset = Dataset.objects.get(id=dataset_id, user=request.user)
        dataset.delete()
        return Response({
            'message': 'Dataset deleted successfully'
        }, status=status.HTTP_200_OK)
    except Dataset.DoesNotExist:
        return Response({
            'error': 'Dataset not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request, dataset_id):
    """
    Generate a PDF report for a dataset.
    Requires JWT authentication - only generates reports for user's own datasets.
    """
    user = request.user
    
    try:
        dataset = Dataset.objects.get(id=dataset_id, user=request.user)
    except Dataset.DoesNotExist:
        return Response({
            'error': 'Dataset not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Generate PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    elements.append(Paragraph("Chemical Equipment Parameter Report", title_style))
    elements.append(Spacer(1, 20))
    
    # Dataset info
    info_style = styles['Normal']
    elements.append(Paragraph(f"<b>Dataset:</b> {dataset.name}", info_style))
    elements.append(Paragraph(f"<b>Uploaded:</b> {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}", info_style))
    elements.append(Paragraph(f"<b>Generated by:</b> {user.username}", info_style))
    elements.append(Spacer(1, 20))
    
    # Summary section
    elements.append(Paragraph("<b>Summary Statistics</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Equipment', str(dataset.total_equipment)],
        ['Average Flowrate', f'{dataset.avg_flowrate:.2f}'],
        ['Average Pressure', f'{dataset.avg_pressure:.2f}'],
        ['Average Temperature', f'{dataset.avg_temperature:.2f}'],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Type distribution
    elements.append(Paragraph("<b>Equipment Type Distribution</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    type_dist = dataset.get_type_distribution()
    type_data = [['Equipment Type', 'Count']]
    for eq_type, count in type_dist.items():
        type_data.append([eq_type, str(count)])
    
    type_table = Table(type_data, colWidths=[3*inch, 2*inch])
    type_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1fae5')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(type_table)
    elements.append(Spacer(1, 20))
    
    # Equipment list
    elements.append(Paragraph("<b>Equipment Details</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    equipment_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
    for eq in dataset.equipment.all()[:50]:  # Limit to 50 for PDF size
        equipment_data.append([
            eq.name[:20] if len(eq.name) > 20 else eq.name,
            eq.equipment_type,
            f'{eq.flowrate:.2f}',
            f'{eq.pressure:.2f}',
            f'{eq.temperature:.2f}'
        ])
    
    equipment_table = Table(equipment_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    equipment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e9d5ff')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(equipment_table)
    
    # Build PDF
    doc.build(elements)
    
    # Return PDF response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{dataset.id}.pdf"'
    return response


@api_view(['GET'])
def get_latest_summary(request):
    """Get summary of the most recently uploaded dataset."""
    try:
        dataset = Dataset.objects.first()
        if not dataset:
            return Response({
                'error': 'No datasets available'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DatasetDetailSerializer(dataset)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
