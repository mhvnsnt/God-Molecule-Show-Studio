'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { Database, UploadCloud, CheckCircle2, AlertCircle, Loader2, Link } from 'lucide-react';

export function CharacterView() {
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [assetStatus, setAssetStatus] = useState<'missing' | 'incomplete' | 'canonical'>('missing');
  const [driveUrl, setDriveUrl] = useState('https://drive.google.com/file/d/1RKxHGkgoKe0hZf7a2kObqzKpgqKfkrhl/view?usp=drivesdk');
  const tokenClientRef = useRef<any>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const hasStartedRef = useRef(false);

  useEffect(() => {
    // Initialize Google Identity Services token client
    if (window.google && window.google.accounts && window.google.accounts.oauth2) {
      tokenClientRef.current = window.google.accounts.oauth2.initTokenClient({
        client_id: '441835407149-qj9eif7h2g83klr8a5t6o890hcd3.apps.googleusercontent.com', 
        scope: 'https://www.googleapis.com/auth/drive.readonly',
        callback: (tokenResponse: any) => {
          setIsAuthenticating(false);
          if (tokenResponse.error) {
            setLogs(prev => [...prev, `[AUTH ERROR] ${tokenResponse.error}`]);
            return;
          }
          handleIngestion(tokenResponse.access_token);
        },
      });
    }

    // Automatically trigger ingestion on mount
    if (!hasStartedRef.current) {
      hasStartedRef.current = true;
      setLogs(prev => [...prev, '[SYSTEM] Automated ingestion triggered...']);
      handleIngestion(null);
    }
  }, []);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleConnectDrive = () => {
    if (!driveUrl) {
      setLogs(prev => [...prev, '[SYSTEM] Please provide a valid Google Drive URL.']);
      return;
    }
    
    setIsAuthenticating(true);
    setLogs(prev => [...prev, '[SYSTEM] Initiating Google Drive OAuth fallback flow...']);
    
    try {
      if (tokenClientRef.current) {
         tokenClientRef.current.requestAccessToken();
      } else {
         throw new Error("GSI not loaded");
      }
    } catch (e) {
      console.warn("GSI auth failed", e);
      setIsAuthenticating(false);
      setLogs(prev => [...prev, `[FATAL] Identity Services failed to initialize.`]);
    }
  };

  const handleIngestion = async (token: string | null) => {
    setIsIngesting(true);
    if (token) {
        setLogs(prev => [...prev, '[SYSTEM] Token acquired. Connecting to TRIPPEDD production bridge...']);
    } else {
        setLogs(prev => [...prev, '[SYSTEM] Connecting to TRIPPEDD production bridge (Unauthenticated mode)...']);
    }
    
    try {
      const res = await fetch('/api/trippedd/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, url: driveUrl })
      });
      
      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep the last incomplete line in the buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim()) {
            setLogs(prev => [...prev, line]);
            
            if (line.includes('EOF_SUCCESS')) {
              setAssetStatus('incomplete');
            }
          }
        }
      }
      
    } catch (err: any) {
      setLogs(prev => [...prev, `[FATAL] Bridge connection failed: ${err.message}`]);
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <div className="flex-1 bg-zinc-950 flex font-sans text-zinc-300 h-full overflow-hidden">
      {/* Left Panel: Asset Status */}
      <div className="w-1/2 p-12 border-r border-zinc-800 flex flex-col justify-center">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="max-w-md"
        >
          <h2 className="text-4xl font-black text-white uppercase tracking-tight mb-2">Character: Mars</h2>
          <p className="text-zinc-500 mb-12">TRIPPEDD Asset Production Pipeline</p>

          <div className="space-y-8">
            <div className="bg-black border border-zinc-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-mono text-sm tracking-widest uppercase text-zinc-400">Canonical 3D Head</h3>
                {assetStatus === 'canonical' ? (
                  <span className="flex items-center text-emerald-500 text-xs font-mono bg-emerald-500/10 px-2 py-1 rounded border border-emerald-900">
                    <CheckCircle2 size={14} className="mr-2" /> ACQUIRED
                  </span>
                ) : assetStatus === 'incomplete' ? (
                  <span className="flex items-center text-amber-500 text-xs font-mono bg-amber-500/10 px-2 py-1 rounded border border-amber-900">
                    <AlertCircle size={14} className="mr-2" /> INCOMPLETE
                  </span>
                ) : (
                  <span className="flex items-center text-red-500 text-xs font-mono bg-red-500/10 px-2 py-1 rounded border border-red-900">
                    <AlertCircle size={14} className="mr-2" /> MISSING
                  </span>
                )}
              </div>
              
              <p className="text-sm text-zinc-500 mb-6">
                Automated ingestion routine active. Acquiring canonical Tripo 3D head geometry to lock Mars' identity across generation backends.
              </p>

              <div className="space-y-4">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Link size={16} className="text-zinc-600" />
                  </div>
                  <input
                    type="text"
                    value={driveUrl}
                    onChange={(e) => setDriveUrl(e.target.value)}
                    placeholder="Paste Google Drive URL..."
                    className="w-full bg-zinc-900 border border-zinc-800 rounded pl-10 pr-4 py-2.5 text-sm text-zinc-300 placeholder:text-zinc-700 focus:outline-none focus:border-cyan-900 focus:ring-1 focus:ring-cyan-900 transition-colors"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <button 
                    onClick={() => handleIngestion(null)}
                    disabled={!driveUrl || isAuthenticating || isIngesting || assetStatus === 'canonical'}
                    className="flex items-center justify-center space-x-2 bg-cyan-900/30 text-cyan-400 hover:bg-cyan-900/50 border border-cyan-900/50 disabled:opacity-50 disabled:hover:bg-cyan-900/30 px-4 py-3 rounded font-medium transition-colors text-sm"
                  >
                    {isIngesting ? <Loader2 size={16} className="animate-spin" /> : <UploadCloud size={16} />}
                    <span>Process Asset</span>
                  </button>

                  <button 
                    onClick={handleConnectDrive}
                    disabled={!driveUrl || isAuthenticating || isIngesting || assetStatus === 'canonical'}
                    className="flex items-center justify-center space-x-2 bg-zinc-100 text-zinc-900 hover:bg-white disabled:opacity-50 disabled:hover:bg-zinc-100 px-4 py-3 rounded font-medium transition-colors text-sm"
                  >
                    {isAuthenticating ? <Loader2 size={16} className="animate-spin" /> : <UploadCloud size={16} />}
                    <span>Auth (Private)</span>
                  </button>
                </div>
              </div>
              
              <p className="text-[10px] text-zinc-600 font-mono mt-4 text-center">
                Paste URL to resolve accessible file. Use 'Auth' if the asset is in a private Drive.
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Right Panel: Production Logs */}
      <div className="w-1/2 bg-black p-8 flex flex-col">
        <div className="flex items-center space-x-2 mb-6">
          <Database size={16} className="text-cyan-500" />
          <h3 className="font-mono text-xs tracking-widest uppercase text-cyan-500">TRIPPEDD Pipeline Output</h3>
        </div>
        
        <div className="flex-1 border border-zinc-900 rounded bg-zinc-950 p-4 font-mono text-[11px] overflow-y-auto leading-relaxed">
          {logs.length === 0 && (
             <span className="text-zinc-700">Waiting for production ingestion...</span>
          )}
          {logs.map((log, i) => {
            if (log.includes('EOF_SUCCESS')) return null;
            return (
              <motion.div 
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                key={i} 
                className={`mb-2 ${log.includes('[ERROR]') || log.includes('[FATAL]') ? 'text-red-400' : 
                                  log.includes('UNKNOWN') || log.includes('INCOMPLETE') ? 'text-amber-400' :
                                  log.includes('[SYSTEM]') || log.includes('[DRIVE]') || log.includes('[BOOTSTRAP]') || log.includes('[INSPECTOR]') ? 'text-cyan-600' : 
                                  log.includes('PASS') || log.includes('successful') || log.includes('VERIFIED') ? 'text-emerald-400' : 
                                  'text-zinc-400'}`}
              >
                <span className="opacity-40 mr-3">{new Date().toISOString().split('T')[1].substring(0,8)}</span>
                {log}
              </motion.div>
            )
          })}
          {(isAuthenticating || isIngesting) && (
            <div className="mt-4 flex items-center space-x-2 text-zinc-600 animate-pulse">
               <Loader2 size={12} className="animate-spin" />
               <span>Processing pipeline block...</span>
            </div>
          )}
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  );
}
