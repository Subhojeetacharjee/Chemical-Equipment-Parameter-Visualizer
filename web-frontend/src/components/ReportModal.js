import React, { useState } from 'react';

const ReportModal = ({ isOpen, onClose, onGenerate, isLoading }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }
    
    try {
      await onGenerate(username, password);
      setUsername('');
      setPassword('');
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to generate report');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>🔐 Generate PDF Report</h3>
        <p style={{ marginBottom: '20px', color: '#64748b' }}>
          Enter your credentials to generate the report
        </p>
        
        {error && (
          <div className="message error" style={{ marginBottom: '15px' }}>
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
          
          <div className="modal-buttons">
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={isLoading}
            >
              {isLoading ? 'Generating...' : 'Generate PDF'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReportModal;
