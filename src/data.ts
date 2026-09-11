import { Episode, INITIAL_PRODUCTION_STATE } from './types';

export const mockEpisode: Episode = {
  id: 'ep-01',
  name: 'Episode 01: The Recursive Room',
  synopsis: 'Mars finds himself in a room that seems to exist entirely within his own thoughts.',
  scenes: [
    {
      id: 'sc-01',
      name: 'Scene 01: The Awakening',
      description: 'Mars opens his eyes to a near-black space populated by tiny colored stars and cyan rim lights.',
      shots: [
        {
          id: 'sh-001',
          name: 'Shot 001',
          description: 'Close up on Mars\' solid glowing white eyes.',
          state: { ...INITIAL_PRODUCTION_STATE, animation: 'checked', audio: 'checked', composite: 'checked', qc: 'checked' },
          thumbnailUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop',
        },
        {
          id: 'sh-002',
          name: 'Shot 002',
          description: 'Pull back to reveal his cobalt skin and indigo dreads against the cosmic void.',
          state: { ...INITIAL_PRODUCTION_STATE, animation: 'checked', composite: 'running' },
          thumbnailUrl: 'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?q=80&w=2670&auto=format&fit=crop',
        },
        {
          id: 'sh-003',
          name: 'Shot 003',
          description: 'Mars speaks deadpan: "Yeah. That happens sometimes."',
          state: { ...INITIAL_PRODUCTION_STATE },
          thumbnailUrl: 'https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?q=80&w=2574&auto=format&fit=crop',
        },
      ],
    },
    {
      id: 'sc-02',
      name: 'Scene 02: Tonnō Pass',
      description: 'The reality degrades into a 640x480 quantized retro digital dream.',
      shots: [
        {
          id: 'sh-004',
          name: 'Shot 004',
          description: 'Mars realizes the universe is a cheap old video game.',
          state: { ...INITIAL_PRODUCTION_STATE, source: 'running', identity: 'pending', asset: 'pending' },
        },
      ],
    }
  ],
};
