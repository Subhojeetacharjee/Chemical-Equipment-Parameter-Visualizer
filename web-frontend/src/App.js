import React, { useState, useEffect, useCallback } from 'react';
import apiService from './services/api';
import FileUpload from './components/FileUpload';
import SummaryCards from './components/SummaryCards';
import Charts from './components/Charts';
import DataTable from './components/DataTable';
import History from './components/History';
import ReportModal from './components/ReportModal';

function App() {
  const [summary, setSummary] = useState(null);
  const [equipmentList, setEquipmentList] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isReportLoading, setIsReportLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showReportModal, setShowReportModal] = useState(false);
  const [activeTab, setActiveTab] = useState('charts');

  // Fetch history on component mount
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await apiService.getHistory();
      setHistory(data.datasets || []);
      
      // Load latest dataset if available
      if (data.datasets && data.datasets.length > 0) {
        await loadDataset(data.datasets[0].id);
      }
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const loadDataset = async (datasetId) => {
    try {
      setIsLoading(true);
      const data = await apiService.getDataset(datasetId);
      
      setSummary({
        total_equipment: data.total_equipment,
        avg_flowrate: data.avg_flowrate,
        avg_pressure: data.avg_pressure,
        avg_temperature: data.avg_temperature,
        type_distribution: data.type_distribution_dict,
      });
      setEquipmentList(data.equipment || []);
      setSelectedDatasetId(datasetId);
    } catch (error) {
      showMessage('error', 'Failed to load dataset');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    try {
      setIsLoading(true);
      setMessage({ type: '', text: '' });
      
      const data = await apiService.uploadCSV(file);
      
      setSummary(data.summary);
      setEquipmentList(data.equipment_list || []);
      setSelectedDatasetId(data.dataset_id);
      
      showMessage('success', data.message);
      
      // Refresh history
      await fetchHistory();
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to upload file';
      showMessage('error', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectDataset = useCallback((datasetId) => {
    loadDataset(datasetId);
  }, []);

  const handleDeleteDataset = async (datasetId) => {
    if (!window.confirm('Are you sure you want to delete this dataset?')) {
      return;
    }
    
    try {
      await apiService.deleteDataset(datasetId);
      showMessage('success', 'Dataset deleted successfully');
      
      // Clear current data if deleted dataset was selected
      if (selectedDatasetId === datasetId) {
        setSummary(null);
        setEquipmentList([]);
        setSelectedDatasetId(null);
      }
      
      // Refresh history
      await fetchHistory();
    } catch (error) {
      showMessage('error', 'Failed to delete dataset');
    }
  };

  const handleGenerateReport = async (username, password) => {
    if (!selectedDatasetId) {
      throw new Error('No dataset selected');
    }
    
    try {
      setIsReportLoading(true);
      const blob = await apiService.generateReport(selectedDatasetId, username, password);
      
      // Download PDF
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${selectedDatasetId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      showMessage('success', 'Report generated successfully');
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to generate report';
      throw new Error(errorMessage);
    } finally {
      setIsReportLoading(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🧪 Chemical Equipment Visualizer</h1>
        <p>Upload, analyze, and visualize chemical equipment parameters</p>
      </header>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="main-content">
        {/* Left Sidebar */}
        <div className="sidebar">
          <div className="card">
            <h2>📤 Upload Data</h2>
            <FileUpload onFileUpload={handleFileUpload} isLoading={isLoading} />
          </div>

          <div className="card" style={{ marginTop: '20px' }}>
            <h2>📚 Upload History</h2>
            <History
              history={history}
              onSelectDataset={handleSelectDataset}
              selectedDatasetId={selectedDatasetId}
              onDeleteDataset={handleDeleteDataset}
            />
          </div>
        </div>

        {/* Main Content Area */}
        <div className="content">
          <div className="card">
            <h2>📊 Summary Statistics</h2>
            <SummaryCards summary={summary} />
            
            {summary && (
              <button
                className="btn btn-primary"
                onClick={() => setShowReportModal(true)}
                style={{ marginTop: '15px' }}
              >
                📄 Generate PDF Report
              </button>
            )}
          </div>

          {/* Tab Navigation */}
          <div className="card" style={{ marginTop: '20px' }}>
            <div style={{ marginBottom: '20px' }}>
              <button
                className={`btn ${activeTab === 'charts' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('charts')}
                style={{ marginRight: '10px' }}
              >
                📈 Charts
              </button>
              <button
                className={`btn ${activeTab === 'table' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('table')}
              >
                📋 Data Table
              </button>
            </div>

            {isLoading ? (
              <div className="loading">
                <div className="spinner"></div>
                <p>Loading data...</p>
              </div>
            ) : activeTab === 'charts' ? (
              <Charts summary={summary} equipmentList={equipmentList} />
            ) : (
              <DataTable equipmentList={equipmentList} />
            )}
          </div>
        </div>
      </div>

      <ReportModal
        isOpen={showReportModal}
        onClose={() => setShowReportModal(false)}
        onGenerate={handleGenerateReport}
        isLoading={isReportLoading}
      />
    </div>
  );
}

export default App;
