import { useMemo, useState } from "react"; // useState let's us store UI state, useMemo computes API_BASE once on load instead of on every render
import "./App.css";

export default function App() {
  const [level, setLevel] = useState("simple"); // simple or very_simple
  const [text, setText] = useState(""); // what the pastes in or uploads, and what they edit before hitting "Simplify"
  const [simplified, setSimplified] = useState(""); // what the API returns as the simplified version
  const [notes, setNotes] = useState([]); // any notes the API returns about what it changed and why
  const [loading, setLoading] = useState(false); // disables the + button and shows "Simplifying…" while waiting for the API response
  const [error, setError] = useState(""); // shows user-friendly error messages

  // Local dev default. Later I need to set this to my deployed API URL.
  const API_BASE = useMemo(() => {
    return import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
  }, []);

  async function handleSimplify() { // validates input which must not be empty
    setError("");
    setSimplified("");
    setNotes([]);

    if (!text.trim()) {
      setError("Paste some text or upload a file first.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/simplify`, { // calls the API, and handles errors
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, level }),
      });

      if (!res.ok) { // if the response is not a 2xx, read the error message from the response body and show it to the user
        const msg = await res.text();
        throw new Error(`API error: ${res.status} ${msg}`);
      }

      const data = await res.json(); // if the response is a 2xx, parse the JSON and update the simplified text and notes in the UI
      setSimplified(data.simplified || "");
      setNotes(data.notes || []);
    } catch (e) {
      setError(e.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  // FormnData is how browsers send files.
async function handleFileUpload(file) {
  setError("");
  setSimplified("");
  setNotes([]);

  if (!file) return;

  if (!file.name.toLowerCase().endsWith(".pdf")) {
    setError("Please upload a PDF file.");
    return;
  }

  setLoading(true);
  try {
    const form = new FormData();
    form.append("file", file);

    // Send level as a query param
    const res = await fetch(`${API_BASE}/upload?level=${encodeURIComponent(level)}`, {
      method: "POST",
      body: form,
    });

    if (!res.ok) {
      const msg = await res.text();
      throw new Error(`API error: ${res.status} ${msg}`);
    }

    const data = await res.json();
    setText(data.original || "");
    setSimplified(data.simplified || "");
  } catch (e) {
    setError(e.message || "Upload failed.");
  } finally {
    setLoading(false);
  }
}

  function downloadSimplified() { // creates a downloadable .txt file from the simplified text and triggers a download in the browser
    const blob = new Blob([simplified], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "easyread.txt";
    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(url);
  }

  return (
    <div className="page"> 
      <header className="header">
        <div>
          <h1>EasyRead</h1>
          <p className="subtitle">
            Make complex English easier to read. Paste text or upload a file, then download the easy version.
          </p>
        </div>

        <a
          className="support"
          href="https://www.buymeacoffee.com/"
          target="_blank"
          rel="noreferrer"
          title="Add my real link later"
        >
          Buy me a drink
        </a>
      </header>

      <div className="controls">
        <label className="label">
          Reading level
          <select value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value="simple">Simple</option>
            <option value="very_simple">Very simple</option>
          </select>
        </label>

        <label className="upload">
          Upload (Upload a PDF)
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => handleFileUpload(e.target.files?.[0])}
          />
        </label>

        <button className="primary" onClick={handleSimplify} disabled={loading}>
          {loading ? "Simplifying…" : "Simplify"}
        </button>
      </div>

      <p className="disclaimer">
        Disclaimer: This tool rewrites text to improve readability. Use at your own risk and always verify important details.
      </p>

      {error && <div className="error">{error}</div>}

      <div className="grid">
        <section className="card">
          <h2>Original</h2>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste text here (or upload a PDF)…"
          />
        </section>

        <section className="card">
          <div className="cardHeader">
            <h2>Easy version</h2>
            <button
              className="secondary"
              onClick={downloadSimplified}
              disabled={!simplified}
              title={!simplified ? "Generate an easy version first" : "Download"}
            >
              Download
            </button>
          </div>

          <textarea
            value={simplified}
            readOnly
            placeholder="Your easy-to-read version will appear here…"
          />

        </section>
      </div>

      <footer className="footer">EasyRead • React + FastAPI</footer>
    </div>
  );
}