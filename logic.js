// Compatibility entry point for the existing UI and Node regression suite.
// All shared rules live in strict TypeScript; storage is an injected adapter.
export * from './src/domain/common.ts';
export * from './src/domain/catalog.ts';
export * from './src/domain/comparison.ts';
export * from './src/domain/state.ts';
export * from './src/domain/cart.ts';
export {readState, writeState} from './src/adapters/storage.ts';
