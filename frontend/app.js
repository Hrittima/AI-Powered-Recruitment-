const API = "https://ai-powered-recruitment-production.up.railway.app";

async function uploadResume(file) {
  const formData = new FormData();
  formData.append("resume", file);

  document.getElementById("loading").style.display = "block";

  try {
    const res = await fetch(API + "/api/analyze", {
      method: "POST",
      body: formData
    });

    const data = await res.json();

    document.getElementById("result").innerHTML = `
      <h2>Score: ${data.score}%</h2>
      <p>${data.rank}</p>
    `;

  } catch {
    alert("Error uploading");
  }

  document.getElementById("loading").style.display = "none";
}