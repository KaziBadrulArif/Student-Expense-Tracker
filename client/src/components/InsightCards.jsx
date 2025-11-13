import React from "react";


function money(cents) {
return `$${((cents || 0) / 100).toFixed(2)}`;
}


export default function InsightCards({ data }) {
if (!data) return null;
const cats = Object.entries(data.by_category || {}).sort((a,b)=>b[1]-a[1]);


return (
<div className="grid">
<div className="card">
<div style={{ fontSize:12, color:"#6b7280" }}>Total</div>
<div style={{ fontSize:24 }}>{money(data.total_cents)}</div>
</div>
<div className="card">
<div style={{ fontSize:12, color:"#6b7280" }}>Daily Avg</div>
<div style={{ fontSize:24 }}>{money(data.daily_avg_cents)}</div>
</div>
<div className="card">
<div style={{ fontSize:12, color:"#6b7280" }}>Month Forecast</div>
<div style={{ fontSize:24 }}>{money(data.month_forecast_cents)}</div>
</div>
<div className="card">
<div style={{ fontSize:12, color:"#6b7280" }}>Top Merchants</div>
<ul style={{ margin:0, paddingLeft:16 }}>
{(data.top_merchants || []).map(([m, c]) => (
<li key={m}>{m} — {money(c)}</li>
))}
</ul>
</div>
<div className="card">
<div style={{ fontSize:12, color:"#6b7280" }}>Categories</div>
<ul style={{ margin:0, paddingLeft:16 }}>
{cats.map(([k,v]) => (<li key={k}>{k} — {money(v)}</li>))}
</ul>
</div>
</div>
);
}