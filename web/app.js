const API_BASE = "";

document.addEventListener("DOMContentLoaded", () => {
  fetchDocuments();

  document.getElementById("search-btn").addEventListener("click", runQuery);
  document.getElementById("github-btn").addEventListener("click", importGitHubRepo);
  document.getElementById("query-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter") runQuery();
  });
});

function setQuery(text) {
  const input = document.getElementById("query-input");
  input.value = text;
  if (text.includes("Scan Project Risks")) {
    scanRisks();
  } else {
    runQuery();
  }
}

async function fetchDocuments() {
  const docList = document.getElementById("doc-list");
  try {
    const res = await fetch(`${API_BASE}/api/documents`);
    const data = await res.json();
    
    if (data.documents && data.documents.length > 0) {
      docList.innerHTML = data.documents.map(doc => `
        <div class="doc-card">
          <div class="doc-name">📄 ${doc.filename}</div>
          <div class="doc-meta">${doc.chunk_count} chunks • Source: ${doc.source_type}</div>
        </div>
      `).join('');
    } else {
      docList.innerHTML = `<div class="doc-card"><div class="doc-name">No documents indexed yet.</div></div>`;
    }
  } catch (err) {
    console.error("Failed to load documents:", err);
    docList.innerHTML = `<div class="doc-card"><div class="doc-name">Backend offline. Run main.py</div></div>`;
  }
}

async function runQuery() {
  const input = document.getElementById("query-input");
  const query = input.value.trim();
  if (!query) return;

  const answerBody = document.getElementById("answer-body");
  const citationsContainer = document.getElementById("citations-container");
  const citationsList = document.getElementById("citations-list");

  answerBody.innerText = "Executing hybrid vector search & synthesizing response...";
  citationsContainer.style.display = "none";

  try {
    const res = await fetch(`${API_BASE}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, top_k: 3 })
    });
    
    const data = await res.json();
    answerBody.innerText = data.answer;

    if (data.citations && data.citations.length > 0) {
      citationsContainer.style.display = "block";
      citationsList.innerHTML = data.citations.map(c => `
        <div class="citation-chip" title="${c.section}">
          📌 ${c.filename} (${c.lines}) • Score: ${c.confidence_score}
        </div>
      `).join('');
    }
  } catch (err) {
    answerBody.innerText = "Error executing query. Ensure server is running (`python main.py`).";
    console.error(err);
  }
}

async function importGitHubRepo() {
  const input = document.getElementById("github-input");
  const status = document.getElementById("github-status");
  const repoUrl = input.value.trim();
  
  if (!repoUrl) {
    status.innerText = "Enter repo (e.g. fastapi/fastapi)";
    return;
  }

  status.innerText = "Connecting to GitHub REST API...";
  try {
    const res = await fetch(`${API_BASE}/api/ingest/github`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_url: repoUrl })
    });
    const data = await res.json();
    
    if (res.ok) {
      status.innerText = `✅ Ingested ${data.chunks_added} chunks!`;
      fetchDocuments();
    } else {
      status.innerText = `❌ Error: ${data.detail}`;
    }
  } catch (err) {
    status.innerText = "❌ Failed to connect to backend.";
  }
}

async function scanRisks() {
  const risksList = document.getElementById("risks-list");
  risksList.innerText = "Scanning indexed documents for risks & blockers...";
  try {
    const res = await fetch(`${API_BASE}/api/risks`);
    const data = await res.json();
    
    if (data.risks && data.risks.length > 0) {
      risksList.innerHTML = data.risks.map(r => `
        <div style="margin-bottom: 0.6rem; padding: 0.6rem; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px;">
          <strong style="color: #f59e0b;">⚠️ ${r.risk_type}</strong> (${r.source} ${r.lines})
          <div style="margin-top: 0.2rem; color: #cbd5e1;">"${r.summary.trim()}..."</div>
        </div>
      `).join('');
    } else {
      risksList.innerText = "No critical project risks detected in indexed documents.";
    }
  } catch (err) {
    risksList.innerText = "Failed to run risk scanner.";
  }
}
