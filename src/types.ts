export type AppView =
  | 'preview'
  | 'episode-builder'
  | 'scene-builder'
  | 'character'
  | 'world-builder'
  | 'timeline'
  | 'bible';

export interface ProductionState {
  source: 'checked' | 'pending' | 'running' | 'failed';
  identity: 'checked' | 'pending' | 'running' | 'failed';
  asset: 'checked' | 'pending' | 'running' | 'failed';
  animation: 'checked' | 'pending' | 'running' | 'failed';
  audio: 'checked' | 'pending' | 'running' | 'failed';
  composite: 'checked' | 'pending' | 'running' | 'failed';
  qc: 'checked' | 'pending' | 'running' | 'failed';
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

export const INITIAL_PRODUCTION_STATE: ProductionState = {
  source: 'checked',
  identity: 'checked',
  asset: 'checked',
  animation: 'running',
  audio: 'pending',
  composite: 'pending',
  qc: 'pending',
};
