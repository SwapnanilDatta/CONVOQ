export default function FileUpload({ onUpload }) {
  return (
    <div className="upload-section">
      <input 
        type="file" 
        accept=".txt" 
        onChange={(e) => onUpload(e.target.files[0])} 
      />
    </div>
  );
}