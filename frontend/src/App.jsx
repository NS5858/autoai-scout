import React, { useState } from "react";
import { analyzeUrl } from "./api";
import "./styles.css";

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState(null);

  const handleAnalyze = async () => {
    if (!url.trim()) {
      setError("Bitte gib einen gültigen Fahrzeuglink ein.");
      return;
    }
    setError("");
    setLoading(true);
    setAnalysis(null);
    try {
      const res = await analyzeUrl(url);
      if (res && (res.data || res.vehicle)) {
        // v1-Fallback oder v2-Struktur
        const payload = res.data ?? res; 
        setAnalysis(payload);
      } else {
        setError(res?.message || "Analyse fehlgeschlagen.");
      }
    } catch (e) {
      setError("Analyse fehlgeschlagen – Link prüfen oder später erneut versuchen.");
    } finally {
      setLoading(false);
    }
  };

  const V = analysis?.vehicle;
  const M = analysis?.market;
  const D = analysis?.demand;
  const W = analysis?.weaknesses;

  return (
    <div className="container">
      <h1>🚗 <span className="highlight">AutoAI Scout</span></h1>
      <p className="subtitle">Fahrzeuginserat einfügen – KI-Detektivmodus startet</p>

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

      {analysis && (
        <div className="result">
          <h2>Analyse-Ergebnis</h2>

          {V && (
            <div className="card">
              <h3>Fahrzeug</h3>
              <p><strong>Plattform:</strong> {V.platform}</p>
              <p><strong>Modell:</strong> {V.title}</p>
              <p><strong>Erstzulassung:</strong> {V.year}</p>
              <p><strong>Kilometerstand:</strong> {Number(V.mileage ?? 0).toLocaleString()} km</p>
              <p><strong>Angebotspreis:</strong> {Number(V.price ?? 0).toLocaleString()} €</p>
            </div>
          )}

          {M && (
            <div className="card">
              <h3>Marktbewertung</h3>
              <p><strong>Durchschnittlicher Marktwert:</strong> {Number(M.average_market_value ?? 0).toLocaleString()} €</p>
              <p><strong>Preisabweichung:</strong> {Number(M.price_difference ?? 0).toLocaleString()} €</p>
              <p><strong>Einschätzung:</strong> {M.valuation}</p>
              <p><strong>Vergleichsdaten:</strong> {M.comparables}</p>
            </div>
          )}

          {D && (
            <div className="card">
              <h3>Nachfrage</h3>
              <p><strong>Score:</strong> {D.score}</p>
              <p><strong>Niveau:</strong> {D.demand_level}</p>
            </div>
          )}

          {W && (
            <div className="card">
              <h3>Typische Schwachstellen</h3>
              <ul>
                {W.map((w, i) => <li key={i}>{w}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
