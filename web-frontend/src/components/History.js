import React from 'react';

const History = ({ history, onSelectDataset, selectedDatasetId, onDeleteDataset }) => {
  if (!history || history.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📚</div>
        <h3>No Upload History</h3>
        <p>Upload your first CSV file</p>
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="history-list">
      {history.map((dataset) => (
        <div
          key={dataset.id}
          className={`history-item ${selectedDatasetId === dataset.id ? 'active' : ''}`}
          onClick={() => onSelectDataset(dataset.id)}
        >
          <div className="history-item-info">
            <h4>{dataset.name}</h4>
            <p>{formatDate(dataset.uploaded_at)}</p>
          </div>
          <div className="history-item-stats">
            <div>{dataset.total_equipment} items</div>
            <button
              className="btn btn-danger"
              style={{ marginTop: '8px', padding: '5px 10px', fontSize: '0.75rem' }}
              onClick={(e) => {
                e.stopPropagation();
                onDeleteDataset(dataset.id);
              }}
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default History;
