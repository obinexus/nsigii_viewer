# Legacy NSIGII codec stream — `7.0.0` / `7.1.0A`

**Status:** authoritative for the `LEGACY_CODEC_STREAM` layout. Owned by
`obinexus/nsigii_viewer`. This is the format that `nsigii-viewer.html`,
`nsigii_play.py`, `donut_nsigii.py`, and the Go encoder in `main.go` read and
write. It is frozen for backward compatibility — every existing `.nsigii` file of
this kind keeps opening unchanged.

This document describes **one** of three unrelated binary layouts that share the
`NSIGII` prefix. It is not the generic byte container and not the constitutional
wrapper.

---

## 1. Place in the NSIGII ecosystem

| Layer | Magic (bytes 0–7) | Repository | Role |
|---|---|---|---|
| `CORE_V1` generic byte container | `NSIGII01` | `obinexus/nsigii_project` | transport — frames arbitrary bytes, CRC-32 |
| Constitutional wrapper | `NSIGII\0` + `0x07` at byte 7 | `obinexusmk2/nsigii` | verification — SHA-256 + trident |
| **Legacy codec stream** — this document | `NSIGII\0\0` | `obinexus/nsigii_viewer` | interpretation — media + interaction state |

The cross-layer detection rule is in
[`obinexusmk2/nsigii` → `docs/DISPATCH.md`](https://github.com/obinexusmk2/nsigii/blob/main/docs/DISPATCH.md).
A legacy stream is **never** a nested NSIGII artifact: its frames are
DEFLATE-compressed media planes, not another container.

---

## 2. Shared 32-byte header

Both kinds begin with the same header. All integers are unsigned little-endian.

| Offset | Size | Field | Notes |
|---:|---:|---|---|
| 0 | 8 | `magic` | ASCII `NSIGII\0\0` — bytes 6 and 7 are both `0x00` |
| 8 | 8 | `version` | NUL-padded ASCII: `7.0.0\0\0\0` or `7.1.0A\0\0` |
| 16 | 4 | `width` | pixels (`7.0.0`) or terminal columns (`7.1.0A`) |
| 20 | 4 | `height` | pixels (`7.0.0`) or terminal rows (`7.1.0A`) |
| 24 | 4 | `framecount` | patched by a seek after the encode loop; see [§5](#5-framecount-is-advisory) |
| 28 | 4 | `reserved` | `0` for `7.0.0`; `(grid_a << 16) \| grid_b` for `7.1.0A` |

Go reference (`main.go`):

```go
header := struct {
    Magic      [8]byte   // {'N','S','I','G','I','I',0,0}
    Version    [8]byte   // {'7','.','0','.','0',0,0,0}
    Width      uint32
    Height     uint32
    FrameCount uint32
    Reserved   uint32
}{ ... }
binary.Write(output, binary.LittleEndian, header)
// ... after the encode loop:
output.Seek(24, 0)
binary.Write(output, binary.LittleEndian, uint32(frameCount))
```

The **trailing `A`** on the version string is the only structural signal that
distinguishes the interactive kind. A `7.0.0` reader that does not know `7.1.0A`
sees an unrecognised version and stops cleanly; a `7.1.0A`-aware reader branches
on it.

---

## 3. Frame table

Immediately after the header, frames repeat to end of file:

```
repeat:
    u32  framesize          little-endian
    u8[framesize] framedata  raw DEFLATE
```

- **Raw DEFLATE** — RFC 1951 with no zlib wrapper and no checksum. Decode with
  `wbits = -15`. Go's `compress/flate` writes this; `zlib.decompress(blob)` (the
  default, `wbits = 15`) fails with *"incorrect header check"* — you must pass
  `zlib.decompress(blob, -15)`. The browser equivalent is
  `new DecompressionStream("deflate-raw")`.
- A `framesize` of `0` is **skipped**, not a terminator. There is no explicit
  terminator — read until EOF.
- A final `framesize` that runs past EOF marks a truncated tail; stop there.
- There is no frame index and no per-frame offset table. Random access requires
  walking the file. HTTP range requests are therefore not possible.

---

## 4. The two kinds

### 4.1 `7.0.0` — I420 video timeline

Each inflated frame is one **I420** (YUV 4:2:0 planar) picture of
`width * height * 3 / 2` bytes:

| Plane | Size |
|---|---|
| Y (luma) | `width * height` |
| U (chroma) | `(width/2) * (height/2)` |
| V (chroma) | `(width/2) * (height/2)` |

Frames play on a timeline at a viewer-chosen frame rate. The compression is not
competitive with a real video codec — the container was the point, not the
codec.

### 4.2 `7.1.0A` — coloured-ASCII rotation state space

Frames are not a timeline. They form a 2-D grid over two rotation angles of the
rendered object (`A` = pitch, driven by vertical cursor motion; `B` = yaw,
driven by horizontal cursor motion). The file carries the **entire interaction
state space**; the player is a lookup driver and computes nothing at play time.

- **Grid dimensions:** `grid_a = (reserved >> 16) & 0xFFFF`,
  `grid_b = reserved & 0xFFFF`. Each is `1..65535`. `framecount == grid_a * grid_b`.
- **Frame index:** `frame = a_index * grid_b + b_index`, with `a_index` the outer
  loop. A player maps cursor state to
  `a_index = floor((A mod 2π) / 2π * grid_a) mod grid_a` and likewise for
  `b_index`.
- **Frame payload:** four **planar** byte planes, each `width * height` bytes,
  concatenated in this order:

  | Plane | Meaning |
  |---|---|
  | `chars` | one ASCII byte per cell; `0x20` (space) = background / empty |
  | `red` | 0–255 |
  | `green` | 0–255 |
  | `blue` | 0–255 |

  Planar (not interleaved) because the char plane is mostly spaces and each
  colour plane is locally smooth, so DEFLATE reaches roughly 30 % of raw versus
  about 60 % interleaved.

- A renderer draws cell `o = row * width + col` as character `chars[o]`; if
  `chars[o] != 0x20`, in colour `rgb(red[o], green[o], blue[o])`.
- The reference bake (`donut_nsigii.py`) uses the luminance ramp
  `.,-~:;=!*#$@` (dark → bright), but a reader must treat `chars` as arbitrary
  printable bytes, not this specific ramp.

---

## 5. `framecount` is advisory

`framecount` at offset 24 is written as a placeholder and patched by a seek
**after** the encode loop. If the encoder was interrupted (or streamed to a
non-seekable sink), it stays `0` or short. A `7.1.0A` bake that knows its count
up front writes it directly, but readers must not depend on that.

**Rule for every reader:** stream frames to EOF and count them. Use `framecount`
only as a sanity cross-check, and surface a mismatch as information, not an
error — the frames themselves are still valid.

---

## 6. Telling this apart from the constitutional wrapper

The wrapper (`obinexusmk2/nsigii`) also starts `NSIGII`. Distinguish before
parsing:

| Check | Legacy codec stream | Constitutional wrapper |
|---|---|---|
| byte 6 | `0x00` | `0x00` |
| byte 7 | `0x00` | `0x07` (`version_major`) |
| tail marker | none | `ENDNSIGII` (current) or `ENDSIGII` (pre-0.1) |

A legacy reader that encounters `byte[7] == 0x07`, an `ENDNSIGII` / `ENDSIGII`
tail, or the 8-byte literal `NSIGII01` must **refuse** the file and point the
operator at the right tool — it must not try to interpret any of them as frames.

> Note: `nsigii-viewer.html` recognises all three layouts — it renders this
> codec stream, decodes `NSIGII01` through the C/WASM adapter and re-dispatches
> the result, and shows a receipt for the constitutional wrapper (`ENDNSIGII` or
> legacy `ENDSIGII` tail). See `INTEGRATION.md`. `nsigii_play.py` still scans
> only for `ENDSIGII`; none of this changes the codec-stream format itself.

---

## 7. Reference reader (complete, `7.0.0` and `7.1.0A`)

```python
import struct, zlib

def read_nsigii_legacy(path):
    with open(path, "rb") as f:
        head = f.read(32)
        if head[:6] != b"NSIGII":
            raise ValueError("not an NSIGII container")
        if head[7] == 0x07 or head[:8] == b"NSIGII01":
            raise ValueError("not a legacy codec stream (wrapper or CORE_V1)")
        version = head[8:16].rstrip(b"\0").decode()
        width, height, declared, reserved = struct.unpack("<IIII", head[16:32])
        frames = []
        while True:
            sz = f.read(4)
            if len(sz) < 4:
                break                       # EOF
            (size,) = struct.unpack("<I", sz)
            if size == 0:
                continue                    # skipped, not a terminator
            blob = f.read(size)
            if len(blob) < size:
                break                       # truncated tail
            frames.append(zlib.decompress(blob, -15))   # raw DEFLATE, wbits=-15
        return version, width, height, reserved, frames
```

For `7.1.0A`, split each frame into four `width*height` slices
(`chars`, `red`, `green`, `blue`) and index with
`a_index * (reserved & 0xFFFF) + b_index`.

---

## 8. Compatibility guarantees

- The 32-byte header and the `u32 size` + raw-DEFLATE frame table are stable and
  will not change.
- New capability is added only by riding unused space — a new version suffix, or
  fields packed into `reserved` — so that old readers stop cleanly on an
  unrecognised version and new readers branch. `7.1.0A` was added this way with
  no format change.
- Existing fixtures (`donut.nsigii`), the drag-to-rotate interaction, the
  state-grid lookup, and raw-DEFLATE decoding continue to work as-is.

---

## 9. Known limitations

- No frame index → no seeking without walking the file → no HTTP range requests.
- `7.0.0` compression is well short of a modern video codec.
- The stream carries no hash and no signature — no proof of origin or integrity.
  Wrap it in a constitutional container (`obinexusmk2/nsigii`) if you need that.
