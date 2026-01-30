import React, { useState } from 'react';
import { Upload, FileText, CheckCircle } from 'lucide-react';

const FileUpload = ({ onFileSelect, isLoading }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState('');
  const [dateFormat, setDateFormat] = useState('auto');

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
      onFileSelect(file, dateFormat);
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      onFileSelect(file, dateFormat);
    }
  };

  return (
    <div className="relative w-full max-w-md mx-auto group">
      {/* Glow effect */}
      <div className={`absolute -inset-0.5 bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl blur opacity-20 group-hover:opacity-60 transition duration-500 ${isDragging ? 'opacity-100' : ''}`}></div>

      <div
        className={`relative flex flex-col items-center justify-center p-10 bg-slate-900 rounded-2xl border-2 border-dashed transition-all duration-300
            ${isDragging ? 'border-purple-500 bg-slate-800' : 'border-slate-700 bg-slate-900'}
            ${isLoading ? 'opacity-50 pointer-events-none' : ''}
         `}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {/* Date Format Select */}
        <div className="absolute top-4 right-4 z-20">
          <select
            value={dateFormat}
            onChange={(e) => setDateFormat(e.target.value)}
            className="bg-slate-800 text-xs text-slate-300 border border-slate-700 rounded-lg px-2 py-1 focus:ring-1 focus:ring-purple-500 outline-none cursor-pointer hover:bg-slate-700 transition-colors"
            disabled={isLoading}
          >
            <option value="auto">Auto Detect</option>
            <option value="mm/dd/yyyy">MM/DD/YYYY (12/31/2024)</option>
            <option value="dd/mm/yyyy">DD/MM/YYYY (31/12/2024)</option>
            <option value="mm/dd/yy">MM/DD/YY (12/31/24)</option>
            <option value="dd/mm/yy">DD/MM/YY (31/12/24)</option>
          </select>
        </div>
        <div className={`w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center mb-4 transition-transform duration-300 ${isDragging ? 'scale-110' : ''}`}>
          {fileName ? <CheckCircle className="text-green-500" size={32} /> : <Upload className="text-purple-400" size={32} />}
        </div>

        <h3 className="text-xl font-bold mb-2">
          {fileName || 'Upload Chat Export'}
        </h3>

        <p className="text-slate-400 text-center text-sm mb-6 max-w-xs">
          {fileName ? 'Ready to analyze!' : 'Drag & drop .txt file here, or click to browse'}
        </p>

        <input
          type="file"
          accept=".txt"
          onChange={handleFileInput}
          className="hidden"
          id="file-input"
          disabled={isLoading}
        />
        <label
          htmlFor="file-input"
          className="px-6 py-2 rounded-full bg-white text-slate-950 font-semibold text-sm hover:bg-slate-200 cursor-pointer transition-all shadow-lg hover:shadow-white/25"
        >
          {fileName ? 'Change File' : 'Choose File'}
        </label>
      </div>

      <div className="mt-6 text-center">
        <p className="text-slate-500 text-xs font-medium uppercase tracking-wider mb-2">How to export from WhatsApp</p>
        <div className="inline-block bg-slate-900/50 rounded-lg px-4 py-3 border border-slate-800 text-slate-400 text-sm">
          Open Chat &gt; Tap on three dots &gt; More &gt; Export Chat &gt; Extract Chat &gt; <span className="text-purple-400 font-semibold">Without Media</span>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;