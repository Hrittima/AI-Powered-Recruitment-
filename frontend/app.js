document.addEventListener("DOMContentLoaded", () => {

  const API = "https://ai-powered-recruitment-production.up.railway.app";

  let selectedFile = null;

  const dropZone   = document.getElementById("dropZone");
  const fileInput  = document.getElementById("resumeInput");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const resultDiv  = document.getElementById("result");
  const loading    = document.getElementById("loading");

  if (!dropZone || !fileInput || !analyzeBtn) {
    console.error("Required DOM elements not found");
    return;
  }

  // ── File selection ──────────────────────────────────────────────────────
  dropZone.onclick = () => fileInput.click();

  fileInput.onchange = () => {
    if (fileInput.files[0]) setFile(fileInput.files[0]);
  };

  dropZone.ondragover = (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  };
  dropZone.ondragleave = () => dropZone.classList.remove("dragover");
  dropZone.ondrop = (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
  };

  function setFile(file) {
    const allowed = [".pdf", ".doc", ".docx"];
    const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    if (!allowed.includes(ext)) {
      showError("Only PDF, DOC, DOCX files are supported.");
      return;
    }
    selectedFile = file;
    dropZone.innerHTML = `<p>✅ ${file.name}</p>`;
    resultDiv.innerHTML = "";
  }

  // ── Analyze ─────────────────────────────────────────────────────────────
  analyzeBtn.onclick = async () => {
    if (!selectedFile) {
      alert("Please upload a resume first!");
      return;
    }

    loading.style.display = "block";
    resultDiv.innerHTML   = "";
    analyzeBtn.disabled   = true;

    const formData = new FormData();
    formData.append("resume", selectedFile);

    try {
      const res = await fetch(`${API}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      let data;
      try {
        data = await res.json();
      } catch {
        throw new Error(`Server returned status ${res.status} with no JSON body.`);
      }

      if (!res.ok || data.error) {
        showError(data.error || `Server error ${res.status}`);
        return;
      }

      renderResult(data);

    } catch (err) {
      console.error(err);
      showError(err.message || "Could not connect to server.");
    } finally {
      loading.style.display = "none";
      analyzeBtn.disabled   = false;
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────
  function renderResult(data) {
    const score    = data.score ?? 0;
    const rank     = data.rank  ?? "--";
    const keywords = data.keywords     ?? [];
    const missing  = data.missing      ?? [];
    const recs     = data.recommendations ?? [];

    const scoreColor = score >= 70 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444";

    resultDiv.innerHTML = `
      <div style="margin-top:20px;">

        <!-- Score circle -->
        <div style="
          width:110px; height:110px; border-radius:50%;
          border: 4px solid ${scoreColor};
          display:flex; flex-direction:column;
          align-items:center; justify-content:center;
          margin: 0 auto 12px;
        ">
          <span style="font-size:28px; font-weight:700; color:${scoreColor}">${score}</span>
          <span style="font-size:11px; color:#9ca3af;">/ 100</span>
        </div>

        <!-- Rank -->
        <div style="font-size:20px; font-weight:600; margin-bottom:6px;">${rank}</div>

        <!-- Progress bar -->
        <div class="progress-bar">
          <div class="progress-fill" style="width:${score}%; background: linear-gradient(90deg, #6366f1, ${scoreColor});"></div>
        </div>

        <!-- Keywords matched -->
        ${keywords.length ? `
          <div style="margin-top:18px; text-align:left;">
            <p style="font-weight:600; margin-bottom:8px;">✅ Matched Keywords</p>
            <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${keywords.map(k => `
                <span style="
                  background:rgba(34,197,94,0.15); border:1px solid #22c55e;
                  color:#22c55e; border-radius:20px;
                  padding:3px 12px; font-size:13px;
                ">${k}</span>
              `).join("")}
            </div>
          </div>
        ` : ""}

        <!-- Missing keywords -->
        ${missing.length ? `
          <div style="margin-top:14px; text-align:left;">
            <p style="font-weight:600; margin-bottom:8px;">❌ Missing Keywords</p>
            <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${missing.map(k => `
                <span style="
                  background:rgba(239,68,68,0.12); border:1px solid #ef4444;
                  color:#ef4444; border-radius:20px;
                  padding:3px 12px; font-size:13px;
                ">${k}</span>
              `).join("")}
            </div>
          </div>
        ` : ""}

        <!-- Recommendations -->
        ${recs.length ? `
          <div style="margin-top:14px; text-align:left;">
            <p style="font-weight:600; margin-bottom:8px;">💡 Recommendations</p>
            <ul style="padding-left:18px; color:#d1d5db; font-size:14px; line-height:1.8;">
              ${recs.map(r => `<li>${r}</li>`).join("")}
            </ul>
          </div>
        ` : ""}

      </div>
    `;
  }

  function showError(msg) {
    resultDiv.innerHTML = `
      <div style="
        margin-top:16px; padding:12px 16px;
        background:rgba(239,68,68,0.12); border:1px solid #ef4444;
        border-radius:10px; color:#ef4444; font-size:14px;
      ">❌ ${msg}</div>
    `;
  }

});