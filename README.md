# God Molecule Show Studio

The show-specific creative cockpit for **God Molecule** — episode/scene/shot state,
the show bible, the cosmology, and the bridge that pulls MARS's canonical asset out
of Drive and hands it to the TRIPPEDD production toolchain.

**Next.js 15 (App Router) · React 19 · TypeScript · Tailwind v4.**

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npm run start    # serve the build
npm run lint     # tsc --noEmit
```

## Layout

```
app/
  layout.tsx                     page shell, metadata, Google Identity Services
  page.tsx                       the cockpit; view switch over the modules
  globals.css                    Tailwind v4 + the dark scrollbar theme
  api/health/route.ts            GET  -> {"status":"TRIPPEDD RUNTIME ONLINE"}
  api/trippedd/ingest/route.ts   POST -> a STREAM of production log lines
lib/driveDownload.ts             public-Drive fetch: redirect + confirm-token paths
src/components/                  Sidebar · Dashboard · ShowBible · Cosmology · Character
src/types.ts  src/data.ts        production state model + the mock episode
tools/                           the python side: asset inspection, proxy build
```

## The ingest route is a stream, and it is deliberately pessimistic

`POST /api/trippedd/ingest` takes `{ token, url }` and streams `text/plain` line by
line while it works, so the Character view's terminal fills in real time rather than
waiting on one big response. The client reads it with a `ReadableStream` reader and
treats the line containing `EOF_SUCCESS` as the terminator.

It runs the authenticated Drive path when a token is present and falls back to the
public path when the API refuses — and it hashes the bytes it actually wrote, so the
`SHA-256` line describes the file on disk, not a second read of it.

**A stage that did not run reports that it did not run.** When the asset inspector is
missing a dependency or the topology check does not pass, the route emits
`PENDING CAPABILITY` / `MARS_CANONICAL: INCOMPLETE` — never a clean result. An
inspector that never executed cannot testify that a mesh is good, and the most
expensive bugs in this production system have all been a "not attempted" that looked
exactly like a "attempted and found nothing".

Measured end to end against the canonical Drive source:

```
[DRIVE] Download complete. Bytes read: 61846048
[DRIVE] SHA-256: e317d06aba68c7cdf56a3e3a0b639770714a8a1f7287897f74672cb191d0fff1
[ASSET] MARS_CANONICAL: INCOMPLETE (Awaiting 3D toolchain validation)
```

That hash is byte-identical to the canonical MARS source recorded in
TRIPPEDD-Production-studios- (`tools/character/fetch_mars_canonical.sh`).

## Notes for agents working in here

- `.trippedd_assets/` is tracked **except** the raw `mars_source_*.glb`, which is
  62 MB and re-fetchable from its Drive file id. Proxies, renders and QC frames in
  there are evidence and stay committed.
- Every component under `src/components/` is a client component (hooks, `window`,
  streaming `fetch`). `app/page.tsx` carries the `'use client'` boundary.
- The python tools the ingest route shells out to live in `tools/` and are expected
  to print JSON on stdout. They fail closed.
