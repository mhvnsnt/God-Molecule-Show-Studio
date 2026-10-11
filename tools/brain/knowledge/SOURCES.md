# Knowledge Corpus — Sources & License Status

`corpus/` holds plain-text/markdown sources for the show-doc brain's RAG index.
Every item is **public domain** (US, pre-1930 publication) or **openly licensed**
(CC BY-SA 4.0). Nothing copyrighted was included.

**Compatibility:** all files are `.md` (or `.txt`-clean markdown), each well under
the RAG indexer's 4 MB per-file cap. Chunker splits on markdown headers into
~1200-char chunks with 250-char overlap — verified with `index.py --roots corpus/`.

**Deliberately excluded (NOT public domain / NOT openly licensed):**
- Preston Blair, *Cartoon Animation* (Walter Foster, 1994) — still in copyright.
  The Lutz (1920) book below is the closest PD-era animation manual.
- Eisenstein, *Film Form* (1949); McKee, *Story*; *The Animator's Survival Kit*
  (Williams, 2001) — all in copyright.

## Animation (1)

| File | Work | License |
|---|---|---|
| `corpus/animation/lutz-animated-cartoons-1920.md` | E. G. Lutz, *Animated Cartoons: How They Are Made, Their Origin and Development* (Scribner's, 1920) — the earliest animation manual: persistence of vision, cel technique, in-betweening, timing | PD (US, 1920) — https://archive.org/details/animatedcartoons00lutz |

## Film theory & history (6)

| File | Work | License |
|---|---|---|
| `corpus/film/lindsay-art-of-the-moving-picture-1915.md` | Vachel Lindsay, *The Art of the Moving Picture* (1915) — first American film-theory book: film as hieroglyphic/moving sculpture | PD (US, 1915) — https://www.gutenberg.org/ebooks/13029 |
| `corpus/film/munsterberg-photoplay-1916.md` | Hugo Münsterberg, *The Photoplay: A Psychological Study* (1916) — attention, memory, emotion in film spectatorship | PD (US, 1916) — https://archive.org/details/photoplayapsych01mngoog |
| `corpus/film/talbot-moving-pictures-1912.md` | Frederick A. Talbot, *Moving Pictures: How They Are Made and Worked* (1912) — early cinema tech incl. trick film & animation precursors | PD (US, 1912) — https://archive.org/details/cu31924030699445 |
| `corpus/film/croy-how-motion-pictures-are-made-1918.md` | Homer Croy, *How Motion Pictures Are Made* (1918) — studio production, directing, scenario writing | PD (US, 1918) — https://archive.org/details/howmotionpictur00croygoog |
| `corpus/film/patterson-cinema-craftsmanship-1920.md` | Frances Taylor Patterson, *Cinema Craftsmanship: A Book for Photoplaywrights* (1920) — screenwriting structure, Columbia film course | PD (US, 1920) — https://archive.org/details/cinemacraftsman00pattgoog |
| `corpus/film/pudovkin-film-technique-1929.md` | V. I. Pudovkin, *Film Technique* (Newnes, 1929 English ed.) — montage theory, constructive editing, film acting | PD in US (1929; US copyright expired). NOTE: author died 1953, so it is NOT PD in life+70 jurisdictions. Keep usage US/internal. — https://archive.org/details/in.ernet.dli.2015.131461 |

## Color theory (3)

| File | Work | License |
|---|---|---|
| `corpus/color/snow-froehlich-theory-practice-of-color-1918.md` | Bonnie E. Snow & Hugo B. Froehlich, *The Theory and Practice of Color* (1918) — classroom color system, harmony exercises | PD (US, 1918) — https://archive.org/details/theorypracticeof00snow |
| `corpus/color/luckiesh-color-and-its-applications-1921.md` | Matthew Luckiesh, *Color and Its Applications* (1921) — physics & psychology of color, lighting, decoration | PD (US, 1921) — https://archive.org/details/coloranditsappl01luckgoog |
| `corpus/color/ridgway-color-standards-1912.md` | Robert Ridgway, *Color Standards and Color Nomenclature* (1912) — 1115 named color swatches, the standard artist reference of its era | PD (US, 1912) — https://archive.org/details/colorstandardsa01ridggoog |

## Drawing & art theory (7)

| File | Work | License |
|---|---|---|
| `corpus/art/dow-composition-1903.md` | Arthur Wesley Dow, *Composition* (1903) — line/notan/color structure; foundation of modern design teaching | PD (US, 1903) — https://archive.org/details/compositionaser00dowgoog |
| `corpus/art/crane-line-and-form-1900.md` | Walter Crane, *Line and Form* (1900) — decorative line, figure drawing for illustration | PD (US, 1900) — https://archive.org/details/lineform0000walt |
| `corpus/art/speed-practice-and-science-of-drawing-1913.md` | Harold Speed, *The Practice and Science of Drawing* (1913) — still the classic drawing manual: mass, line, tone, rhythm | PD (US, 1913) — https://www.gutenberg.org/ebooks/14264 |
| `corpus/art/ruskin-elements-of-drawing-1857.md` | John Ruskin, *The Elements of Drawing* (1857) — observation-first drawing exercises | PD (US, 1857) — https://www.gutenberg.org/ebooks/26716 |
| `corpus/art/parkhurst-painter-in-oil-1898.md` | Daniel Burleigh Parkhurst, *The Painter in Oil* (1898) — oil technique, values, color mixing | PD (US, 1898) — https://archive.org/details/painterinoilaco00parkgoog |
| `corpus/art/cross-light-and-shade-1897.md` | Anson K. Cross, *Light and Shade* (1897) — shading, charcoal/pencil/brush rendering | PD (US, 1897) — https://archive.org/details/lightandshadewi01crosgoog |
| `corpus/art/ross-on-drawing-and-painting-1912.md` | Denman Waldo Ross, *On Drawing and Painting* (1912) — Harvard design lectures: tone relations, color design | PD (US, 1912) — https://archive.org/details/ondrawingandpai03rossgoog |

## Music theory (130 files)

| Path | Work | License |
|---|---|---|
| `corpus/music/ham-rudiments-of-music-1900.md` | Albert Ham, *The Rudiments of Music and Elementary Harmony* (1900) | PD (US, 1900) — https://archive.org/details/rudimentsofmusic00hama |
| `corpus/music/diller-first-theory-book-1921.md` | Angela Diller, *First Theory Book* (1921) — beginner harmony | PD (US, 1921) — https://archive.org/details/firsttheorybook00dill |
| `corpus/music/open-music-theory/*.md` (128 files) | **Open Music Theory** — full modern college theory text: fundamentals, diatonic harmony, chromatic harmony, form, counterpoint, pop/rock, jazz | **CC BY-SA 4.0** — https://github.com/openmusictheory/openmusictheory.github.io (site: https://openmusictheory.github.io). Attribution + share-alike apply to these files. |

## Stats

- 149 files, ~8.8 MB total plain text
- Coverage: animation craft, film theory/history, screenwriting, color theory,
  drawing/painting technique, music theory (historical + modern)

## Rebuilding

Downloads were fetched with `/tmp/fetch_corpus.py` (not kept — it was a
one-shot; the recipe above is reproducible from the source URLs listed).
Re-running `python3 ../rag/index.py` picks up corpus files automatically if
`corpus/` is added to the indexer's crawl roots.
