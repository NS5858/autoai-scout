import React, { useState } from "react";
import axios from "axios";

export default function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const backendUrl = import.meta.env.VITE_API_URL || "https://autoai-scout.onrender.com";

  const handleAnalyze = async () => {
    setError(null);
    setResult(null);
    if (!url.trim()) {
      setError("Bitte einen Fahrzeug-Link eingeben.");
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(`${backendUrl}/analyze`, { url });
      setResult(response.data);
    } catch (err) {
      setError("Analyse fehlgeschlagen – überprüfe den Link oder versuche es später erneut.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem", maxWidth: "700px", margin: "auto" }}>
      <h1 style={{ color: "#0078ff", textAlign: "center" }}>🚗 AutoAI Scout</h1>
      <p style={{ textAlign: "center" }}>Fahrzeuginserat eingeben und KI-Analyse starten</p>

      <div style={{ display: "flex", gap: "0.5rem", marginTop: "2rem" }}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.autoscout24.de/angebote/..."
          style={{
            flex: 1,
            padding: "0.8rem",
            borderRadius: "8px",
            border: "1px solid #ccc"
          }}
        />
        <button
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            padding: "0.8rem 1.2rem",
            backgroundColor: "#0078ff",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer"
          }}
        >
          {loading ? "Analysiere..." : "Start"}
        </button>
      </div>

      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}

      {result && (
        <div
          style={{
            marginTop: "2rem",
            padding: "1rem",
            border: "1px solid #ddd",
            borderRadius: "10px",
            background: "#fafafa"
          }}
        >
          <h3>Analyse-Ergebnis</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
