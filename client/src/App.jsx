import React, { useEffect, useState } from "react";
import { getInsights, getNudges } from "./api";
import UploadCSV from "./components/UploadCSV.jsx";
import InsightCards from "./components/InsightCards.jsx";
import NudgeList from "./components/NudgeList.jsx";
import BudgetBars from "./components/BudgetBars.jsx";

export default function App() {
  const [insights, setInsights] = useState(null);
  const [nudges, setNudges] = useState([]);
  const [err, setErr] = useState("");

  const [budgets] = useState({
    groceries: 36000,  // $360
    delivery:  24000,  // $240
    coffee:     4000,  // $40
    household: 12000,  // $120
  });

  async function refresh() {
    try {
      setErr("");
      const [i, n] = await Promise.all([getInsights(), getNudges()]);
      setInsights(i); setNudges(n);
    } catch (e) {
      setErr(String(e?.message || e));
    }
  }

  useEffect(() => { refresh(); }, []);

  return (
    <>
      <header className="topbar">
        <div className="container">
          <h1>Spend Insights + Nudges</h1>
        </div>
      </header>

      <main className="container">
        {err && <div className="alert">{err}</div>}

        {/*  Upload is FRONT AND CENTER */}
        <UploadCSV onUploaded={refresh} />
        <div className="spacer" />

        {insights && (
          <>
            <InsightCards data={insights} />
            <div className="spacer" />
            <BudgetBars byCategory={insights.by_category} budgetsCents={budgets} />
            <div className="spacer" />
          </>
        )}

        <NudgeList nudges={nudges} refresh={refresh} />
      </main>
    </>
  );
}
