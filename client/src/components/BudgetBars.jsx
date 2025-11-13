import React from "react";

function money(x){ return `$${(x/100).toFixed(0)}`; }

function Bar({label, used, cap}) {
  const pct = Math.min(100, Math.round((used/cap)*100 || 0));
  return (
    <div style={{marginBottom:12}}>
      <div style={{display:"flex", justifyContent:"space-between", fontSize:14}}>
        <span>{label}</span>
        <span>{money(used)} / {money(cap)} ({pct}%)</span>
      </div>
      <div style={{height:10, background:"#eee", borderRadius:6}}>
        <div style={{height:"100%", width:`${pct}%`, borderRadius:6, background:"#3b82f6"}} />
      </div>
    </div>
  );
}

export default function BudgetBars({ byCategory, budgetsCents }) {
  const used = (name) => byCategory?.[name] || 0;
  return (
    <div className="card">
      <h3 style={{marginTop:0}}>Budgets (Variable Spend)</h3>
      <Bar label="Groceries"  used={used("Groceries")}  cap={budgetsCents.groceries}/>
      <Bar label="Delivery"   used={used("Food Delivery")} cap={budgetsCents.delivery}/>
      <Bar label="Coffee"     used={used("Coffee")}      cap={budgetsCents.coffee}/>
      <Bar label="Household"  used={used("Household")}   cap={budgetsCents.household}/>
    </div>
  );
}
