const SEEDS = [
  "growth", "trust", "advisory", "guardian", "launch", "setup", "ledger",
  "compliance", "formation", "capital", "foundry", "prime", "mentor",
  "clarity", "fortress", "secure", "shield", "bridge", "pivot", "venture",
  "scale", "pilot", "nexus", "atlas", "beacon", "harbor", "summit", "ridge"
];

const PREFIXES = ["Neo", "Apex", "True", "Bright", "Core", "Nova", "Prime", "Clear", "Bold", "Swift"];
const SUFFIXES = ["ly", "ora", "ify", "hub", "lab", "works", "base", "path", "craft", "wise"];
const MID = ["Grow", "Trust", "Lead", "Form", "Scale", "Guide", "Forge", "Lift"];

function clean(s) {
  return s.toLowerCase().replace(/[^a-z0-9]/g, "");
}

function scoreName(name, keywords) {
  let score = 0.45;
  const n = name.toLowerCase();
  const len = n.length;
  if (len >= 5 && len <= 10) score += 0.2;
  else if (len >= 4 && len <= 12) score += 0.1;
  if (/^[a-z]+$/.test(n)) score += 0.08;
  for (const k of keywords) {
    if (k && n.includes(clean(k))) score += 0.07;
  }
  if (/(corp|company|solutions|services)$/i.test(name)) score -= 0.15;
  if (/(ly|ora|ify|hub)$/i.test(name)) score += 0.05;
  return Math.max(0.1, Math.min(0.99, score + (Math.random() * 0.08 - 0.02)));
}

function titleCase(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function generateCandidates(keywords, count, minLen, maxLen) {
  const keys = keywords.length ? keywords : SEEDS.slice(0, 5);
  const pool = [...new Set([...keys.map(clean).filter(Boolean), ...SEEDS])];
  const out = new Set();

  while (out.size < count) {
    const mode = Math.random();
    let name = "";
    if (mode < 0.25) {
      name = titleCase(pick(PREFIXES)) + titleCase(pick(pool));
    } else if (mode < 0.5) {
      name = titleCase(pick(pool)) + titleCase(pick(SUFFIXES));
    } else if (mode < 0.75) {
      name = titleCase(pick(MID)) + titleCase(pick(pool));
    } else {
      const a = pick(pool);
      const b = pick(pool);
      name = titleCase(a.slice(0, Math.ceil(a.length / 2)) + b.slice(Math.floor(b.length / 2)));
    }
    const compact = clean(name);
    if (compact.length >= minLen && compact.length <= maxLen) out.add(name);
  }
  return [...out];
}

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function run() {
  const keywords = document.getElementById("keywords").value.split(",").map((s) => s.trim()).filter(Boolean);
  const count = +document.getElementById("count").value || 80;
  const top = +document.getElementById("top").value || 12;
  const minLen = +document.getElementById("minLen").value || 5;
  const maxLen = +document.getElementById("maxLen").value || 12;

  const candidates = generateCandidates(keywords, count, minLen, maxLen)
    .map((name) => ({ name, score: scoreName(name, keywords) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, top);

  const el = document.getElementById("results");
  el.innerHTML = candidates.map((r, i) => `
    <div class="result">
      <div>
        <div class="name">${i + 1}. ${r.name}</div>
        <div class="meta">Brandable · SME consultancy style</div>
      </div>
      <div class="score">${(r.score * 100).toFixed(0)}%</div>
    </div>
  `).join("");
}

document.getElementById("generate").addEventListener("click", run);
run();
