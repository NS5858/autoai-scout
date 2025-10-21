import React, { useState } from "react";
import { analyzeUrl } from "./api";
import "./styles.css";

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    if (!url.trim()) {
      setError("Bitte gib einen gültigen Fahrzeuglink ein.");
      return;
    }

    setError("");
    setLoading(true);
    setResult(null);

    try {
      const data = await analyzeUrl(url);
      if (data.success) {
        setResult(data.data);
      } else {
        setError(data.message || "Analyse fehlgeschlagen.");
      }
    } catch (err) {
      setError("Analyse fehlgeschlagen – bitte überprüfe den Link oder versuche es später erneut.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>🚗 <span className="highlight">AutoAI Scout</span></h1>
      <p className="subtitle">Fahrzeuginserat eingeben und KI-Analyse starten</p>

      <div className="input-group">
        <input
          type="text"
          placeholder="https://www.autoscout24.de/..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button onClick={handleAnalyze} disabled={loading}>
          {loading ? "Analysiere..." : "Start"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <h2>Analyse-Ergebnis</h2>
          <p><strong>Plattform:</strong> {result.details.platform}</p>
          <p><strong>Fahrzeug:</strong> {result.details.title}</p>
          <p><strong>Erstzulassung:</strong> {result.details.year}</p>
          <p><strong>Kilometerstand:</strong> {result.details.mileage.toLocaleString()} km</p>
          <p><strong>Angebotspreis:</strong> {result.details.original_price.toLocaleString()} €</p>
          <hr />
          <p className="ai">
            Geschätzter Marktwert: <span className="value">{result.estimated_value.toLocaleString()} €</span>
          </p>
          <p className="confidence">
            KI-Zuverlässigkeit: <span className="value">{result.ai_confidence}%</span>
          </p>
        </div>
      )}
    </div>
  );
}
