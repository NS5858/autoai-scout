const BACKEND_URL = "https://autoai-scout.onrender.com";

export async function analyzeUrl(url) {
  const response = await fetch(`${BACKEND_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    throw new Error("Backend nicht erreichbar");
  }

  return await response.json();
}
