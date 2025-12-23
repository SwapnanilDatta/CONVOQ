import React, { useState } from 'react';
import { Upload } from 'lucide-react';


const FileUpload = ({ onFileSelect, isLoading }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState('');

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'text/plain') {
      setFileName(file.name);
      onFileSelect(file);
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      onFileSelect(file);
    }
  };

  return (
    <div className="file-upload-container">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`file-upload-box ${isDragging ? 'dragging' : ''} ${isLoading ? 'loading' : ''}`}
      >
        <Upload className={`upload-icon ${isDragging ? 'active' : ''}`} size={48} />
        <h3 className="upload-title">
          {fileName || 'Upload Chat Export'}
        </h3>
        <p className="upload-description">
          Drag and drop your chat file here, or click to browse
        </p>
        <input
          type="file"
          accept=".txt"
          onChange={handleFileInput}
          className="file-input"
          id="file-input"
          disabled={isLoading}
        />
        <label htmlFor="file-input" className="file-input-label">
          Choose File
        </label>
        {fileName && (
          <p className="selected-file">Selected: {fileName}</p>
        )}
      </div>
    </div>
  );
};

export default FileUpload;