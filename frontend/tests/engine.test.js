import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateWeights, normalizeWeights, normalizeIndicator, priorityScores, sensitivity } from '../js/decision-engine.js';

const data = JSON.parse(readFileSync(new URL('../../data/processed/dataset.json', import.meta.url)));
const inds = data.indicators.map((i) => ({ key: i.key, direction: i.direction }));
const sites = data.sites.map((s) => ({ id: s.id, values: s.values }));
const defW = Object.fromEntries(data.indicators.map((i) => [i.key, i.default_weight]));

test('negative and non-summing weights rejected', () => {
  assert.equal(validateWeights({ a: -0.1, b: 1.1 }).ok, false);
  assert.equal(validateWeights({ a: 0.5, b: 0.4 }).ok, false);
  assert.equal(validateWeights({ a: 0.5, b: 0.5 }).ok, true);
});
test('all-zero raw weights throw', () => assert.throws(() => normalizeWeights({ a: 0, b: 0 })));
test('normalisation, flip and identical values', () => {
  assert.deepEqual(normalizeIndicator([0, 5, 10], 1), [0, 0.5, 1]);
  assert.deepEqual(normalizeIndicator([0, 5, 10], -1), [1, 0.5, 0]);
  assert.deepEqual(normalizeIndicator([7, 7], 1), [0.5, 0.5]);
  assert.equal(normalizeIndicator([1, null, 3], 1)[1], null);
});
test('JS scores and ranks match the Python pipeline output', () => {
  const res = priorityScores(sites, inds, defW);
  for (const s of data.sites) {
    const r = res.find((x) => x.id === s.id);
    assert.ok(Math.abs(r.score - s.default_score) < 1e-6, `${s.id} score`);
    assert.equal(r.rank, s.default_rank, `${s.id} rank`);
  }
});
test('missing indicator flags incomplete, never zero', () => {
  const c = priorityScores(sites, inds, defW).find((x) => x.id === 'C');
  assert.equal(c.complete, false);
  assert.deepEqual(c.missing, ['signal_density']);
  assert.equal(c.contrib.signal_density, 0);
});
test('contributions sum to score and score within bounds', () => {
  for (const r of priorityScores(sites, inds, defW)) {
    assert.ok(r.score >= 0 && r.score <= 100);
    assert.ok(Math.abs(Object.values(r.contrib).reduce((a, b) => a + b, 0) - r.score) < 1e-6);
  }
});
test('sensitivity matches Python ranges', () => {
  const js = sensitivity(sites, inds, data.scenarios);
  for (const p of data.sensitivity) {
    assert.equal(js.find((x) => x.id === p.location_id).range, p.rank_range);
  }
});
