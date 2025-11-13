const BASE = "http://127.0.0.1:8000/api";

async function jfetch(url, opts) {
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

export async function uploadCSV(file, { mode, month } = {}) {
  const fd = new FormData();
  fd.append("file", file);
  const p = new URLSearchParams();
  if (mode) p.set("mode", mode);
  if (month) p.set("month", month);
  return jfetch(`${BASE}/transactions/upload?${p}`, { method: "POST", body: fd });
}

export const getInsights = () => jfetch(`${BASE}/insights`);
export const getNudges = () => jfetch(`${BASE}/nudges`);
export const suggestNudges = () => jfetch(`${BASE}/nudges/suggest`, { method: "POST" });
