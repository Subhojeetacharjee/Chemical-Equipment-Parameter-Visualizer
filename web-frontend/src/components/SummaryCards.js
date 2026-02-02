import React from 'react';

const SummaryCards = ({ summary }) => {
  if (!summary) return null;

  return (
    <div className="summary-grid">
      <div className="summary-card primary">
        <h3>Total Equipment</h3>
        <div className="value">{summary.total_equipment}</div>
      </div>
      <div className="summary-card">
        <h3>Avg Flowrate</h3>
        <div className="value">{summary.avg_flowrate?.toFixed(2) || '0.00'}</div>
      </div>
      <div className="summary-card">
        <h3>Avg Pressure</h3>
        <div className="value">{summary.avg_pressure?.toFixed(2) || '0.00'}</div>
      </div>
      <div className="summary-card">
        <h3>Avg Temperature</h3>
        <div className="value">{summary.avg_temperature?.toFixed(2) || '0.00'}</div>
      </div>
      <div className="summary-card">
        <h3>Equipment Types</h3>
        <div className="value">
          {summary.type_distribution 
            ? Object.keys(summary.type_distribution).length 
            : 0}
        </div>
      </div>
    </div>
  );
};

export default SummaryCards;
