'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ZoomIn, ZoomOut, Infinity as InfinityIcon } from 'lucide-react';

const COSMOLOGY_LAYERS = [
  { id: 'thought', name: 'A Tiny Thought', desc: 'A fleeting conceptual manifestation inside a mind.' },
  { id: 'consciousness', name: 'Another Consciousness', desc: 'A mind containing the entire lower cascade.' },
  { id: 'another-mars', name: 'Another Mars', desc: 'A parallel observer experiencing the cascade.' },
  { id: 'another-reality', name: 'Another Reality', desc: 'A distinct ontological framework.' },
  { id: 'dimensions', name: 'Dimensions', desc: 'Planes of existence beyond standard spacetime.' },
  { id: 'multiverse', name: 'A Multiverse', desc: 'A cluster of parallel or branching realities.' },
  { id: 'galaxies', name: 'Galaxies', desc: 'Massive gravitationally bound systems of stars and worlds.' },
  { id: 'universe', name: 'A Universe', desc: 'An entire cosmological instance folded inside.' },
  { id: 'quantum', name: 'Quantum Structures', desc: 'Probability fields and subatomic indeterminacy.' },
  { id: 'atoms', name: 'Atoms', desc: 'The fundamental atomic framework.' },
  { id: 'molecules', name: 'Molecules', desc: 'Chemical structures binding reality together.' },
  { id: 'cells', name: 'Cells', desc: 'Biological building blocks of the organism.' },
  { id: 'mars-eye', name: 'Mars\'s Eye', desc: 'The biological and perceptual anchor of the observer.' }
];

export function Cosmology() {
  // Start somewhere in the middle
  const [currentIndex, setCurrentIndex] = useState(7);
  const [direction, setDirection] = useState(1); // 1 = inward, -1 = outward

  const zoomIn = () => {
    setDirection(1);
    setCurrentIndex((prev) => (prev + 1) % COSMOLOGY_LAYERS.length);
  };

  const zoomOut = () => {
    setDirection(-1);
    setCurrentIndex((prev) => (prev - 1 + COSMOLOGY_LAYERS.length) % COSMOLOGY_LAYERS.length);
  };

  const currentLayer = COSMOLOGY_LAYERS[currentIndex];
  const outerLayer = COSMOLOGY_LAYERS[(currentIndex - 1 + COSMOLOGY_LAYERS.length) % COSMOLOGY_LAYERS.length];
  const innerLayer = COSMOLOGY_LAYERS[(currentIndex + 1) % COSMOLOGY_LAYERS.length];

  return (
    <div className="flex-1 bg-black flex flex-col items-center justify-center relative overflow-hidden font-sans">
       {/* Background effects */}
       <div className="absolute inset-0 opacity-20 pointer-events-none flex items-center justify-center">
         <div className="w-[80vw] h-[80vw] max-w-[800px] max-h-[800px] border-[1px] border-cyan-900/30 rounded-full absolute animate-[spin_60s_linear_infinite]" />
         <div className="w-[60vw] h-[60vw] max-w-[600px] max-h-[600px] border-[1px] border-magenta-900/20 rounded-full absolute animate-[spin_40s_linear_infinite_reverse]" />
         <div className="w-[40vw] h-[40vw] max-w-[400px] max-h-[400px] border-[1px] border-cyan-500/10 rounded-full absolute" />
       </div>

       {/* Main Visualization */}
       <div className="relative z-10 w-full max-w-4xl flex flex-col items-center px-8">
         <div className="flex items-center space-x-3 mb-16 text-zinc-500 font-mono text-xs uppercase tracking-[0.2em] md:tracking-[0.3em] text-center">
           <InfinityIcon size={14} className="text-cyan-500 hidden md:block" />
           <span>There is no guaranteed outside</span>
           <InfinityIcon size={14} className="text-magenta-500 hidden md:block" />
         </div>

         <div className="relative w-full h-48 md:h-64 flex items-center justify-center">
           <AnimatePresence mode="popLayout" custom={direction}>
             <motion.div
               key={currentIndex}
               custom={direction}
               initial={{ opacity: 0, scale: direction > 0 ? 3 : 0.3, filter: 'blur(10px)' }}
               animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
               exit={{ opacity: 0, scale: direction > 0 ? 0.3 : 3, filter: 'blur(10px)' }}
               transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
               className="absolute flex flex-col items-center text-center w-full"
             >
               <h2 className="text-4xl md:text-7xl font-black text-white tracking-tighter mb-4 drop-shadow-2xl px-4 leading-tight">
                 {currentLayer.name}
               </h2>
               <p className="text-base md:text-xl text-cyan-200/70 font-light max-w-2xl px-4">
                 {currentLayer.desc}
               </p>
             </motion.div>
           </AnimatePresence>
         </div>

         {/* Navigation Controls */}
         <div className="mt-20 flex flex-col items-center space-y-8">
           <div className="flex items-center space-x-8 md:space-x-16">
             <button
               onClick={zoomOut}
               className="group flex flex-col items-center space-y-4 transition-opacity hover:opacity-80 w-32"
             >
               <div className="w-16 h-16 rounded-full border border-zinc-800 bg-zinc-950 flex items-center justify-center text-zinc-400 group-hover:border-cyan-500/50 group-hover:text-cyan-400 transition-colors shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                 <ZoomOut size={24} />
               </div>
               <div className="text-center">
                 <span className="block text-[10px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Zoom Out To</span>
                 <span className="block text-xs md:text-sm text-zinc-300 font-medium truncate w-full">{outerLayer.name}</span>
               </div>
             </button>

             <div className="w-px h-24 bg-gradient-to-b from-transparent via-zinc-800 to-transparent" />

             <button
               onClick={zoomIn}
               className="group flex flex-col items-center space-y-4 transition-opacity hover:opacity-80 w-32"
             >
               <div className="w-16 h-16 rounded-full border border-zinc-800 bg-zinc-950 flex items-center justify-center text-zinc-400 group-hover:border-magenta-500/50 group-hover:text-magenta-400 transition-colors shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                 <ZoomIn size={24} />
               </div>
               <div className="text-center">
                 <span className="block text-[10px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Zoom In To</span>
                 <span className="block text-xs md:text-sm text-zinc-300 font-medium truncate w-full">{innerLayer.name}</span>
               </div>
             </button>
           </div>
         </div>
       </div>
    </div>
  );
}
