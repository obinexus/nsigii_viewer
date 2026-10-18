# Viewer integration — the dispatch front end

`nsigii-viewer.html` classifies whatever bytes it is handed by the **first 8
bytes** (the shared contract in
[`obinexusmk2/nsigii` → `docs/DISPATCH.md`](https://github.com/obinexusmk2/nsigii/blob/main/docs/DISPATCH.md))
and routes:

```
open(bytes)
  ├─ NSIGII01            → decode with the C/WASM codec → re-dispatch the result
  ├─ NSIGII\0 + 0x07     → verify the trident (browser Web Crypto). 3/3 YES →
  │                        extract → re-dispatch. Otherwise → unverified receipt.
  ├─ NSIGII\0\0          → the existing NSIGII Scope renderer (7.0.0 / 7.1.0A), unchanged
  └─ anything else       → "inert bytes", metadata + download only
```

Nesting is bounded to 4 hops. A payload is never executed — "extract" releases
bytes to the next dispatch hop, never to a runtime.

The legacy renderer — `renderAscii`, `drawVideoFrame`, `sliceFrames`, the
`DecompressionStream("deflate-raw")` inflate, the cursor gain law, `?src=` — is
untouched. `FORMAT-LEGACY.md` remains authoritative for the `NSIGII\0\0` layout.

## The CORE_V1 codec is not vendored here

`NSIGII01` decoding uses the C codec compiled to WebAssembly. Three files are
expected **next to `nsigii-viewer.html`** and are `.gitignore`d:

| File | Source |
|---|---|
| `nsigii.js` | `make wasm` in `obinexus/nsigii_project` |
| `nsigii.wasm` | `make wasm` in `obinexus/nsigii_project` |
| `nsigii-adapter.mjs` | `obinexus/nsigii_project` → `bindings/web/nsigii-adapter.mjs` |
| `nsigii-constitutional.mjs` | `obinexusmk2/nsigii` → `dist/browser/constitutional.mjs` (`npm run build`) — optional; without it a wrapper is an unverified receipt |

Get them by building that repo (`make wasm`), or from its CI artifact
(`nsigii-core-wasm`). The viewer loads them lazily — only the first time a
`NSIGII01` file is opened — and shows a clear message if they are absent. Opening
an ordinary `7.0.0` / `7.1.0A` stream needs none of this.

## Tests

`npm test` runs Playwright (`test/viewer.spec.mjs`):

- **E** — opens the original `donut.nsigii`, asserts it renders.
- **F** — opens a `NSIGII01`-wrapped `donut.nsigii`, same render via WASM decode.
- **G** — opens a constitutional wrapper ▸ `NSIGII01` ▸ legacy donut; verify +
  extract + decode + render, all three layers.
- a valid single-layer wrapper (verify → extract → render), a **tampered**
  wrapper (receipt only, payload not released), and the inert-bytes path.

CI (`.github/workflows/ci.yml`) checks out `obinexus/nsigii_project` at a pinned
revision, builds the C core + `make wasm`, and runs the suite headless.
