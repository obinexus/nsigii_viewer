#!/usr/bin/env python3
"""
donut_nsigii.py -- bake the rotating ASCII donut into an interactive .nsigii

The existing .nsigii container is a linear video: frame 0, 1, 2 ... played in
order. This writes a *navigable* one. Instead of a timeline, the frames form a
2-D grid over the torus's two rotation angles:

        A  (pitch, X axis)  <- vertical cursor movement
        B  (yaw,   Z axis)  <- horizontal cursor movement

The file therefore carries the complete interaction state space. The player is a
thin driver: it turns cursor motion into an (A, B) coordinate and looks up the
matching cell. Nothing is computed at play time, so the artifact stays pure data
and stays readable from Python, Lua, or anything else that can inflate DEFLATE.

CONTAINER (same 32-byte header as the video kind)
    0   8   magic       "NSIGII\0\0"
    8   8   version     "7.1.0A\0\0"   <- trailing 'A' = coloured-ASCII kind
    16  4   width       uint32   terminal columns
    20  4   height      uint32   terminal rows
    24  4   framecount  uint32   grid_a * grid_b
    28  4   reserved    uint32   (grid_a << 16) | grid_b
    then, per frame:
    0   4   framesize   uint32
    4   N   framedata   raw DEFLATE of four planar W*H byte planes:
                            chars | red | green | blue

    Frame index = a_index * grid_b + b_index.

Planar rather than interleaved because the char plane is mostly spaces and each
colour plane is locally smooth, so DEFLATE does far better on it.

    python donut_nsigii.py                      # 80x24, 24x24 grid
    python donut_nsigii.py --cols 100 --rows 30 --grid 32
"""

import argparse
import math
import struct
import sys
import time
import zlib

LUMA_CHARS = ".,-~:;=!*#$@"          # 12 steps, dark -> bright
THETA_STEP = 0.07                    # around the tube cross-section
PHI_STEP = 0.02                      # around the ring
R1, R2, K2 = 1.0, 2.0, 5.0


def hsv_to_rgb(h, s, v):
    """h in degrees, s/v in 0..1 -> (r,g,b) 0..255"""
    h = h % 360.0
    c = v * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = v - c
    if h < 60:    r, g, b = c, x, 0
    elif h < 120: r, g, b = x, c, 0
    elif h < 180: r, g, b = 0, c, x
    elif h < 240: r, g, b = 0, x, c
    elif h < 300: r, g, b = x, 0, c
    else:         r, g, b = c, 0, x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def build_palette(hue_steps=180):
    """
    Colour is a function of (phi, luminance):
      hue   <- phi, the material coordinate around the ring, so the colour is
               painted onto the torus and sweeps as it turns
      value <- luminance index, so shading still reads as shape
    Precomputed because it is looked up once per plotted point.
    """
    pal = []
    for hi in range(hue_steps):
        hue = hi * 360.0 / hue_steps
        row = []
        for li in range(12):
            v = 0.30 + 0.70 * (li / 11.0)
            row.append(hsv_to_rgb(hue, 0.85, v))
        pal.append(row)
    return pal


def render_cell(A, B, w, h, pal, hue_steps):
    """One (A,B) orientation -> (chars, r, g, b) planes of w*h bytes."""
    size = w * h
    chars = bytearray(b" " * size)
    rp = bytearray(size)
    gp = bytearray(size)
    bp = bytearray(size)
    zbuf = [0.0] * size

    cosA, sinA = math.cos(A), math.sin(A)
    cosB, sinB = math.cos(B), math.sin(B)

    # K1 chosen so the torus fills the width; y gets half the scale because a
    # terminal cell is about twice as tall as it is wide.
    k1x = w * K2 * 3.0 / (8.0 * (R1 + R2))
    k1y = k1x * 0.5
    cx, cy = w / 2.0, h / 2.0

    theta = 0.0
    while theta < 6.283185:
        costheta, sintheta = math.cos(theta), math.sin(theta)
        circlex = R2 + R1 * costheta
        circley = R1 * sintheta
        phi = 0.0
        while phi < 6.283185:
            cosphi, sinphi = math.cos(phi), math.sin(phi)

            x = circlex * (cosB * cosphi + sinA * sinB * sinphi) - circley * cosA * sinB
            y = circlex * (sinB * cosphi - sinA * cosB * sinphi) + circley * cosA * cosB
            z = K2 + cosA * circlex * sinphi + circley * sinA
            ooz = 1.0 / z

            xp = int(cx + k1x * ooz * x)
            yp = int(cy - k1y * ooz * y)

            lum = (cosphi * costheta * sinB
                   - cosA * costheta * sinphi
                   - sinA * sintheta
                   + cosB * (cosA * sintheta - costheta * sinA * sinphi))

            if lum > 0 and 0 <= xp < w and 0 <= yp < h:
                o = yp * w + xp
                if ooz > zbuf[o]:
                    zbuf[o] = ooz
                    li = int(lum * 8)
                    if li > 11:
                        li = 11
                    chars[o] = ord(LUMA_CHARS[li])
                    hi = int(phi * hue_steps / 6.283185) % hue_steps
                    r, g, b = pal[hi][li]
                    rp[o], gp[o], bp[o] = r, g, b
            phi += PHI_STEP
        theta += THETA_STEP

    return bytes(chars) + bytes(rp) + bytes(gp) + bytes(bp)


def main():
    ap = argparse.ArgumentParser(description="Bake an interactive donut .nsigii")
    ap.add_argument("--out", default="donut.nsigii")
    ap.add_argument("--cols", type=int, default=80, help="terminal columns")
    ap.add_argument("--rows", type=int, default=24, help="terminal rows")
    ap.add_argument("--grid", type=int, default=24,
                    help="rotation steps per axis (grid x grid frames)")
    ap.add_argument("--hue-steps", type=int, default=180)
    args = ap.parse_args()

    w, h = args.cols, args.rows
    ga = gb = args.grid
    if not (1 <= ga <= 0xFFFF):
        print("grid must be 1..65535", file=sys.stderr)
        return 2

    pal = build_palette(args.hue_steps)
    total = ga * gb
    print("baking %d frames (%dx%d rotation grid) at %dx%d cells"
          % (total, ga, gb, w, h))

    t0 = time.perf_counter()
    payloads = []
    raw_total = 0
    for ai in range(ga):
        A = ai * 2.0 * math.pi / ga
        for bi in range(gb):
            B = bi * 2.0 * math.pi / gb
            planes = render_cell(A, B, w, h, pal, args.hue_steps)
            raw_total += len(planes)
            co = zlib.compressobj(9, zlib.DEFLATED, -15)   # raw DEFLATE, like Go
            payloads.append(co.compress(planes) + co.flush())
        done = (ai + 1) * gb
        print("  %4d/%d  %.1fs" % (done, total, time.perf_counter() - t0),
              end="\r", flush=True)
    print()

    with open(args.out, "wb") as f:
        f.write(struct.pack("<8s8sIIII",
                            b"NSIGII\0\0", b"7.1.0A\0\0",
                            w, h, total, (ga << 16) | gb))
        for blob in payloads:
            f.write(struct.pack("<I", len(blob)))
            f.write(blob)

    enc_total = sum(len(p) + 4 for p in payloads)
    print("wrote %s" % args.out)
    print("  frames      %d  (%dx%d grid, %.1f deg per step)"
          % (total, ga, gb, 360.0 / ga))
    print("  raw planes  %s bytes" % format(raw_total, ","))
    print("  encoded     %s bytes  (%.2f%% of raw)"
          % (format(enc_total, ","), 100.0 * enc_total / raw_total))
    print("  elapsed     %.1fs" % (time.perf_counter() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
