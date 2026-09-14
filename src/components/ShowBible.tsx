import React from 'react';
import { motion } from 'motion/react';

export function ShowBible() {
  return (
    <div className="flex-1 bg-zinc-950 overflow-y-auto p-8 lg:p-16 text-zinc-300 font-sans">
      <div className="max-w-4xl mx-auto space-y-16">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="pb-8 border-b border-zinc-800"
        >
          <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-4 uppercase">
            God Molecule
          </h1>
          <h2 className="text-xl md:text-2xl text-cyan-500 font-light tracking-wide uppercase">
            Show / Production Bible
          </h2>
        </motion.div>

        <Section title="1. The Core Idea">
          <p>
            God Molecule is an adult surrealist animated/AI-assisted anthology about Mars, a deadpan, overconfident, psychedelic consciousness whose mind contains entire worlds.
          </p>
          <p>
            Mars is essentially a floating/disembodied head, but the underlying character asset is a complete head/neck/geometry model so the production system can animate him properly.
          </p>
          <p>Every episode can enter a completely different reality.</p>
          <div className="bg-zinc-900/50 p-6 rounded-lg border border-zinc-800 font-mono text-sm text-cyan-100/70">
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
              <li>a cheap old video game</li>
              <li>a psychedelic children's program</li>
              <li>an abandoned mall</li>
              <li>a cosmic horror landscape</li>
              <li>a suburban backyard</li>
              <li>a microscopic world</li>
              <li>a fake documentary</li>
              <li>a dream</li>
              <li>a medical simulation</li>
              <li>a 3D game</li>
              <li>crude 2D animation</li>
              <li>found footage</li>
              <li>live-action/AI-assisted footage</li>
              <li>a completely abstract universe</li>
            </ul>
          </div>
          <p className="text-white font-medium text-lg mt-6">
            But underneath the apparent randomness, everything is happening inside or through consciousness.
          </p>
          <blockquote className="border-l-4 border-cyan-500 pl-6 py-2 my-6 text-zinc-200 italic space-y-2">
            <p>What is reality?</p>
            <p>What is consciousness?</p>
            <p>What is identity?</p>
            <p>What happens when the observer becomes part of what is being observed?</p>
            <p>Is Mars experiencing the universe, or is the universe experiencing Mars?</p>
          </blockquote>
          <p className="font-bold text-white">And then it will immediately make a stupid joke.</p>
        </Section>

        <Section title="11. Mars">
          <p>Mars is the anchor.</p>
          <p>His personality:</p>
          <div className="flex flex-wrap gap-2 my-4">
            {['deadpan', 'overconfident', 'philosophical', 'stoner-ish', 'observant', 'casually arrogant', 'curious', 'emotionally strange', 'unpredictable'].map(trait => (
              <span key={trait} className="px-3 py-1 bg-zinc-900 border border-zinc-800 rounded-full text-xs font-mono text-zinc-400">
                {trait}
              </span>
            ))}
          </div>
          <p>He can be simultaneously:</p>
          <blockquote className="border-l-4 border-magenta-500 pl-6 py-2 my-4 text-white font-mono text-sm">
            the narrator, protagonist, observer, creator, prisoner, god, idiot and audience.
          </blockquote>
        </Section>

        <Section title="13. Mars' Approved Visual Language">
          <div className="space-y-8">
            <div>
              <h4 className="text-cyan-400 font-bold uppercase tracking-wider mb-2">Skin</h4>
              <p>Cobalt / electric blue. Not generic blue. It needs saturated cobalt, cyan interaction, dimensional shading, painterly texture, granular digital breakup.</p>
            </div>
            <div>
              <h4 className="text-indigo-400 font-bold uppercase tracking-wider mb-2">Hair</h4>
              <p>Indigo / violet dreads. Dark enough to disappear into black space sometimes, but containing violet, magenta, blue, subtle information, painterly texture.</p>
            </div>
            <div>
              <h4 className="text-white font-bold uppercase tracking-wider mb-2">Eyes</h4>
              <p>Solid glowing white. Not realistic eyeballs. The eyes are an intentional graphic element.</p>
            </div>
          </div>
        </Section>

        <Section title="21. God Molecule Creative Constitution">
          <ol className="list-decimal pl-5 space-y-3 font-mono text-sm text-zinc-400">
            <li><span className="text-zinc-200">Mars's identity is immutable unless explicitly changed.</span></li>
            <li>Canonical references outrank generated interpretations.</li>
            <li>Generated media is subordinate to source identity.</li>
            <li><span className="text-zinc-200">Style may change; identity may not drift.</span></li>
            <li>Imperfection may be intentional.</li>
            <li>Technical failure is never automatically treated as style.</li>
            <li>Every episode may establish its own visual reality.</li>
            <li>Reality transitions are a storytelling mechanism.</li>
            <li>Death may produce progression rather than reset.</li>
            <li>Comedy and philosophy coexist.</li>
            <li>Surrealism must have internal logic, even when the audience cannot see it.</li>
            <li>The audience should be allowed to interpret.</li>
            <li>Never explain a mystery merely because the system can.</li>
            <li>Visual experimentation is encouraged.</li>
            <li>Provenance and source assets must always be preserved.</li>
          </ol>
        </Section>
        
        <Section title="The God Molecule Cosmology">
           <p>Mars isn't simply carrying a universe around in his head. His consciousness is a cosmological substrate.</p>
           <p>Inside his consciousness can exist:</p>
           <div className="bg-zinc-900/50 p-6 rounded-lg border border-zinc-800 text-sm">
             thoughts → memories → simulated realities → dimensions → universes → multiverses → galaxies → microscopic worlds → quantum-scale phenomena → abstract mathematical spaces
           </div>
           <blockquote className="border-l-4 border-cyan-500 pl-6 py-2 my-6 text-zinc-200 italic">
             "Is Mars containing everything, or is something containing Mars?"
           </blockquote>
        </Section>
        <Section title="God Molecule 3D World / Gaussian Splat Theme">
          <p>
            Reality can be rendered as a navigable radiance-field substrate: scanned or reconstructed spaces become Gaussian-splat worlds that can coexist with conventional Blender geometry, the real Mars character, procedural molecular structures, particles, lighting and effects.
          </p>
          <p>
            This is a background visual grammar for Mars's consciousness, not a replacement for the story bible or canonical character. Worlds may transform radically while Mars's identity remains stable.
          </p>
          <div className="bg-zinc-900/50 p-6 rounded-lg border border-zinc-800 text-sm">
            physical scene → radiance field → molecular/procedural layer → animation → cinematic render
          </div>
          <p>
            The studio concept includes Layout, Modeling, Splatting, Shading, Animation, AI Director and Rendering workspaces, with viewport modes for wireframe, solid, material, splats, quantum and cinematic presentation. Camera, world, molecular and character tracks share a production timeline.
          </p>
          <p>
            AI may propose worlds, analyze references, generate panoramic environments, direct shots, create temporary cinematic previews, score scenes and provide voice interfaces. Execution remains physical and evidence-backed: real artifacts, pixels, provenance, SHA-256 and receipts outrank UI claims.
          </p>
        </Section>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string, children: React.ReactNode }) {
  return (
    <motion.section 
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 0, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      className="space-y-4"
    >
      <h3 className="text-2xl font-bold text-white uppercase tracking-tight">{title}</h3>
      <div className="space-y-4 leading-relaxed text-zinc-400">
        {children}
      </div>
    </motion.section>
  );
}