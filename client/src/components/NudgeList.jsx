import React from "react";
import { suggestNudges } from "../api";


export default function NudgeList({ nudges, refresh }) {
return (
<div className="card">
<div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
<h3 style={{ margin:0 }}>Nudges</h3>
<button onClick={async ()=>{ await suggestNudges(); await refresh(); }}>
Re-run suggestions
</button>
</div>
<ul>
{(nudges||[]).map(n => (
<li key={n.id} style={{ marginBottom:8 }}>
<strong>{n.type}</strong>: {n.message}
</li>
))}
</ul>
</div>
);
}