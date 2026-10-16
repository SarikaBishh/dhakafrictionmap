// Weighted scoring engine. Mirrors analysis/calculate_scores.py (cross-checked by frontend/tests).
const TOL = 1e-9;
const round9 = (x) => Math.round(x * 1e9) / 1e9;

export function validateWeights(w) {
  const v = Object.values(w);
  if (v.some((x) => typeof x !== 'number' || Number.isNaN(x))) return { ok: false, error: 'Weights must be numbers.' };
  if (v.some((x) => x < 0)) return { ok: false, error: 'Weights must be non-negative.' };
  const t = v.reduce((a, b) => a + b, 0);
  if (Math.abs(t - 1) > TOL) return { ok: false, error: `Weights must sum to 1 (got ${t}).` };
  return { ok: true, error: '' };
}

export function normalizeWeights(raw) {
  const t = Object.values(raw).reduce((a, b) => a + b, 0);
  if (!(t > 0)) throw new Error('At least one weight must be above zero.');
  return Object.fromEntries(Object.entries(raw).map(([k, x]) => [k, x / t]));
}

// Min-max to [0,1]; direction -1 flips; identical values -> 0.5; null stays null.
export function normalizeIndicator(values, direction = 1) {
  const xs = values.filter((x) => x != null && !Number.isNaN(x));
  const mn = Math.min(...xs), mx = Math.max(...xs);
  return values.map((x) => {
    if (x == null || Number.isNaN(x)) return null;
    const n = mx === mn ? 0.5 : (x - mn) / (mx - mn);
    return direction > 0 ? n : 1 - n;
  });
}

// sites: [{id, values:{key:number|null}}]; inds: [{key, direction}]; w: fractions summing to 1.
// Missing indicators are dropped per site and remaining weights renormalised; site flagged incomplete.
export function priorityScores(sites, inds, w) {
  const v = validateWeights(w);
  if (!v.ok) throw new Error(v.error);
  const N = {};
  inds.forEach((i) => { N[i.key] = normalizeIndicator(sites.map((s) => s.values[i.key]), i.direction); });
  const out = sites.map((s, idx) => {
    const used = inds.filter((i) => w[i.key] > 0 && N[i.key][idx] != null);
    const missing = inds.filter((i) => w[i.key] > 0 && N[i.key][idx] == null).map((i) => i.key);
    const tw = used.reduce((a, i) => a + w[i.key], 0);
    const contrib = {};
    inds.forEach((i) => { contrib[i.key] = used.includes(i) && tw > 0 ? (100 * w[i.key] * N[i.key][idx]) / tw : 0; });
    const score = tw > 0 ? round9(Object.values(contrib).reduce((a, b) => a + b, 0)) : null;
    return { id: s.id, score, complete: missing.length === 0, missing, contrib, rank: null };
  });
  out.forEach((o) => {
    if (o.score != null) o.rank = 1 + out.filter((x) => x.score != null && x.score > o.score).length;
  });
  return out;
}

export function sensitivity(sites, inds, scenarios, cutoff = 2) {
  const ranks = {};
  Object.entries(scenarios).forEach(([name, w]) => {
    priorityScores(sites, inds, w).forEach((o) => { (ranks[o.id] = ranks[o.id] || {})[name] = o.rank; });
  });
  return sites.map((s) => {
    const r = Object.values(ranks[s.id]).filter((x) => x != null);
    const range = r.length ? Math.max(...r) - Math.min(...r) : 0;
    return { id: s.id, ranks: ranks[s.id], range, sensitive: range >= cutoff };
  });
}
