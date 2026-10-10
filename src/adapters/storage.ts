import type {DemoState} from '../domain/types.ts';
import {STATE_KEY} from '../domain/common.ts';
import {record} from '../domain/validation.ts';
import {initialState, migrateState} from '../domain/state.ts';
/** Minimal port; callers inject local, session, or isolated in-memory storage. */
export interface StateStorage {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
}
export function readState(storage: StateStorage): {state: DemoState; status: 'ok' | 'recovery' | 'corrupt' | 'denied'} {
  let raw: string | null | undefined;
  try { raw = storage.getItem(STATE_KEY); const parsed = raw ? JSON.parse(raw) : null; const state = migrateState(parsed); if (state.recovery && !record(parsed).recovery) state.recovery.rawState = raw ?? ''; return {state, status: state.recovery ? 'recovery' : 'ok'}; }
  catch (error) { const state = initialState(); if (error instanceof SyntaxError && typeof raw === 'string') state.recovery = {version: 1, rawState: raw, quarantinedOrders: []}; return {state, status: error instanceof SyntaxError ? 'corrupt' : 'denied'}; }
}
export function writeState(storage: StateStorage, state: DemoState): boolean {
  try {
    let next = state;
    // A normal write must never erase unreadable historical orders. Explicit demo
    // reset may clear working records, but their recoverable source remains.
    if (!state.recovery && typeof storage.getItem === 'function') {
      const previous = readState(storage);
      if (previous.status === 'denied') return false;
      if (previous.state.recovery) next = {...state, recovery: previous.state.recovery};
    }
    storage.setItem(STATE_KEY, JSON.stringify(next)); return true;
  } catch { return false; }
}
