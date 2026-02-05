import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Bar, Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  ChartDataLabels
);

const Charts = ({ summary, equipmentList }) => {
  if (!summary || !equipmentList || equipmentList.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📊</div>
        <h3>No Data to Display</h3>
        <p>Upload a CSV file to see charts</p>
      </div>
    );
  }

  // Type Distribution Pie Chart - Modern Doughnut Style
  const typeDistribution = summary.type_distribution || {};
  const totalEquipment = Object.values(typeDistribution).reduce((a, b) => a + b, 0);
  
  const pieData = {
    labels: Object.keys(typeDistribution),
    datasets: [
      {
        data: Object.values(typeDistribution),
        backgroundColor: [
          '#667eea',
          '#764ba2',
          '#f472b6',
          '#10b981',
          '#f59e0b',
          '#ef4444',
          '#06b6d4',
          '#8b5cf6',
        ],
        borderWidth: 0,
        hoverBorderWidth: 3,
        hoverBorderColor: '#fff',
        spacing: 2,
      },
    ],
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '55%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          usePointStyle: true,
          pointStyle: 'circle',
          font: {
            size: 12,
            weight: '500',
          },
          generateLabels: (chart) => {
            const data = chart.data;
            if (data.labels.length && data.datasets.length) {
              return data.labels.map((label, i) => {
                const value = data.datasets[0].data[i];
                return {
                  text: `${label} (${value})`,
                  fillStyle: data.datasets[0].backgroundColor[i],
                  strokeStyle: data.datasets[0].backgroundColor[i],
                  lineWidth: 0,
                  pointStyle: 'circle',
                  hidden: false,
                  index: i,
                };
              });
            }
            return [];
          },
        },
      },
      title: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: { size: 14, weight: 'bold' },
        bodyFont: { size: 13 },
        cornerRadius: 8,
        callbacks: {
          label: (context) => {
            const value = context.raw;
            const percentage = ((value / totalEquipment) * 100).toFixed(1);
            return ` ${context.label}: ${value} units (${percentage}%)`;
          },
        },
      },
      datalabels: {
        color: '#fff',
        font: {
          weight: 'bold',
          size: 14,
        },
        formatter: (value, context) => {
          const percentage = ((value / totalEquipment) * 100).toFixed(0);
          return percentage >= 8 ? `${value}\n(${percentage}%)` : '';
        },
        textAlign: 'center',
      },
    },
  };

  // Parameters Bar Chart
  const barData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [
      {
        label: 'Average Values',
        data: [
          summary.avg_flowrate || 0,
          summary.avg_pressure || 0,
          summary.avg_temperature || 0,
        ],
        backgroundColor: [
          'rgba(102, 126, 234, 0.8)',
          'rgba(118, 75, 162, 0.8)',
          'rgba(16, 185, 129, 0.8)',
        ],
        borderColor: [
          '#667eea',
          '#764ba2',
          '#10b981',
        ],
        borderWidth: 2,
        borderRadius: 8,
      },
    ],
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: {
        top: 30,
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      datalabels: {
        anchor: 'end',
        align: 'top',
        color: '#374151',
        font: {
          weight: 'bold',
          size: 12,
        },
        formatter: (value) => value.toFixed(1),
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  // Equipment Parameters Line Chart (first 10 equipment)
  const limitedEquipment = equipmentList.slice(0, 10);
  const lineData = {
    labels: limitedEquipment.map(eq => eq.name.substring(0, 15)),
    datasets: [
      {
        label: 'Flowrate',
        data: limitedEquipment.map(eq => eq.flowrate),
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Pressure',
        data: limitedEquipment.map(eq => eq.pressure),
        borderColor: '#764ba2',
        backgroundColor: 'rgba(118, 75, 162, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Temperature',
        data: limitedEquipment.map(eq => eq.temperature),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
        },
      },
      datalabels: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45,
        },
      },
    },
  };

  // Type Distribution Bar Chart
  const typeBarData = {
    labels: Object.keys(typeDistribution),
    datasets: [
      {
        label: 'Equipment Count',
        data: Object.values(typeDistribution),
        backgroundColor: 'rgba(102, 126, 234, 0.8)',
        borderColor: '#667eea',
        borderWidth: 2,
        borderRadius: 8,
      },
    ],
  };

  const typeBarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: {
        top: 30,
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      datalabels: {
        anchor: 'end',
        align: 'top',
        color: '#374151',
        font: {
          weight: 'bold',
          size: 12,
        },
        formatter: (value) => value,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  return (
    <div className="charts-grid">
      <div className="chart-container">
        <div className="chart-header">
          <h3>📊 Equipment Type Distribution</h3>
          <span className="chart-subtitle">Total: {totalEquipment} units</span>
        </div>
        <div style={{ height: '320px', padding: '10px' }}>
          <Doughnut data={pieData} options={pieOptions} />
        </div>
      </div>
      
      <div className="chart-container">
        <h3>📈 Average Parameter Values</h3>
        <div style={{ height: '300px' }}>
          <Bar data={barData} options={barOptions} />
        </div>
      </div>
      
      <div className="chart-container">
        <h3>📉 Equipment Parameters Trend</h3>
        <div style={{ height: '300px' }}>
          <Line data={lineData} options={lineOptions} />
        </div>
      </div>
      
      <div className="chart-container">
        <h3>🏭 Equipment Count by Type</h3>
        <div style={{ height: '300px' }}>
          <Bar data={typeBarData} options={typeBarOptions} />
        </div>
      </div>
    </div>
  );
};

export default Charts;
