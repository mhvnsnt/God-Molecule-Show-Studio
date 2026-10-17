export type AppView =
  | 'preview'
  | 'episode-builder'
  | 'scene-builder'
  | 'character'
  | 'world-builder'
  | 'cosmology'
  | 'timeline'
  | 'bible';

export interface ProductionState {
  source: 'checked' | 'pending' | 'running' | 'failed' | 'unknown';
  identity: 'checked' | 'pending' | 'running' | 'failed' | 'unknown';
  asset: 'checked' | 'pending' | 'running' | 'failed' | 'unknown';
  animation: 'checked' | 'pending' | 'running' | 'failed' | 'unknown';
  audio: 'checked' | 'pending' | 'running' | 'failed' | 'unknown';
  composite: 'checked' | 'pending' | 'running' | 'failed' | 'unknown';
  qc: 'checked' | 'pending' | 'running' | 'failed' | 'unknown';
}

export interface MarsCharacterPackage {
  id: string;
  identity: {
    canonicalPhotos: string[];
    references: { front?: string; left?: string; right?: string; back?: string };
  };
  geometry: {
    sourceMesh?: string;
    cleanedMesh?: string;
    vertices?: number;
    faces?: number;
    topologyStatus: 'UNKNOWN' | 'PASS' | 'FAIL';
  };
  materials: {
    skin?: string;
    hair?: string;
    eyes?: string;
    sigil?: string;
  };
  rig: {
    skeletonStatus: 'UNKNOWN' | 'PASS' | 'FAIL';
    blendshapeCount?: number;
  };
  provenance: {
    sourceUrl?: string;
    sha256?: string;
    acquiredAt?: string;
  };
}

export interface Shot {
  id: string;
  name: string;
  description: string;
  state: ProductionState;
  thumbnailUrl?: string;
}

export interface Scene {
  id: string;
  name: string;
  description: string;
  shots: Shot[];
}

export interface Episode {
  id: string;
  name: string;
  synopsis: string;
  scenes: Scene[];
}

declare global {
  interface Window {
    google: any;
  }
}

export const INITIAL_PRODUCTION_STATE: ProductionState = {
  source: 'checked',
  identity: 'checked',
  asset: 'checked',
  animation: 'running',
  audio: 'pending',
  composite: 'pending',
  qc: 'pending',
};
