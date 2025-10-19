import React, { useState } from "react";
import { Sparkles, Search, Car, Sun, Moon, Link as LinkIcon } from "lucide-react";

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);
  const [dark, setDark] = useState(true);

  const bg = dark ? "bg-zinc-950 text-zinc-100" : "bg-white text-zinc-900";

  async function handleAnalyze() {
    if (!url.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) throw new Error(`Serverfehler: ${res.status}`);
      const data = await res.json();
      if (!data.ok) throw new Error("Analyse fehlgeschlagen");
      setResult(data.data);
    } catch (err: any) {
      setError(err.message || "Unbekannter Fehler");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`min-h-screen transition-colors duration-300 ${bg}`}>
      <header className="sticky top-0 z-30 border-b border-zinc-700/50 backdrop-blur bg-black/40">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="grid h-9 w-9 place-items-center rounded-2xl bg-gradient-to-br from-amber-400 to-amber-600 text-black shadow-lg">
              <Car className="h-5 w-5" />
            </div>
            <div>
              <div className="text-sm font-semibold tracking-tight">AutoAI Scout</div>
              <div className="text-[11px] opacity-70">Smart Profit Tool</div>
            </div>
          </div>
          <button
            onClick={() => setDark(!dark)}
            className="rounded-full border border-zinc-600 bg-zinc-800 p-2 text-zinc-200 hover:bg-zinc-700"
          >
            {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 pb-16 pt-8">
        <div className="rounded-3xl border border-zinc-700 bg-zinc-900 p-6 shadow-sm mb-6">
          <div className="mb-3 flex items-center gap-2">
            <Search className="h-4 w-4" />
            <h2 className="text-base font-semibold">Inserat analysieren</h2>
          </div>
          <div className="flex flex-col gap-3 md:flex-row md:items-center">
            <div className="relative w-full">
              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="z. B. https://www.kleinanzeigen.de/s-anzeige/..."
                className="w-full rounded-2xl border border-zinc-600 bg-zinc-800 px-4 py-3 text-[15px] text-zinc-100 placeholder:text-zinc-400 shadow-sm outline-none focus:ring focus:ring-amber-400"
              />
              <LinkIcon className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-2xl bg-amber-500 px-5 py-3 text-sm font-semibold text-black shadow hover:bg-amber-400 active:translate-y-px disabled:opacity-60"
            >
              {loading ? (
                <>
                  <Sparkles className="h-4 w-4 animate-spin" />
                  Analysiere...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Analyse starten
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 rounded-xl bg-red-900/30 border border-red-700 p-4 text-red-300">
            Fehler: {error}
          </div>
        )}

        {result && (
          <div className="space-y-6 mt-6">
            <div className="rounded-3xl border border-zinc-700 bg-zinc-900 p-5 shadow-sm">
              <h3 className="text-base font-semibold mb-2">Analyse-Ergebnis</h3>
              <p className="text-sm text-zinc-300">
                Bewertung: {result.summary?.recommendation || "Keine Empfehlung"} <br />
                Marktwert: {result.summary?.fair_value_eur?.toLocaleString("de-DE") || "–"} €<br />
                Deal-Score: {result.summary?.deal_score ?? "–"} <br />
                Flip-Score: {result.summary?.flip_score ?? "–"}
              </p>
            </div>

            {result.text_analysis?.red_flags?.length > 0 && (
              <div className="rounded-3xl border border-amber-600/40 bg-amber-900/20 p-5">
                <h4 className="font-semibold text-amber-400 mb-1">Warnungen:</h4>
                <ul className="text-sm text-zinc-200 list-disc pl-4">
                  {result.text_analysis.red_flags.map((f: string, i: number) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="border-t border-zinc-700 py-8 text-center text-xs text-zinc-500">
        © {new Date().getFullYear()} AutoAI Scout · Live Version · by Enes.
      </footer>
    </div>
  );
}
