"""
Chemical Equipment Parameter Visualizer - Desktop Application
Built with PyQt5 and Matplotlib
"""

import sys
import os
import json
import requests
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QTabWidget, QGroupBox, QGridLayout, QMessageBox, QListWidget,
    QListWidgetItem, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QSplitter, QFrame, QScrollArea, QSizePolicy, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# API Configuration
API_BASE_URL = os.environ.get('API_URL', 'http://localhost:8000/api')


class UploadWorker(QThread):
    """Background worker for file upload with progress"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            self.progress.emit(20)
            with open(self.file_path, 'rb') as f:
                files = {'file': (os.path.basename(self.file_path), f, 'text/csv')}
                self.progress.emit(50)
                response = requests.post(f'{API_BASE_URL}/upload/', files=files, timeout=30)
                self.progress.emit(80)

            if response.status_code == 201:
                self.progress.emit(100)
                self.finished.emit(response.json())
            else:
                try:
                    error_data = response.json()
                    self.error.emit(error_data.get('error', f'Error: {response.status_code}'))
                except:
                    self.error.emit(f'Error: {response.status_code}')
        except requests.exceptions.ConnectionError:
            self.error.emit('Connection error. Make sure the backend server is running.')
        except Exception as e:
            self.error.emit(str(e))


class APIWorker(QThread):
    """Background worker for API calls"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, method, url, data=None, files=None):
        super().__init__()
        self.method = method
        self.url = url
        self.data = data
        self.files = files

    def run(self):
        try:
            if self.method == 'GET':
                response = requests.get(self.url, timeout=30)
            elif self.method == 'POST':
                if self.files:
                    response = requests.post(self.url, files=self.files, timeout=30)
                else:
                    response = requests.post(self.url, json=self.data, timeout=30)
            elif self.method == 'DELETE':
                response = requests.delete(self.url, timeout=30)
            else:
                self.error.emit(f'Unknown method: {self.method}')
                return

            if response.status_code in [200, 201]:
                self.finished.emit(response.json())
            else:
                try:
                    error_data = response.json()
                    self.error.emit(error_data.get('error', f'Error: {response.status_code}'))
                except:
                    self.error.emit(f'Error: {response.status_code}')
        except requests.exceptions.ConnectionError:
            self.error.emit('Connection error. Make sure the backend server is running.')
        except Exception as e:
            self.error.emit(str(e))


class MplCanvas(FigureCanvas):
    """Matplotlib canvas for embedding in PyQt5"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setMinimumSize(280, 220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.fig.tight_layout(pad=3.0)


class LoginDialog(QDialog):
    """Dialog for PDF report authentication"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Generate PDF Report')
        self.setFixedSize(350, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title = QLabel('🔐 Authentication Required')
        title.setFont(QFont('Segoe UI', 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Form
        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter username')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter password')
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow('Username:', self.username_input)
        form_layout.addRow('Password:', self.password_input)
        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()


class ChartWidget(QWidget):
    """Widget containing multiple Matplotlib charts"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(650, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create four chart canvases
        self.pie_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.bar_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.line_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.type_bar_canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Add to grid
        layout.addWidget(self.create_chart_frame('Equipment Type Distribution', self.pie_canvas), 0, 0)
        layout.addWidget(self.create_chart_frame('Average Parameter Values', self.bar_canvas), 0, 1)
        layout.addWidget(self.create_chart_frame('Equipment Parameters Trend', self.line_canvas), 1, 0)
        layout.addWidget(self.create_chart_frame('Type Count', self.type_bar_canvas), 1, 1)

    def create_chart_frame(self, title, canvas):
        """Create a styled frame for each chart"""
        frame = QFrame()
        frame.setMinimumSize(300, 260)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 10, QFont.Bold))
        title_label.setStyleSheet('color: #1e293b; border: none;')
        layout.addWidget(title_label)
        layout.addWidget(canvas, 1)

        return frame

    def update_charts(self, summary, equipment_list):
        """Update all charts with new data"""
        if not summary:
            return

        type_distribution = summary.get('type_distribution', {})
        
        # Clear all axes
        self.pie_canvas.axes.clear()
        self.bar_canvas.axes.clear()
        self.line_canvas.axes.clear()
        self.type_bar_canvas.axes.clear()

        # Color palette
        colors = ['#667eea', '#764ba2', '#f472b6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6']

        # 1. Pie Chart - Type Distribution
        if type_distribution:
            labels = list(type_distribution.keys())
            sizes = list(type_distribution.values())
            wedges, texts, autotexts = self.pie_canvas.axes.pie(
                sizes, labels=None, colors=colors[:len(labels)],
                autopct='%1.1f%%', startangle=90, pctdistance=0.75,
                textprops={'fontsize': 8, 'color': 'white', 'fontweight': 'bold'}
            )
            self.pie_canvas.axes.legend(wedges, labels, loc='lower center', 
                                         fontsize=7, ncol=2, bbox_to_anchor=(0.5, -0.15))

        # 2. Bar Chart - Average Values
        params = ['Flowrate', 'Pressure', 'Temp']
        values = [
            summary.get('avg_flowrate', 0),
            summary.get('avg_pressure', 0),
            summary.get('avg_temperature', 0)
        ]
        bars = self.bar_canvas.axes.bar(params, values, color=['#667eea', '#764ba2', '#10b981'], width=0.6)
        self.bar_canvas.axes.set_ylabel('Avg Value', fontsize=9)
        self.bar_canvas.axes.tick_params(axis='both', labelsize=8)
        self.bar_canvas.axes.spines['top'].set_visible(False)
        self.bar_canvas.axes.spines['right'].set_visible(False)
        
        # Add value labels on bars
        for bar, val in zip(bars, values):
            self.bar_canvas.axes.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f'{val:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold'
            )

        # 3. Line Chart - Equipment Parameters Trend
        if equipment_list:
            limited_equipment = equipment_list[:8]  # Limit to 8 for cleaner display
            names = [eq.get('name', '')[:8] for eq in limited_equipment]
            flowrates = [eq.get('flowrate', 0) for eq in limited_equipment]
            pressures = [eq.get('pressure', 0) for eq in limited_equipment]
            temperatures = [eq.get('temperature', 0) for eq in limited_equipment]

            x = range(len(names))
            self.line_canvas.axes.plot(x, flowrates, 'o-', label='Flow', color='#667eea', linewidth=1.5, markersize=4)
            self.line_canvas.axes.plot(x, pressures, 's-', label='Press', color='#764ba2', linewidth=1.5, markersize=4)
            self.line_canvas.axes.plot(x, temperatures, '^-', label='Temp', color='#10b981', linewidth=1.5, markersize=4)
            self.line_canvas.axes.set_xticks(x)
            self.line_canvas.axes.set_xticklabels(names, rotation=30, ha='right', fontsize=7)
            self.line_canvas.axes.legend(loc='upper right', fontsize=7, framealpha=0.9)
            self.line_canvas.axes.tick_params(axis='y', labelsize=7)
            self.line_canvas.axes.grid(True, alpha=0.3, linestyle='--')
            self.line_canvas.axes.spines['top'].set_visible(False)
            self.line_canvas.axes.spines['right'].set_visible(False)

        # 4. Type Bar Chart
        if type_distribution:
            types = [t[:10] for t in type_distribution.keys()]  # Truncate long names
            counts = list(type_distribution.values())
            bars = self.type_bar_canvas.axes.bar(types, counts, color='#667eea', width=0.6)
            self.type_bar_canvas.axes.set_ylabel('Count', fontsize=9)
            self.type_bar_canvas.axes.tick_params(axis='x', rotation=30, labelsize=7)
            self.type_bar_canvas.axes.tick_params(axis='y', labelsize=8)
            self.type_bar_canvas.axes.spines['top'].set_visible(False)
            self.type_bar_canvas.axes.spines['right'].set_visible(False)
            
            for bar, count in zip(bars, counts):
                self.type_bar_canvas.axes.text(
                    bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom', fontsize=8, fontweight='bold'
                )

        # Refresh all canvases with better padding
        for canvas in [self.pie_canvas, self.bar_canvas, self.line_canvas, self.type_bar_canvas]:
            canvas.fig.tight_layout(pad=1.5)
            canvas.draw()

    def clear_charts(self):
        """Clear all charts"""
        for canvas in [self.pie_canvas, self.bar_canvas, self.line_canvas, self.type_bar_canvas]:
            canvas.axes.clear()
            canvas.draw()


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.current_dataset_id = None
        self.summary = None
        self.equipment_list = []
        self.history = []
        self.worker = None
        self.upload_worker = None
        self.selected_file_path = None
        
        self.setWindowTitle('Chemical Equipment Parameter Visualizer')
        self.setMinimumSize(1400, 900)
        self.setup_ui()
        self.apply_styles()
        # Delay history fetch for smoother startup
        QTimer.singleShot(500, self.fetch_history)

    def setup_ui(self):
        """Set up the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Upload and History
        left_panel = self.create_left_panel()
        left_panel.setMinimumWidth(320)
        left_panel.setMaximumWidth(400)
        splitter.addWidget(left_panel)

        # Right panel - Summary, Charts, and Table
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([350, 1050])
        splitter.setStretchFactor(0, 0)  # Left panel doesn't stretch
        splitter.setStretchFactor(1, 1)  # Right panel stretches
        main_layout.addWidget(splitter)

    def create_header(self):
        """Create header section"""
        header = QFrame()
        header.setObjectName('header')
        header.setFixedHeight(100)
        header.setStyleSheet("""
            #header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(5)

        title = QLabel('Chemical Equipment Parameter Visualizer')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setStyleSheet('color: #ffffff; background: transparent; letter-spacing: 1px;')
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel('Upload, analyze, and visualize chemical equipment parameters')
        subtitle.setFont(QFont('Arial', 10))
        subtitle.setStyleSheet('color: #e0e0ff; background: transparent;')
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        return header

    def create_left_panel(self):
        """Create left panel with upload and history"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Upload section
        upload_group = QGroupBox('📤 Upload CSV File')
        upload_group.setFont(QFont('Segoe UI', 11, QFont.Bold))
        upload_layout = QVBoxLayout(upload_group)
        upload_layout.setSpacing(10)

        # Select file button
        self.select_btn = QPushButton('📁 Select CSV File')
        self.select_btn.setObjectName('primaryButton')
        self.select_btn.clicked.connect(self.select_file)
        self.select_btn.setMinimumHeight(45)
        upload_layout.addWidget(self.select_btn)

        # Selected file display with clear button
        self.file_frame = QFrame()
        self.file_frame.setStyleSheet("""
            QFrame {
                background-color: #f0fdf4;
                border: 1px solid #86efac;
                border-radius: 8px;
            }
        """)
        self.file_frame.setVisible(False)
        file_frame_layout = QHBoxLayout(self.file_frame)
        file_frame_layout.setContentsMargins(10, 8, 10, 8)
        
        self.file_label = QLabel('No file selected')
        self.file_label.setStyleSheet('color: #166534; font-weight: bold; border: none;')
        file_frame_layout.addWidget(self.file_label, 1)
        
        clear_file_btn = QPushButton('✕')
        clear_file_btn.setFixedSize(24, 24)
        clear_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        clear_file_btn.clicked.connect(self.clear_selected_file)
        file_frame_layout.addWidget(clear_file_btn)
        upload_layout.addWidget(self.file_frame)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 4px;
            }
        """)
        upload_layout.addWidget(self.progress_bar)

        # Upload button (separate from select)
        self.upload_btn = QPushButton('⬆️ Upload File')
        self.upload_btn.setObjectName('primaryButton')
        self.upload_btn.clicked.connect(self.start_upload)
        self.upload_btn.setMinimumHeight(45)
        self.upload_btn.setEnabled(False)
        upload_layout.addWidget(self.upload_btn)

        layout.addWidget(upload_group)

        # History section
        history_group = QGroupBox('📚 Upload History (Last 5)')
        history_group.setFont(QFont('Segoe UI', 11, QFont.Bold))
        history_layout = QVBoxLayout(history_group)
        history_layout.setSpacing(8)

        self.history_list = QListWidget()
        self.history_list.setMinimumHeight(250)
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_history_context_menu)
        history_layout.addWidget(self.history_list)

        # Button row for history
        history_btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton('🔄 Refresh')
        refresh_btn.clicked.connect(self.fetch_history)
        history_btn_layout.addWidget(refresh_btn)
        
        self.delete_btn = QPushButton('🗑️ Delete Selected')
        self.delete_btn.clicked.connect(self.delete_selected_history)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #fee2e2;
                color: #dc2626;
                border: 1px solid #fecaca;
            }
            QPushButton:hover {
                background-color: #fecaca;
            }
        """)
        history_btn_layout.addWidget(self.delete_btn)
        
        history_layout.addLayout(history_btn_layout)

        layout.addWidget(history_group, 1)

        return panel

    def create_right_panel(self):
        """Create right panel with summary, charts, and table"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Summary section
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(20, 20, 20, 20)

        summary_header = QHBoxLayout()
        summary_title = QLabel('📊 Summary Statistics')
        summary_title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        summary_header.addWidget(summary_title)

        self.report_btn = QPushButton('📄 Generate PDF Report')
        self.report_btn.setObjectName('primaryButton')
        self.report_btn.clicked.connect(self.generate_report)
        self.report_btn.setEnabled(False)
        summary_header.addWidget(self.report_btn)

        summary_layout.addLayout(summary_header)

        # Summary cards grid
        self.summary_grid = QGridLayout()
        self.summary_cards = {}
        
        card_configs = [
            ('total', 'Total Equipment', 0, 0),
            ('flowrate', 'Avg Flowrate', 0, 1),
            ('pressure', 'Avg Pressure', 0, 2),
            ('temperature', 'Avg Temperature', 0, 3),
            ('types', 'Equipment Types', 0, 4),
        ]

        for key, label, row, col in card_configs:
            card = self.create_summary_card(label, '-')
            self.summary_cards[key] = card
            self.summary_grid.addWidget(card, row, col)

        summary_layout.addLayout(self.summary_grid)
        layout.addWidget(summary_frame)

        # Tabs for Charts and Data Table
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }
            QTabBar::tab {
                background-color: #f1f5f9;
                padding: 12px 30px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #667eea;
                font-weight: bold;
            }
        """)

        # Charts tab
        self.chart_widget = ChartWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.chart_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('background-color: transparent; border: none;')
        self.tabs.addTab(scroll_area, '📈 Charts')

        # Data table tab
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #e2e8f0;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #667eea;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item:alternate {
                background-color: #f8fafc;
            }
        """)
        self.tabs.addTab(self.data_table, '📋 Data Table')

        layout.addWidget(self.tabs)

        return panel

    def create_summary_card(self, label, value):
        """Create a summary statistics card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                border-radius: 10px;
                border: 1px solid #e2e8f0;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout(card)

        label_widget = QLabel(label)
        label_widget.setFont(QFont('Segoe UI', 9))
        label_widget.setStyleSheet('color: #64748b; border: none;')
        label_widget.setAlignment(Qt.AlignCenter)

        value_widget = QLabel(str(value))
        value_widget.setFont(QFont('Segoe UI', 20, QFont.Bold))
        value_widget.setStyleSheet('color: #1e293b; border: none;')
        value_widget.setAlignment(Qt.AlignCenter)
        value_widget.setObjectName('valueLabel')

        layout.addWidget(label_widget)
        layout.addWidget(value_widget)

        return card

    def apply_styles(self):
        """Apply global application styles"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 12px;
                color: #475569;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
            QPushButton#primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                font-weight: bold;
            }
            QPushButton#primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
            QPushButton#primaryButton:disabled {
                background: #94a3b8;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e2e8f0;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f0f4ff;
            }
        """)

    def select_file(self):
        """Open file dialog to select CSV file (doesn't upload yet)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select CSV File', '',
            'CSV Files (*.csv);;All Files (*)'
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.file_frame.setVisible(True)
            self.upload_btn.setEnabled(True)

    def clear_selected_file(self):
        """Clear the selected file"""
        self.selected_file_path = None
        self.file_label.setText('No file selected')
        self.file_frame.setVisible(False)
        self.upload_btn.setEnabled(False)

    def start_upload(self):
        """Start the file upload in a background thread"""
        if not self.selected_file_path:
            return
        
        # Disable buttons during upload
        self.select_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        
        # Start background upload
        self.upload_worker = UploadWorker(self.selected_file_path)
        self.upload_worker.progress.connect(self.on_upload_progress)
        self.upload_worker.finished.connect(self.on_upload_finished)
        self.upload_worker.error.connect(self.on_upload_error)
        self.upload_worker.start()

    def on_upload_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def on_upload_finished(self, data):
        """Handle successful upload"""
        self.progress_bar.setVisible(False)
        self.select_btn.setEnabled(True)
        self.clear_selected_file()
        
        self.current_dataset_id = data.get('dataset_id')
        self.summary = data.get('summary', {})
        self.equipment_list = data.get('equipment_list', [])
        
        self.update_summary_cards()
        self.update_charts()
        self.update_table()
        self.fetch_history()
        
        QMessageBox.information(self, 'Success', data.get('message', 'File uploaded successfully!'))

    def on_upload_error(self, error_msg):
        """Handle upload error"""
        self.progress_bar.setVisible(False)
        self.select_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)
        QMessageBox.critical(self, 'Upload Error', error_msg)

    def fetch_history(self):
        """Fetch upload history from API"""
        try:
            response = requests.get(f'{API_BASE_URL}/history/', timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.history = data.get('datasets', [])
                self.update_history_list()
        except:
            pass  # Silently fail on history fetch

    def update_history_list(self):
        """Update the history list widget"""
        self.history_list.clear()
        for dataset in self.history:
            date = datetime.fromisoformat(dataset['uploaded_at'].replace('Z', '+00:00'))
            formatted_date = date.strftime('%b %d, %Y %H:%M')
            
            item = QListWidgetItem(
                f"📁 {dataset['name']}\n"
                f"    {formatted_date}\n"
                f"    {dataset['total_equipment']} items"
            )
            item.setData(Qt.UserRole, dataset['id'])
            self.history_list.addItem(item)

    def on_history_item_clicked(self, item):
        """Handle history item click"""
        dataset_id = item.data(Qt.UserRole)
        self.load_dataset(dataset_id)

    def show_history_context_menu(self, position):
        """Show context menu for history items"""
        from PyQt5.QtWidgets import QMenu
        item = self.history_list.itemAt(position)
        if item:
            menu = QMenu()
            load_action = menu.addAction('📂 Load Dataset')
            delete_action = menu.addAction('🗑️ Delete')
            
            action = menu.exec_(self.history_list.mapToGlobal(position))
            dataset_id = item.data(Qt.UserRole)
            
            if action == load_action:
                self.load_dataset(dataset_id)
            elif action == delete_action:
                self.delete_dataset(dataset_id)

    def delete_selected_history(self):
        """Delete the currently selected history item"""
        current_item = self.history_list.currentItem()
        if current_item:
            dataset_id = current_item.data(Qt.UserRole)
            self.delete_dataset(dataset_id)
        else:
            QMessageBox.warning(self, 'Warning', 'Please select a dataset to delete')

    def delete_dataset(self, dataset_id):
        """Delete a dataset from history"""
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            'Are you sure you want to delete this dataset?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                response = requests.delete(f'{API_BASE_URL}/datasets/{dataset_id}/delete/', timeout=10)
                if response.status_code == 200:
                    # Clear current view if deleted dataset was selected
                    if self.current_dataset_id == dataset_id:
                        self.current_dataset_id = None
                        self.summary = None
                        self.equipment_list = []
                        self.update_summary_cards()
                        self.chart_widget.clear_charts()
                        self.data_table.setRowCount(0)
                        self.report_btn.setEnabled(False)
                    
                    self.fetch_history()
                    QMessageBox.information(self, 'Success', 'Dataset deleted successfully')
                else:
                    QMessageBox.warning(self, 'Error', 'Failed to delete dataset')
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

    def load_dataset(self, dataset_id):
        """Load a specific dataset from the API"""
        try:
            response = requests.get(f'{API_BASE_URL}/datasets/{dataset_id}/', timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.current_dataset_id = dataset_id
                self.summary = {
                    'total_equipment': data.get('total_equipment'),
                    'avg_flowrate': data.get('avg_flowrate'),
                    'avg_pressure': data.get('avg_pressure'),
                    'avg_temperature': data.get('avg_temperature'),
                    'type_distribution': data.get('type_distribution_dict', {}),
                }
                self.equipment_list = data.get('equipment', [])
                
                self.update_summary_cards()
                self.update_charts()
                self.update_table()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load dataset: {e}')

    def update_summary_cards(self):
        """Update summary card values"""
        if not self.summary:
            # Clear all cards when no data
            for key in self.summary_cards:
                card = self.summary_cards.get(key)
                if card:
                    value_label = card.findChild(QLabel, 'valueLabel')
                    if value_label:
                        value_label.setText('-')
            return

        self.report_btn.setEnabled(True)

        updates = {
            'total': str(self.summary.get('total_equipment', 0)),
            'flowrate': f"{self.summary.get('avg_flowrate', 0):.2f}",
            'pressure': f"{self.summary.get('avg_pressure', 0):.2f}",
            'temperature': f"{self.summary.get('avg_temperature', 0):.2f}",
            'types': str(len(self.summary.get('type_distribution', {}))),
        }

        for key, value in updates.items():
            card = self.summary_cards.get(key)
            if card:
                value_label = card.findChild(QLabel, 'valueLabel')
                if value_label:
                    value_label.setText(value)

    def update_charts(self):
        """Update chart visualizations"""
        self.chart_widget.update_charts(self.summary, self.equipment_list)

    def update_table(self):
        """Update data table with equipment list"""
        self.data_table.setRowCount(len(self.equipment_list))
        
        for row, equipment in enumerate(self.equipment_list):
            self.data_table.setItem(row, 0, QTableWidgetItem(str(equipment.get('name', ''))))
            self.data_table.setItem(row, 1, QTableWidgetItem(str(equipment.get('equipment_type', ''))))
            self.data_table.setItem(row, 2, QTableWidgetItem(f"{equipment.get('flowrate', 0):.2f}"))
            self.data_table.setItem(row, 3, QTableWidgetItem(f"{equipment.get('pressure', 0):.2f}"))
            self.data_table.setItem(row, 4, QTableWidgetItem(f"{equipment.get('temperature', 0):.2f}"))

        self.data_table.resizeColumnsToContents()

    def generate_report(self):
        """Generate PDF report with authentication"""
        if not self.current_dataset_id:
            QMessageBox.warning(self, 'Warning', 'No dataset selected')
            return

        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username, password = dialog.get_credentials()
            
            if not username or not password:
                QMessageBox.warning(self, 'Warning', 'Please enter both username and password')
                return

            try:
                response = requests.post(
                    f'{API_BASE_URL}/report/{self.current_dataset_id}/',
                    json={'username': username, 'password': password},
                    timeout=30
                )

                if response.status_code == 200:
                    # Save PDF file
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, 'Save PDF Report', 
                        f'report_{self.current_dataset_id}.pdf',
                        'PDF Files (*.pdf)'
                    )
                    if file_path:
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        QMessageBox.information(self, 'Success', f'Report saved to {file_path}')
                else:
                    error = response.json().get('error', 'Failed to generate report')
                    QMessageBox.warning(self, 'Error', error)
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application-wide font
    font = QFont('Segoe UI', 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
