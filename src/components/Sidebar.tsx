import React from 'react';
import { AppView } from '../types';
import { Book, Film, LayoutDashboard, User, Globe, Clock } from 'lucide-react';

interface SidebarProps {
  currentView: AppView;
  onViewChange: (view: AppView) => void;
}

export function Sidebar({ currentView, onViewChange }: SidebarProps) {
  const navItems: { id: AppView; label: string; icon: React.ReactNode }[] = [
    { id: 'preview', label: 'Preview Dashboard', icon: <LayoutDashboard size={18} /> },
    { id: 'bible', label: 'Show Bible', icon: <Book size={18} /> },
    { id: 'episode-builder', label: 'Episode Builder', icon: <Film size={18} /> },
    { id: 'scene-builder', label: 'Scene Builder', icon: <Film size={18} /> },
    { id: 'character', label: 'Character: Mars', icon: <User size={18} /> },
    { id: 'world-builder', label: 'World Builder', icon: <Globe size={18} /> },
    { id: 'timeline', label: 'Timeline', icon: <Clock size={18} /> },
  ];

  return (
    <div className="w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col text-zinc-400 font-mono text-sm">
      <div className="p-6 border-b border-zinc-800">
        <h1 className="text-xl font-bold text-white tracking-widest uppercase">God Molecule</h1>
        <p className="text-xs mt-1 text-cyan-500">TRIPPEDD Studio</p>
      </div>
      
      <nav className="flex-1 py-4">
        <ul className="space-y-1 px-3">
          {navItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => onViewChange(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded transition-all duration-200 ${
                  currentView === item.id 
                    ? 'bg-zinc-800 text-white' 
                    : 'hover:bg-zinc-900 hover:text-zinc-200'
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>
      
      <div className="p-4 border-t border-zinc-800 text-xs text-zinc-600">
        System Status: <span className="text-emerald-500">ONLINE</span>
      </div>
    </div>
  );
}
