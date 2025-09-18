
const $ = s => document.querySelector(s);
const urlEl = $("#url");
const msgEl = $("#msg");
const prevBox = $("#previewBox");
const thumb = $("#thumb");
const title = $("#title");
const meta = $("#meta");
const quality = $("#quality");

function showMsg(text, type="err"){
  msgEl.className = `msg ${type}`;
  msgEl.textContent = text;
  msgEl.classList.remove("hide");
}
function clearMsg(){ msgEl.classList.add("hide"); }

async function call(endpoint, payload){
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  });
  const data = await res.json().catch(()=>({}));
  if(!res.ok) throw new Error(data.error || "Erreur");
  return data;
}

$("#preview").addEventListener("click", async () => {
  clearMsg();
  prevBox.classList.add("hide");
  try {
    const audio = document.querySelector('input[name="type"]:checked').value === "audio";
    const data = await call("/api/preview", { url: urlEl.value.trim(), audio });
    if(data.thumbnail) thumb.src = data.thumbnail;
    title.textContent = data.title || "(Sans titre)";
    meta.textContent = [data.uploader, data.duration ? `${data.duration}s`:""].filter(Boolean).join(" • ");
    prevBox.classList.remove("hide");
  } catch(e){
    showMsg(e.message || String(e), "err");
  }
});

$("#download").addEventListener("click", async () => {
  clearMsg();
  try {
    const audio = document.querySelector('input[name="type"]:checked').value === "audio";
    const data = await call("/api/download", {
      url: urlEl.value.trim(),
      audio,
      quality: quality.value
    });
    prevBox.classList.remove("hide");
    title.textContent = "Téléchargement prêt";
    meta.textContent = data.filename || "";
    // Démarre le téléchargement
    const a = document.createElement("a");
    a.href = data.url;
    a.download = data.filename || "";
    document.body.appendChild(a);
    a.click();
    a.remove();
    showMsg("Téléchargement démarré ✅", "ok");
  } catch(e){
    showMsg(e.message || String(e), "err");
  }
});

// Coller lien + Enter -> démarrer directement
urlEl.addEventListener("keydown", (e)=>{
  if(e.key === "Enter"){ $("#download").click(); }
});
