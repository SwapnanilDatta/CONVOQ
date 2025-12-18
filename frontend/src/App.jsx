import { useState } from "react"

function App() {
  const [result, setResult] = useState(null)

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append("file", file)

    const res = await fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      body: formData
    })

    const data = await res.json()
    setResult(data)
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>CONVOQ</h1>

      <input type="file" accept=".txt" onChange={handleUpload} />

      {result && (
        <>
          <h3>Total Messages: {result.total_messages}</h3>

          <pre style={{ maxHeight: "300px", overflow: "auto" }}>
            {JSON.stringify(result.messages, null, 2)}
          </pre>
        </>
      )}
    </div>
  )
}

export default App
