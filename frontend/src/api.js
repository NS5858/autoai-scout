const API_URL = "https://autoai-scout.onrender.com";

export async function analyzeText(text) {
  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error("Serverfehler oder keine Verbindung");
  }

  return await response.json();
}
