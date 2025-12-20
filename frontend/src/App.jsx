import { useState } from "react";
import { uploadChatFile, analyzeReplyTime, analyzeSentiment } from "./api/chatApi";
import FileUpload from "./components/FileUpload";
import SentimentAnalyzer from "./components/SentimentAnalysis";

function App() {
  const [chatData, setChatData] = useState(null);
  const [sentimentData, setSentimentData] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileAction = async (file) => {
    if (!file) return;
    setLoading(true);

    try {
      const [uploadRes, replyRes, sentimentRes] = await Promise.all([
        uploadChatFile(file),
        analyzeReplyTime(file),
        analyzeSentiment(file)
      ]);

      setChatData(uploadRes);
      setSentimentData(sentimentRes.timeline || []);
      
      console.log("Reply Analysis:", replyRes);
    } catch (error) {
      console.error("Processing failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>CONVOQ</h1>
      
      <FileUpload onUpload={handleFileAction} />

      {loading && <p>Processing everything...</p>}

      <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
     
        {chatData && (
          <div style={{ flex: 1 }}>
            <h3>Total Messages: {chatData.total_messages}</h3>
            <pre style={{ maxHeight: "400px", overflow: "auto", background: "#f40000ff", padding: "10px" }}>
              {JSON.stringify(chatData.messages, null, 2)}
            </pre>
          </div>
        )}

        
        {sentimentData.length > 0 && (
          <div style={{ flex: 1 }}>
            <SentimentAnalyzer timeline={sentimentData} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;