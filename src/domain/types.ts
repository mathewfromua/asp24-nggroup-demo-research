/** Stable product IDs identify a specific model/revision, independently of display names or SKU. */
export type Brand = 'asp' | 'ng';
export type GroupId = 'ups' | 'optics' | 'switches' | 'cable' | 'wifi' | 'splitters' | 'meters' | 'injectors';
export type Scalar = string | number | boolean;
export interface KnownParameter { status: 'known'; value: Scalar; unit?: string }
export type ParameterValue = KnownParameter
  | { status: 'unknown' | 'missing' | 'not-applicable'; reason?: string }
  | { status: 'conflicting'; values: KnownParameter[]; reason?: string };
export interface Product {
  id: string; group: GroupId; name: string; sku: string; code: string;
  manufacturer: string; family: string; typeLabel: string;
  price: number; available: boolean; availabilityState?: string;
  ng: boolean; unit: string; revision: string; aliases?: string[];
  desc?: string; compat?: string; isDemo?: boolean; sourceKind?: string;
  props: Record<string, Scalar | null | ParameterValue>;
  numericFacets?: Record<string, {value: number | null; unit: string; derivedFrom: string}>;
  unitDefinition?: {kind: 'piece' | 'reel'; integerOnly: true; lengthM?: number};
  knownMissingFields?: string[];
}
export interface ProductGroup {
  icon: string; label: string; filters: string[]; description: string;
  name: string; typeLabel: string; family: string; keys: string[];
  numericFacetDefinitions: [string, string, string][];
}
export interface ConsultationDraft { purpose: string; quantity: string; question: string }
export interface ComparisonUndo { group: GroupId; id: string; at: number; pair: string[]; replacementId?: string }
export interface Checkout { alias: string; delivery: string; payment: string; note: string }
export interface Recovery { version: 1; rawState: string; quarantinedOrders: unknown[] }
export interface DemoState {
  version: 4; science: Record<string, unknown> | ScienceState; recovery: Recovery | null;
  orders: unknown[]; checkout: Checkout; cart: Record<string, number>; favorites: string[];
  compareByGroup: Record<GroupId, string[]>; listName: string; note: string;
  catalogs: Record<Brand, string>; drafts: Record<string, ConsultationDraft>;
  view: {
    catalogViews: Record<Brand, 'cards' | 'list' | 'series'>;
    comparisonDialog: {type: 'details'; id: string} | null;
    group: GroupId; differences: boolean; expanded: boolean; compareBrand: Brand; compareExperience: 'classic' | 'modern';
    research: Record<GroupId, {scroll: number; x: number; row: string; offset: number}>;
    pairs: Record<GroupId, string[]>;
    pages: Record<string, {scroll: number; details: boolean[]; focus: string}>;
  };
}
export interface ProjectReference { title: string; url: string; productId?: string }
export interface Project {
  id: string; name: string; note: string; candidates: string[]; chosen: string[];
  quantities: Record<string, number>; references: ProjectReference[];
  createdAt: string; updatedAt: string;
}
export interface ScienceState {
  version: 1; projects: Project[]; activeProjectId: string | null; nextProjectSeq: number;
  quarantine: unknown[];
}
