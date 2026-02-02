import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const FileUpload = ({ onFileUpload, isLoading }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
    disabled: isLoading,
  });

  return (
    <div className="upload-section">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-icon">📁</div>
        {isDragActive ? (
          <p>Drop the CSV file here...</p>
        ) : (
          <>
            <p>Drag & drop a CSV file here, or click to select</p>
            <p className="file-types">Supports: .csv files</p>
          </>
        )}
        {acceptedFiles.length > 0 && (
          <p style={{ marginTop: '10px', color: '#667eea', fontWeight: '600' }}>
            Selected: {acceptedFiles[0].name}
          </p>
        )}
      </div>
      {acceptedFiles.length > 0 && (
        <button 
          className="upload-btn" 
          onClick={() => onFileUpload(acceptedFiles[0])}
          disabled={isLoading}
        >
          {isLoading ? 'Uploading...' : 'Upload & Analyze'}
        </button>
      )}
    </div>
  );
};

export default FileUpload;
