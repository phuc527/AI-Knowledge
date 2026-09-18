import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  async function uploadFile() {
    if (!file) {
      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      alert(`Uploaded ${data.file}. Chunks: ${data.chunks}`);
    } finally {
      setLoading(false);
    }
  }

  async function askQuestion() {
    if (!question.trim()) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/chat?question=${encodeURIComponent(question)}`,
        {
          method: "POST",
        },
      );

      const data = await response.json();

      setAnswer(data.answer);
      setSources(data.sources);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        maxWidth: 900,
        margin: "40px auto",
        fontFamily: "Arial",
      }}
    >
      <h1>AI Knowledge Assistant</h1>

      <section>
        <h2>Upload document</h2>

        <input
          type="file"
          accept=".pdf"
          onChange={(event) => {
            setFile(event.target.files[0]);
          }}
        />

        <button
          onClick={uploadFile}
          disabled={loading || !file}
          style={{ marginLeft: 10 }}
        >
          Upload PDF
        </button>
      </section>

      <hr />

      <section>
        <h2>Ask AI</h2>

        <textarea
          value={question}
          onChange={(event) => {
            setQuestion(event.target.value);
          }}
          placeholder="Ask something about your documents..."
          rows={5}
          style={{
            width: "100%",
            padding: 10,
            boxSizing: "border-box",
          }}
        />

        <button
          onClick={askQuestion}
          disabled={loading}
          style={{ marginTop: 10 }}
        >
          Ask AI
        </button>
      </section>

      {loading && <p>Processing...</p>}

      {answer && (
        <section>
          <h2>Answer</h2>

          <div
            style={{
              padding: 20,
              background: "#f5f5f5",
              borderRadius: 8,
              whiteSpace: "pre-wrap",
            }}
          >
            {answer}
          </div>
        </section>
      )}

      {sources.length > 0 && (
        <section>
          <h2>Sources</h2>

          <ul>
            {sources.map((source, index) => (
              <li key={index}>
                {source.file} — page {source.page}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

export default App;
