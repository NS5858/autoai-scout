import { useState } from "react";
import { analyzeText } from "./api";

function App() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await analyzeText(input);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "Arial" }}>
      <h1 style={{ textAlign: "center", color: "#0077ff" }}>AutoAI Scout</h1>

      <textarea
        rows={4}
        placeholder="Beschreibe dein Fahrzeug hier..."
        style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      <button
        onClick={handleAnalyze}
        style={{
          width: "100%",
          padding: "10px",
          backgroundColor: "#0077ff",
          color: "white",
          border: "none",
          cursor: "pointer",
        }}
      >
        {loading ? "Analysiere..." : "Analysieren"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div
          style={{
            marginTop: "20px",
            background: "#f7f7f7",
            padding: "10px",
            borderRadius: "8px",
          }}
        >
          <h3>Ergebnis</h3>
          <p><strong>Marke:</strong> {result.brand}</p>
          <p><strong>Modell:</strong> {result.model}</p>
          <p><strong>Zustand:</strong> {result.condition}</p>
          <p><strong>Preis:</strong> {result.estimated_price} €</p>
          <p><strong>Vertrauen:</strong> {result.confidence}</p>
        </div>
      )}
    </div>
  );
}

export default App;
