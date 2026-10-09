export const isRecord = (value: unknown): value is Record<string, unknown> => value !== null && typeof value === 'object' && !Array.isArray(value) && (Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null);
export const record = (value: unknown): Record<string, unknown> => value !== null && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
export const uniqueStrings = (value: unknown): string[] => [...new Set(Array.isArray(value) ? value.filter((entry): entry is string => typeof entry === 'string') : [])];
export const unsafeKeys = new Set(['__proto__', 'constructor', 'prototype', 'toString']);
export function hasUnsafeKeys(value: unknown): boolean {
  return value !== null && typeof value === 'object' && Object.entries(value).some(([key, entry]) => unsafeKeys.has(key) || hasUnsafeKeys(entry));
}
export const cloneJson = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
