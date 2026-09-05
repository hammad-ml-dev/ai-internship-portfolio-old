const CITIES = [
  "Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad",
  "Multan", "Peshawar", "Quetta", "Gujranwala", "Sialkot"
];

const CUISINES = [
  "Pakistani", "BBQ", "Chinese", "Fast Food", "Italian", "Thai",
  "Indian", "Turkish", "Lebanese", "Desserts", "Beverages"
];

const NAMES = [
  "BBQ Tonight", "Chinese Wok", "Pizza Express", "Nando's", "Hardee's",
  "Karachi Darbar", "Student Biryani", "Salt'n Pepper", "Café Flo", "Bundu Khan",
  "Ginsoy", "Howdy", "Optp", "Xander's", "Chop Chop"
];

const AREAS = {
  Karachi: ["Clifton", "Saddar", "Gulshan-e-Iqbal", "North Nazimabad", "DHA"],
  Lahore: ["Gulberg", "Johar Town", "Model Town", "DHA", "Mall Road"],
  Islamabad: ["F-7", "F-10", "G-11", "Blue Area", "Bahria Town"],
  default: ["Main Boulevard", "City Center", "Commercial Area", "Ring Road", "Station Road"]
};

let lastRows = [];

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function phoneFor(city) {
  const prefix = city === "Karachi" || city === "Lahore" ? "030" : "03" + Math.floor(Math.random() * 10);
  return `+92 ${prefix}${Math.floor(Math.random() * 10)} ${String(Math.floor(Math.random() * 900 + 100))} ${String(Math.floor(Math.random() * 90 + 10))} ${String(Math.floor(Math.random() * 90 + 10))}`;
}

function scoreLead(r) {
  let s = 40;
  if (r.phone) s += 15;
  if (r.website) s += 15;
  if (r.rating >= 4.2) s += 20;
  if (r.reviews_count > 200) s += 10;
  return Math.min(99, s);
}

function generate(city, count) {
  const areas = AREAS[city] || AREAS.default;
  const rows = [];
  for (let i = 0; i < count; i++) {
    const base = pick(NAMES);
    const name = i === 0 ? `${base} ${city}` : `${base} ${city} Branch ${i + 1}`;
    const rating = +(3 + Math.random() * 2).toFixed(1);
    const reviews = Math.floor(20 + Math.random() * 900);
    const hasWeb = Math.random() > 0.35;
    const row = {
      name,
      city,
      cuisine_type: pick(CUISINES),
      phone: phoneFor(city),
      address: `${Math.floor(Math.random() * 90 + 1)} ${pick(areas)}, ${city}`,
      website: hasWeb ? `https://www.${base.toLowerCase().replace(/[^a-z0-9]+/g, "")}${city.toLowerCase()}.com` : "",
      rating,
      reviews_count: reviews,
      source: pick(["Google Maps", "Yellow Pages PK", "FoodPanda", "Demo"]),
      lead_score: 0
    };
    row.lead_score = scoreLead(row);
    rows.push(row);
  }
  return rows.sort((a, b) => b.lead_score - a.lead_score);
}

function renderStats(rows) {
  const avg = rows.reduce((s, r) => s + r.rating, 0) / rows.length;
  const withWeb = rows.filter((r) => r.website).length;
  const high = rows.filter((r) => r.lead_score >= 80).length;
  document.getElementById("stats").innerHTML = `
    <div class="stat"><b>${rows.length}</b><span>Total leads</span></div>
    <div class="stat"><b>${avg.toFixed(1)}</b><span>Avg rating</span></div>
    <div class="stat"><b>${withWeb}</b><span>With website</span></div>
    <div class="stat"><b>${high}</b><span>High potential</span></div>
  `;
}

function renderTable(rows) {
  const wrap = document.getElementById("tableWrap");
  wrap.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Restaurant</th><th>Cuisine</th><th>Phone</th><th>Rating</th><th>Score</th><th>Source</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map((r) => `
          <tr>
            <td><strong>${r.name}</strong><div style="color:#97a8be;font-size:12px">${r.address}</div></td>
            <td><span class="badge">${r.cuisine_type}</span></td>
            <td>${r.phone}</td>
            <td>${r.rating} (${r.reviews_count})</td>
            <td><strong>${r.lead_score}</strong></td>
            <td>${r.source}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function toCsv(rows) {
  const cols = ["name", "city", "cuisine_type", "phone", "address", "website", "rating", "reviews_count", "source", "lead_score"];
  const lines = [cols.join(",")].concat(rows.map((r) => cols.map((c) => `"${String(r[c]).replace(/"/g, '""')}"`).join(",")));
  return lines.join("\n");
}

function init() {
  const citySel = document.getElementById("city");
  CITIES.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = c;
    opt.textContent = c;
    citySel.appendChild(opt);
  });

  document.getElementById("run").addEventListener("click", () => {
    const city = citySel.value;
    const count = +document.getElementById("count").value;
    lastRows = generate(city, count);
    renderStats(lastRows);
    renderTable(lastRows);
    document.getElementById("csv").disabled = false;
  });

  document.getElementById("csv").addEventListener("click", () => {
    const blob = new Blob([toCsv(lastRows)], { type: "text/csv;charset=utf-8;" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `restaurant_leads_${citySel.value.toLowerCase()}.csv`;
    a.click();
  });
}

init();
