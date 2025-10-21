import { useState } from "react";
import { analyzeUrl, health } from "./api";

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [resp, setResp] = useState(null);
  const [err, setErr] = useState("");

  const runHealth = async () => {
    setErr("");
    setResp(null);
    setLoading(true);
    try {
      const h = await health();
      setResp({ health: h });
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  const runAnalyze = async () => {
    setErr("");
    setResp(null);
    setLoading(true);
    try {
      const data = await analyzeUrl(url.trim());
      setResp({ analyze: data });
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: "0 16px", fontFamily: "Inter, system-ui, Arial" }}>
      <h1 style={{ marginBottom: 12 }}>AutoAI Scout</h1>
      <p style={{ color: "#555", marginTop: 0 }}>
        Gib einen Inserat-Link ein (AutoScout24, mobile.de, eBay Kleinanzeigen). Der Backend-Service ist: <code>{import.meta.env.VITE_API_BASE}</code>
      </p>

      <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.autoscout24.de/..."
          style={{
            flex: 1,
            padding: "12px 14px",
            borderRadius: 12,
            border: "1px solid #ccc",
            fontSize: 16,
          }}
        />
        <button
          onClick={runAnalyze}
          disabled={!url || loading}
          style={{
            padding: "12px 16px",
            borderRadius: 12,
            border: "none",
            background: "#111827",
            color: "white",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          {loading ? "Analysiere..." : "Analysieren"}
        </button>
        <button
          onClick={runHealth}
          disabled={loading}
          style={{
            padding: "12px 16px",
            borderRadius: 12,
            border: "1px solid #ccc",
            background: "white",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Health
        </button>
      </div>

      {err && (
        <div style={{ marginTop: 16, padding: 12, borderRadius: 12, border: "1px solid #fda4af", background: "#fff1f2", color: "#be123c" }}>
          Fehler: {err}
        </div>
      )}

      {resp?.health && (
        <div style={{ marginTop: 16, padding: 16, borderRadius: 12, border: "1px solid #d1fae5", background: "#ecfeff" }}>
          <h3 style={{ marginTop: 0 }}>Health</h3>
          <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(resp.health, null, 2)}</pre>
        </div>
      )}

      {resp?.analyze && <AnalyzeResult data={resp.analyze} />}
    </div>
  );
}

function AnalyzeResult({ data }) {
  const { listing, valuation } = data || {};
  const v = listing?.vehicle || {};
  const seller = listing?.seller || {};
  const imgs = listing?.images || [];

  return (
    <div style={{ marginTop: 24, display: "grid", gap: 16 }}>
      <section style={card()}>
        <h3 style={{ marginTop: 0, marginBottom: 8 }}>Inserat</h3>
        <div style={{ display: "grid", gap: 6 }}>
          <Row k="Quelle" v={listing?.domain} />
          <Row k="Titel" v={listing?.title} />
          <Row k="URL" v={<a href={listing?.url} target="_blank" rel="noreferrer">{listing?.url}</a>} />
          <Row k="Preis (EUR)" v={fmt(listing?.price_eur)} />
          <Row k="Beschreibung" v={listing?.description} />
        </div>
      </section>

      <section style={card()}>
        <h3 style={{ marginTop: 0, marginBottom: 8 }}>Fahrzeug</h3>
        <div style={{ display: "grid", gap: 6, gridTemplateColumns: "repeat(2, minmax(0, 1fr))" }}>
          <Row k="Marke" v={v.make} />
          <Row k="Modell" v={v.model} />
          <Row k="Baujahr" v={v.year} />
          <Row k="km" v={v.mileage_km?.toLocaleString?.("de-DE")} />
          <Row k="Leistung (kW)" v={v.power_kw} />
          <Row k="Kraftstoff" v={v.fuel_type} />
          <Row k="Getriebe" v={v.transmission} />
          <Row k="Farbe" v={v.color} />
          <Row k="Karosserie" v={v.body_type} />
          <Row k="VIN" v={v.vin} />
        </div>
      </section>

      <section style={card()}>
        <h3 style={{ marginTop: 0, marginBottom: 8 }}>Bewertung</h3>
        <div style={{ display: "grid", gap: 6, gridTemplateColumns: "repeat(3, minmax(0, 1fr))" }}>
          <Row k="Schätzwert" v={fmt(valuation?.estimated_value_eur)} />
          <Row k="Konfidenz min" v={fmt(valuation?.conf_low_eur)} />
          <Row k="Konfidenz max" v={fmt(valuation?.conf_high_eur)} />
        </div>
        <div style={{ marginTop: 8, color: "#555" }}>
          <small>Methode: {valuation?.method} • {valuation?.notes}</small>
        </div>
      </section>

      {imgs?.length > 0 && (
        <section style={card()}>
          <h3 style={{ marginTop: 0, marginBottom: 8 }}>Bilder</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 8 }}>
            {imgs.map((img, i) => (
              <img key={i} src={img.url} alt={`Bild ${i+1}`} style={{ width: "100%", borderRadius: 8, objectFit: "cover", aspectRatio: "16 / 10" }} />
            ))}
          </div>
        </section>
      )}

      <section style={card()}>
        <h3 style={{ marginTop: 0, marginBottom: 8 }}>Rohdaten</h3>
        <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(data, null, 2)}</pre>
      </section>
    </div>
  );
}

function Row({ k, v }) {
  return (
    <div style={{ display: "flex", gap: 8, fontSize: 14 }}>
      <div style={{ width: 140, color: "#6b7280" }}>{k}</div>
      <div style={{ flex: 1, fontWeight: 600 }}>{v ?? "—"}</div>
    </div>
  );
}
function card() {
  return { border: "1px solid #e5e7eb", borderRadius: 16, padding: 16, background: "white", boxShadow: "0 1px 2px rgba(0,0,0,0.04)" };
}
function fmt(n) {
  if (n == null) return "—";
  try { return Number(n).toLocaleString("de-DE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }); }
  catch { return String(n); }
}
