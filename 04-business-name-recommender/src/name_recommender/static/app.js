let lastResults = [];

async function generateNames() {
	const keywords = document.getElementById('keywords').value
		.split(',')
		.map(k => k.trim())
		.filter(Boolean);
	const count = parseInt(document.getElementById('count').value || '120', 10);
	const top = parseInt(document.getElementById('top').value || '15', 10);
	const minLen = parseInt(document.getElementById('minLen').value || '5', 10);
	const maxLen = parseInt(document.getElementById('maxLen').value || '12', 10);
	const checkDomains = document.getElementById('checkDomains').checked;
	const datasetCsv = document.getElementById('datasetCsv').value.trim() || null;
	const useLlm = document.getElementById('useLlm').checked;
	const tldChecks = Array.from(document.querySelectorAll('.tlds input[type="checkbox"]:checked')).map(i => i.value);

	const payload = { keywords, count, top, min_len: minLen, max_len: maxLen, check_domains: checkDomains, tlds: tldChecks, dataset_csv: datasetCsv, use_llm: useLlm };
	const loading = document.getElementById('loading');
	const resultsEl = document.getElementById('results');

	loading.classList.remove('hidden');
	resultsEl.innerHTML = '';

	try {
		const res = await fetch('/api/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
		if (!res.ok) throw new Error('Failed to generate');
		const data = await res.json();
		lastResults = Array.isArray(data.results) ? data.results : [];
		renderResults(lastResults);
	} catch (e) {
		resultsEl.innerHTML = `<div class="result">Error: ${e.message}</div>`;
	} finally {
		loading.classList.add('hidden');
	}
}

function renderResults(items) {
	const resultsEl = document.getElementById('results');
	resultsEl.innerHTML = '';
	for (const r of items) {
		const card = document.createElement('div');
		card.className = 'result';
		card.innerHTML = `
			<div class="name">${r.name}</div>
			<div class="score">Score: ${(r.score ?? 0).toFixed(3)}</div>
			${r.availability_score != null ? `<div class="avail">Availability: ${(r.availability_score*100).toFixed(0)}%</div>` : ''}
		`;
		if (r.domains) {
			const tags = document.createElement('div');
			tags.className = 'domain-tags';
			Object.entries(r.domains).forEach(([tld, label]) => {
				const t = document.createElement('span');
				t.className = 'tag';
				t.innerText = `${tld}: ${label}`;
				tags.appendChild(t);
			});
			card.appendChild(tags);
		}
		resultsEl.appendChild(card);
	}
}

document.addEventListener('DOMContentLoaded', () => {
	const btn = document.getElementById('generate');
	btn.addEventListener('click', generateNames);

	// Upload CSV handler
	const uploadBtn = document.getElementById('uploadBtn');
	uploadBtn.addEventListener('click', async () => {
		const fileInput = document.getElementById('datasetFile');
		if (!fileInput.files || !fileInput.files[0]) return;
		const form = new FormData();
		form.append('file', fileInput.files[0]);
		const res = await fetch('/api/upload-dataset', { method: 'POST', body: form });
		const data = await res.json();
		document.getElementById('datasetCsv').value = data.dataset_csv || '';
	});

	// Download CSV of last results (includes availability percent and per-TLD columns if present)
	const dl = document.getElementById('downloadCsv');
	dl.addEventListener('click', () => {
		if (!Array.isArray(lastResults) || lastResults.length === 0) return;

		const allTlds = Array.from(new Set(lastResults.flatMap(r => Object.keys(r.domains || {})))).sort();
		const header = ['rank','name','score'];
		const includeAvailPct = lastResults.some(r => typeof r.availability_score === 'number');
		if (includeAvailPct) header.push('availability_percent');
		header.push(...allTlds);

		const lines = [];
		lines.push(header.join(','));

		const esc = v => '"' + String(v).replaceAll('"','""') + '"';

		lastResults.forEach((r, i) => {
			const row = [i+1, r.name ?? '', (r.score ?? 0).toFixed(3)];
			if (includeAvailPct) row.push(r.availability_score != null ? Math.round(r.availability_score*100) + '%' : '');
			for (const t of allTlds) row.push((r.domains && r.domains[t]) ? r.domains[t] : '');
			lines.push(row.map(esc).join(','));
		});

		const csv = lines.join('\n');
		const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url; a.download = 'names.csv'; a.click();
		URL.revokeObjectURL(url);
	});
});


