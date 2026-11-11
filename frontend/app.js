const $ = (id) => document.getElementById(id);
const api = async (path, opts={}) => {
  const r = await fetch(path, opts);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
};

// Tabs
document.querySelectorAll("#tabs button").forEach(b => {
  b.onclick = () => {
    document.querySelectorAll("#tabs button").forEach(x=>x.classList.remove("active"));
    document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));
    b.classList.add("active");
    document.getElementById("tab-"+b.dataset.tab).classList.add("active");
    loadTab(b.dataset.tab);
  };
});

async function loadTab(t) {
  if (t === "memory") loadMemory();
  if (t === "vault") loadVault();
  if (t === "network") loadNetwork();
  if (t === "tools") loadTools();
  if (t === "docs") loadDocs();
  if (t === "levels") loadLevels();
  if (t === "settings") loadSettings();
}

// Status
async function refreshStatus() {
  try {
    const s = await api("/api/status");
    $("statusLine").textContent = `${s.app} v${s.version} · ${s.current_level} · model: ${s.model}`;
    if (s.last_used) {
      $("inUseBadge").textContent = `in use: ${s.last_used.model} · ${s.last_used.endpoint}`;
    }
  } catch (e) { $("statusLine").textContent = "offline"; }
}
refreshStatus();

// Chat
let chatHistory = [];
$("sendBtn").onclick = async () => {
  const msg = $("msgInput").value.trim();
  if (!msg) return;
  $("msgInput").value = "";
  appendMsg("user", msg);
  const provider = $("providerSel").value;
  const model = $("modelInput").value.trim() || null;
  const useMemory = $("useMemory").checked;
  const useTools = $("useTools").checked;
  try {
    const r = await fetch("/api/chat", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({message:msg, provider, model, use_memory:useMemory, use_tools:useTools})
    });
    const reader = r.body.getReader();
    const dec = new TextDecoder();
    let buf = "";
    let assistantDiv = appendMsg("assistant", "");
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      buf += dec.decode(value, {stream:true});
      const lines = buf.split("\n");
      buf = lines.pop();
      for (const line of lines) {
        if (!line.startsWith("data:")) continue;
        try {
          const j = JSON.parse(line.slice(5));
          if (j.token) assistantDiv.textContent += j.token;
          if (j.done) { /* ok */ }
          if (j.error) assistantDiv.textContent = "Error: " + j.error;
        } catch {}
      }
    }
  } catch (e) { appendMsg("assistant", "Error: " + e.message); }
  refreshStatus();
};

function appendMsg(role, text) {
  const d = document.createElement("div");
  d.className = "msg " + role;
  d.innerHTML = `<div class="role">${role}</div><div class="content">${escapeHtml(text)}</div>`;
  $("chatLog").appendChild(d);
  $("chatLog").scrollTop = $("chatLog").scrollHeight;
  return d.querySelector(".content");
}
function escapeHtml(s){ return s.replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c])); }

// Memory
async function loadMemory() {
  const d = await api("/api/memory");
  $("memList").innerHTML = d.items.map(m => `
    <div class="card">
      <div class="meta">#${m.id} · ${m.kind} · ${m.pinned?"📌 ":""}${new Date(m.updated_at*1000).toLocaleString()}</div>
      <div contenteditable="true" data-id="${m.id}" class="memtext">${escapeHtml(m.content)}</div>
      <div class="row">
        <button onclick="saveMem(${m.id}, this)">Save</button>
        <button class="secondary" onclick="delMem(${m.id})">Delete</button>
      </div>
    </div>`).join("");
}
$("memAdd").onclick = async () => {
  await api("/api/memory", {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({content:$("memContent").value, kind:$("memKind").value, pinned:$("memPinned").checked})});
  $("memContent").value = "";
  loadMemory();
};
window.saveMem = async (id, btn) => {
  const el = document.querySelector(`[data-id="${id}"]`);
  await api(`/api/memory/${id}`, {method:"PUT", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({content: el.innerText, kind:"fact"})});
};
window.delMem = async (id) => { await api(`/api/memory/${id}`, {method:"DELETE"}); loadMemory(); };

// Vault
async function loadVault() {
  const d = await api("/api/vault");
  $("vaultList").innerHTML = "<div class='card'>Stored providers: " + (d.providers.join(", ") || "none") + "</div>";
}
$("vaultSet").onclick = async () => {
  await api("/api/vault", {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({provider:$("vaultProvider").value, api_key:$("vaultKey").value})});
  $("vaultKey").value = "";
  loadVault();
};

// Network
async function loadNetwork() {
  const d = await api("/api/network");
  $("airgapToggle").checked = d.airgap;
  $("netList").innerHTML = Object.entries(d.endpoints).map(([k,v]) =>
    `<div class="card"><label><input type="checkbox" ${v?"checked":""} onchange="setNet('${k}', this.checked)"> ${k}</label></div>`).join("");
}
$("airgapToggle").onchange = async (e) => { await api("/api/airgap?v="+e.target.checked, {method:"POST"}); loadNetwork(); };
window.setNet = async (ep, val) => { await api("/api/network", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({endpoint:ep, allowed:val})}); };

// Tools
async function loadTools() {
  const d = await api("/api/tools");
  $("toolsList").innerHTML = d.tools.map(t =>
    `<div class="card"><b>${t.name}</b> <span class="badge ${t.enabled?"unlocked":"locked"}">${t.enabled?"on":"off"}</span>
     <div class="meta">${t.description}</div>
     <button class="secondary" onclick="toggleTool('${t.name}', ${!t.enabled})">${t.enabled?"Disable":"Enable"}</button></div>`).join("");
  $("toolSel").innerHTML = d.tools.map(t=>`<option>${t.name}</option>`).join("");
}
window.toggleTool = async (name, en) => { await api(`/api/tools/toggle?name=${name}&enabled=${en}`, {method:"POST"}); loadTools(); };
$("toolRun").onclick = async () => {
  let args = {};
  try { args = JSON.parse($("toolArgs").value || "{}"); } catch {}
  const r = await api("/api/tool/run", {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({name:$("toolSel").value, args})});
  $("toolOut").textContent = JSON.stringify(r.result, null, 2);
};

// Docs / Oracle
async function loadDocs() {
  const d = await api("/api/documents");
  $("docList").innerHTML = d.documents.map(x => `<div class="card">#${x.id} ${escapeHtml(x.name)} <span class="meta">${x.chunks} chunks</span></div>`).join("");
}
$("docAdd").onclick = async () => {
  await api("/api/documents", {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({name:$("docName").value, content:$("docContent").value})});
  $("docName").value=""; $("docContent").value="";
  loadDocs();
};
$("docSearch").onclick = async () => {
  const d = await api("/api/documents/search?q="+encodeURIComponent($("docQuery").value));
  $("docResults").innerHTML = d.results.map(r=>`<div class="card">${escapeHtml(r.content)}</div>`).join("");
};

// Levels
async function loadLevels() {
  const d = await api("/api/levels");
  $("levelsList").innerHTML = d.levels.map(l => `
    <div class="card">
      <b>${l.level} — ${l.name}</b> <span class="badge ${l.unlocked?"unlocked":"locked"}">${l.unlocked?"unlocked":"locked"}</span>
      <div class="meta">${l.description}</div>
      ${!l.unlocked && l.can_unlock ? `<button onclick="unlockLvl('${l.level}')">Unlock</button>` : ""}
      ${l.unlocked ? `<button class="secondary" onclick="setLvl('${l.level}')">Set current</button>` : ""}
    </div>`).join("");
}
window.unlockLvl = async (l) => { await api("/api/levels/unlock", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({level:l})}); loadLevels(); refreshStatus(); };
window.setLvl = async (l) => { await api("/api/levels/set", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({level:l})}); refreshStatus(); };

// Settings
async function loadSettings() {
  const d = await api("/api/settings");
  const s = d.settings;
  $("setName").value = (await api("/api/identity")).identity?.name || "";
  $("setGuardian").checked = s.guardian === "1";
}
$("saveSettings").onclick = async () => {
  await api("/api/settings", {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({guardian: $("setGuardian").checked ? "1" : "0"})});
  if ($("setName").value.trim()) {
    await api("/api/identity", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({name:$("setName").value.trim()})});
  }
  $("settingsOut").textContent = "saved";
};
$("backupBtn").onclick = async () => {
  const r = await api("/api/backup", {method:"POST"});
  $("settingsOut").textContent = "backup: " + r.file;
};
