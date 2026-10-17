import React, { useState } from 'react';
import { AppView } from './types';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { ShowBible } from './components/ShowBible';
import { Cosmology } from './components/Cosmology';
import { CharacterView } from './components/Character';
import { FileCode2 } from 'lucide-react';

export default function App() {
  const [currentView, setCurrentView] = useState<AppView>('preview');

  return (
    <div className="flex h-screen w-full bg-black overflow-hidden font-sans selection:bg-cyan-900 selection:text-cyan-50">
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />
      
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {currentView === 'preview' && <Dashboard />}
        {currentView === 'bible' && <ShowBible />}
        {currentView === 'cosmology' && <Cosmology />}
        {currentView === 'character' && <CharacterView />}
        
        {/* Placeholders for other views */}
        {['episode-builder', 'scene-builder', 'world-builder', 'timeline'].includes(currentView) && (
          <div className="flex-1 bg-zinc-950 flex flex-col items-center justify-center text-zinc-500">
            <FileCode2 size={64} className="mb-6 opacity-20" />
            <h2 className="text-xl font-mono tracking-widest uppercase text-zinc-400 mb-2">Module Not Initialized</h2>
            <p className="max-w-md text-center text-sm">
              The <span className="text-cyan-500">{currentView}</span> module is part of the TRIPPEDD underlying production infrastructure and is currently offline or pending integration.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
