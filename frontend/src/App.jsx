import { useState } from "react";
import { uploadChatFile, analyzeReplyTime } from "./api/chatApi";
import FileUpload from "./components/FileUpload";

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileAction = async (file) => {
    if (!file) return;
    setLoading(true);

    try {
      // Run both calls
      const uploadData = await uploadChatFile(file);
      setResult(uploadData);

      const replyData = await analyzeReplyTime(file);
      console.log("Reply Analysis:", replyData);
    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>CONVOQ</h1>
      
      <FileUpload onUpload={handleFileAction} />

      {loading && <p>Processing chat...</p>}

      {result && (
        <div style={{ marginTop: "20px" }}>
          <h3>Total Messages: {result.total_messages}</h3>
          <pre style={{ maxHeight: "300px", overflow: "auto", background: "#ff0000ff" }}>
            {JSON.stringify(result.messages, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;