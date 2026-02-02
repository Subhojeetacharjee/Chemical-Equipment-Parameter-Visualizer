import React from 'react';

const DataTable = ({ equipmentList }) => {
  if (!equipmentList || equipmentList.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📋</div>
        <h3>No Equipment Data</h3>
        <p>Upload a CSV file to view data</p>
      </div>
    );
  }

  return (
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Flowrate</th>
            <th>Pressure</th>
            <th>Temperature</th>
          </tr>
        </thead>
        <tbody>
          {equipmentList.map((equipment, index) => (
            <tr key={equipment.id || index}>
              <td>{equipment.name}</td>
              <td>{equipment.equipment_type}</td>
              <td>{equipment.flowrate?.toFixed(2)}</td>
              <td>{equipment.pressure?.toFixed(2)}</td>
              <td>{equipment.temperature?.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
