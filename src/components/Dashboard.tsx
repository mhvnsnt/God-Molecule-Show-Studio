'use client';

import React, { useState } from 'react';
import { mockEpisode } from '../data';
import { ProductionState, Shot } from '../types';
import { CheckCircle2, Circle, Loader2, XCircle, Play } from 'lucide-react';
import { motion } from 'motion/react';

export function Dashboard() {
  const [activeShot, setActiveShot] = useState<Shot>(mockEpisode.scenes[0].shots[0]);

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-zinc-950 text-white font-sans">
      <div className="flex-1 flex overflow-hidden">
        {/* Left column: Hierarchy */}
        <div className="w-80 border-r border-zinc-800 flex flex-col overflow-y-auto">
          <div className="p-4 border-b border-zinc-800 bg-zinc-900/50">
            <h2 className="text-lg font-semibold text-cyan-400">EPISODE</h2>
            <p className="text-zinc-300 text-sm mt-1">{mockEpisode.name}</p>
          </div>
          
          <div className="p-4 space-y-6">
            {mockEpisode.scenes.map(scene => (
              <div key={scene.id} className="space-y-3">
                <div>
                  <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Scene</h3>
                  <p className="text-sm text-zinc-200">{scene.name}</p>
                </div>
                
                <div className="space-y-1 pl-4 border-l-2 border-zinc-800">
                  <h4 className="text-[10px] font-bold text-zinc-600 uppercase tracking-wider mb-2">Shots</h4>
                  {scene.shots.map(shot => (
                    <button
                      key={shot.id}
                      onClick={() => setActiveShot(shot)}
                      className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                        activeShot.id === shot.id 
                          ? 'bg-zinc-800 text-white border border-zinc-700' 
                          : 'text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span>{shot.name}</span>
                        {shot.state.qc === 'checked' && <CheckCircle2 size={12} className="text-emerald-500" />}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right column: Preview & State */}
        <div className="flex-1 flex flex-col bg-black">
          {/* Main Preview Area */}
          <div className="flex-1 relative flex flex-col p-6 border-b border-zinc-900">
            <div className="flex justify-between items-end mb-4">
               <div>
                  <h2 className="text-2xl font-bold tracking-tight text-white">{activeShot.name}</h2>
                  <p className="text-zinc-400 text-sm mt-1 max-w-2xl">{activeShot.description}</p>
               </div>
               <button className="flex items-center space-x-2 bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-2 rounded transition-colors text-sm font-medium">
                 <Play size={16} />
                 <span>Play Render</span>
               </button>
            </div>
            
            <div className="flex-1 bg-zinc-900 rounded-lg overflow-hidden border border-zinc-800 relative flex items-center justify-center">
              {activeShot.thumbnailUrl ? (
                <motion.img 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  key={activeShot.id}
                  src={activeShot.thumbnailUrl} 
                  alt={activeShot.name} 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="text-zinc-600 flex flex-col items-center">
                  <Loader2 size={32} className="animate-spin mb-4 text-zinc-700" />
                  <span className="text-sm font-mono uppercase tracking-widest">Awaiting Render</span>
                </div>
              )}
              
              {/* Overlay UI elements */}
              <div className="absolute top-4 left-4 bg-black/60 backdrop-blur px-3 py-1.5 rounded text-xs font-mono text-zinc-300">
                CAM_01 // 24FPS
              </div>
              <div className="absolute bottom-4 right-4 bg-black/60 backdrop-blur px-3 py-1.5 rounded text-xs font-mono text-zinc-300">
                TC: 01:00:24:12
              </div>
            </div>
          </div>

          {/* Production State */}
          <div className="h-64 p-6 bg-zinc-950 font-mono text-xs uppercase overflow-y-auto">
            <h3 className="text-zinc-500 font-bold tracking-widest mb-4">Production State</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
              {Object.entries(activeShot.state).map(([stage, status]) => (
                <StatusCard key={stage} stage={stage} status={status as 'checked' | 'pending' | 'running' | 'failed'} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusCard({ stage, status }: { stage: string, status: 'checked' | 'pending' | 'running' | 'failed', key?: string }) {
  const getStatusColor = () => {
    switch(status) {
      case 'checked': return 'text-emerald-400 border-emerald-900 bg-emerald-950/30';
      case 'running': return 'text-amber-400 border-amber-900 bg-amber-950/30';
      case 'failed': return 'text-red-400 border-red-900 bg-red-950/30';
      default: return 'text-zinc-500 border-zinc-800 bg-zinc-900/20';
    }
  };

  const getStatusIcon = () => {
    switch(status) {
      case 'checked': return <CheckCircle2 size={16} />;
      case 'running': return <Loader2 size={16} className="animate-spin" />;
      case 'failed': return <XCircle size={16} />;
      default: return <Circle size={16} />;
    }
  };

  return (
    <div className={`p-4 rounded border flex flex-col items-center justify-center space-y-3 transition-colors ${getStatusColor()}`}>
      {getStatusIcon()}
      <span className="font-bold tracking-wider">{stage}</span>
      <span className="text-[10px] opacity-70">{status}</span>
    </div>
  );
}
