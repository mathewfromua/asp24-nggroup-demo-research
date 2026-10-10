import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const bytes = path => readFileSync(new URL(`../${path}`, import.meta.url));
const read = path => JSON.parse(bytes(path));
const digest = value => createHash('sha256').update(value).digest('hex');
const manuscript = read('reports/content.json');
const claims = read('reports/claim-map-editorial.json');
const registry = read('research/editorial-source-register.json');

test('report evidence map identifies the current manuscript and printed source notes', () => {
  assert.equal(claims.manuscript_sha256, digest(bytes('reports/content.json')));
  for (const [report, sections] of Object.entries(manuscript)) {
    for (const section of sections) {
      const mapped = claims.page_source_map.find(page => page.report === report && page.html_anchor === section.id);
      assert.ok(mapped, `stable section ${section.id} has an evidence map`);
      assert.equal(mapped.title, section.title);
      for (const block of section.blocks.filter(block => block[0] === 'source')) {
        const number = block[1].match(/^<b>\[(\d+)\]<\/b>/)?.[1];
        assert.ok(number, `${section.id}: source has a citation number`);
        assert.equal(claims.sources[`${report}:${number}`].printed_source_note, block[1]);
      }
    }
  }
});

test('current direct reading preserves a separate historical scope and matches the retrieval log', () => {
  const readings = new Map(registry.rc3_reverification.readings.map(reading => [reading.id, reading]));
  const linked = new Set();
  for (const [key, source] of Object.entries(claims.sources)) {
    if (!source.current_readings) continue;
    assert.ok(source.historical_evidence?.status, `${key}: historical attribution retained`);
    assert.ok(source.secondary.length, `${key}: previous report remains a distinct source`);
    assert.notEqual(source.status, source.historical_evidence.status, `${key}: stale overall status replaced`);
    for (const entry of source.current_readings) {
      const recorded = readings.get(entry.id);
      assert.ok(recorded, `${key}: ${entry.id} has an independent reading log`);
      for (const field of ['url', 'actual_sha256', 'retrieved_at_utc', 'read_at_utc', 'method', 'verified']) {
        assert.equal(entry[field], recorded[field], `${key}/${entry.id}: ${field}`);
      }
      assert.match(entry.actual_sha256, /^[a-f0-9]{64}$/);
      assert.equal(recorded.http_status, 200);
      assert.equal(entry.archival_identity, 'NOT_ESTABLISHED');
      assert.equal(entry.public_copy, 'NOT_REDISTRIBUTED');
      if (entry.physical_pages) {
        assert.deepEqual(entry.physical_pages, recorded.physical_pages);
        assert.ok(entry.physical_pages.every(page => Number.isInteger(page) && page >= 1 && page <= recorded.total_physical_pages));
      } else {
        assert.ok(entry.locator, `${key}: HTML reading needs a bounded locator`);
      }
      linked.add(entry.id);
    }
  }
  assert.deepEqual([...linked].sort(), [...readings.keys()].sort(), 'every RC3 reading is linked to a claim');
});

test('public evidence log integrity and reviewer-only historical additions remain explicit', () => {
  const log = bytes('research/editorial-source-register.json');
  const catalog = claims.file_catalog['research/editorial-source-register.json'];
  assert.equal(catalog.sha256, digest(log));
  assert.equal(catalog.bytes, log.length);
  for (const key of ['ASP24:4', 'ASP24:16', 'NGGroup:9']) {
    const review = claims.sources[key].rc3_reviewer_evidence;
    assert.equal(review.status, 'NOT_INDEPENDENTLY_REREAD_IN_RC3', key);
    assert.equal(review.sha256, registry.rc3_reverification.historical_review.sha256, key);
    assert.ok(review.locator && review.scope);
  }
});
