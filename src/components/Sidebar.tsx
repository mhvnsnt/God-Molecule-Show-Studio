import React, { useState } from 'react';
import { AppView } from '../types';
import { Book, Film, LayoutDashboard, User, Globe, Clock, Orbit, PanelLeftClose, PanelLeftOpen } from 'lucide-react';

interface SidebarProps {
  currentView: AppView;
  onViewChange: (view: AppView) => void;
}

export function Sidebar({ currentView, onViewChange }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navItems: { id: AppView; label: string; icon: React.ReactNode }[] = [
    { id: 'preview', label: 'Preview Dashboard', icon: <LayoutDashboard size={18} /> },
    { id: 'bible', label: 'Show Bible', icon: <Book size={18} /> },
    { id: 'episode-builder', label: 'Episode Builder', icon: <Film size={18} /> },
    { id: 'scene-builder', label: 'Scene Builder', icon: <Film size={18} /> },
    { id: 'character', label: 'Character: Mars', icon: <User size={18} /> },
    { id: 'world-builder', label: 'World Builder', icon: <Globe size={18} /> },
    { id: 'cosmology', label: 'Cosmology', icon: <Orbit size={18} /> },
    { id: 'timeline', label: 'Timeline', icon: <Clock size={18} /> },
  ];

  return (
    <div className={`bg-zinc-950 border-r border-zinc-800 flex flex-col text-zinc-400 font-mono text-sm transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64 shrink-0'}`}>
      <div className={`p-4 border-b border-zinc-800 flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
        {!isCollapsed && (
          <div className="overflow-hidden">
            <h1 className="text-xl font-bold text-white tracking-widest uppercase truncate">God Molecule</h1>
            <p className="text-[10px] mt-1 text-cyan-500 truncate">TRIPPEDD Studio</p>
          </div>
        )}
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)} 
          className="p-1 hover:text-white transition-colors shrink-0"
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          {isCollapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
        </button>
      </div>
      
      <nav className="flex-1 py-4 overflow-y-auto overflow-x-hidden scrollbar-hide">
        <ul className="space-y-1 px-2">
          {navItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => onViewChange(item.id)}
                title={isCollapsed ? item.label : undefined}
                className={`w-full flex items-center ${isCollapsed ? 'justify-center px-0' : 'space-x-3 px-3'} py-2.5 rounded transition-all duration-200 ${
                  currentView === item.id 
                    ? 'bg-zinc-800 text-white' 
                    : 'hover:bg-zinc-900 hover:text-zinc-200'
                }`}
              >
                <div className="shrink-0">{item.icon}</div>
                {!isCollapsed && <span className="truncate">{item.label}</span>}
              </button>
            </li>
          ))}
        </ul>
      </nav>
      
      {!isCollapsed && (
        <div className="p-4 border-t border-zinc-800 text-[10px] text-zinc-600 truncate">
          System Status: <span className="text-emerald-500">ONLINE</span>
        </div>
      )}
    </div>
  );
}
