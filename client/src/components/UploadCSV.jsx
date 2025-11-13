import React, { useRef, useState } from "react";
import { uploadCSV } from "../api";

export default function UploadCSV({ onUploaded }) {
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  const [replace, setReplace] = useState(true);
  const [month, setMonth] = useState("2025-10");
  const inputRef = useRef(null);

  async function doUpload(file) {
    if (!file) return;
    setBusy(true); setMsg("");
    try {
      const res = await uploadCSV(file, { mode: replace ? "replace" : undefined, month });
      setMsg(`Imported ${res.created} rows${res.month ? ` for ${res.month}` : ""}`);
      onUploaded?.();
    } catch (e) {
      setMsg(e?.message || "Upload failed");
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  function onChange(e) { doUpload(e.target.files?.[0]); }

  function onDrop(e) {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    doUpload(file);
  }

  return (
    <div className="card">
      <div className="upload-header">
        <h2>Upload Transactions</h2>
        <div className="upload-controls">
          <label className="checkbox">
            <input type="checkbox" checked={replace} onChange={e=>setReplace(e.target.checked)} />
            Replace month
          </label>
          <input type="month" value={month} onChange={e=>setMonth(e.target.value)} disabled={!replace} />
        </div>
      </div>

      <div
        className="dropzone"
        onDragOver={e=>e.preventDefault()}
        onDrop={onDrop}
        role="button"
        tabIndex={0}
        onKeyDown={(e)=>{ if(e.key==="Enter" && inputRef.current) inputRef.current.click(); }}
        onClick={()=>inputRef.current?.click()}
      >
        <div className="dropzone-inner">
          <div className="upload-icon">⬆️</div>
          <div className="upload-text">
            <div className="upload-title">Drag & Drop CSV here</div>
            <div className="upload-sub">or</div>
          </div>
          <button className="btn-primary" type="button" onClick={()=>inputRef.current?.click()}>
            Choose CSV File
          </button>
          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            onChange={onChange}
            style={{ display: "none" }}
          />
        </div>
      </div>

      {busy && <p className="muted">Uploading…</p>}
      {msg && <p className="success">{msg}</p>}
    </div>
  );
}
