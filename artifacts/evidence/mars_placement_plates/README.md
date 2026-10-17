# Mars placement plates

These are the operator-supplied placement references for the MARS_LOD2 facial rig pipeline.

## Source attachments

- `1000168411.png` — source attachment SHA-256: `291a42ba82d3bd2d94a84638ead374d2111dab74b5fdc7320b9597f0f071de75`
- `1000168416.png` — source attachment SHA-256: `e893a4fbb3ed1f084ae1fa6a11b0cfa2b4040d4d1917b9a742893d6de4ea8284`

The repository stores compact JPEG working references derived from those uploads so GitHub-based agents can inspect the placement visually without depending on the chat attachment state.

## Mark semantics

- **Red:** brow / upper orbital placement constraint.
- **Yellow:** upper eyelid and nostril placement constraint.
- **Green:** lower eyelid placement constraint.

These marks are **placement constraints only**. They are not MVMP-478 landmark truth and must not be baked into MARS_CANONICAL geometry.

## Production rule

Use these plates to validate the measured head-frame placement of semantic eyelids, sockets, brows, and nostrils. The production gate remains fail-closed:

`real MARS_LOD2.glb -> MVMP 478 landmarks -> semantic eyelids -> eye sockets -> face rig -> actual blink -> actual PNG evidence -> brow/eyelid measurements -> PASS/FAIL`

No donor head, generated replacement mesh, or `MARS_source.glb` substitute may satisfy the MARS_LOD2 input gate.

The final validation must use a no-specular capture and clipping/protrusion checks so lid margins cannot visually blow out or detach from the measured head frame.
