#!/usr/bin/env python3
"""
nsigii_play.py -- terminal player for OBINexus .nsigii containers (codec v7.x)

Streams a .nsigii file, inflates each frame, converts I420 -> RGB and draws it
in the terminal using Unicode half-blocks with 24-bit colour. Each character
cell carries two vertical pixels (foreground = top, background = bottom), so a
24-row terminal shows 48 pixel rows.

    python nsigii_play.py video.nsigii
    python nsigii_play.py video.nsigii --fps 25
    python nsigii_play.py video.nsigii --gray
    python nsigii_play.py video.nsigii --info
    python nsigii_play.py video.nsigii --loop

Keys while playing
    q / Esc / Ctrl-Z / Ctrl-C    quit
    space                        pause / resume

No third-party dependencies. Only the cells actually drawn are sampled from
each frame, so 1080p plays without numpy.

Container format (little-endian), as written by main.go:
    offset 0   8   magic       "NSIGII\0\0"
    offset 8   8   version     "7.0.0\0\0\0"
    offset 16  4   width       uint32
    offset 20  4   height      uint32
    offset 24  4   framecount  uint32   (patched on clean exit; 0 if interrupted)
    offset 28  4   reserved    uint32
    then, repeating:
           0   4   framesize   uint32
           4   N   framedata   raw DEFLATE (RFC 1951) of I420 planes
"""

import argparse
import math
import os
import shutil
import struct
import sys
import time
import zlib

MAGIC = b"NSIGII"
HDR_SIZE = 32
UPPER_HALF = "▀"          # upper half block

ESC_HOME = "\x1b[H"
ESC_CLEAR = "\x1b[2J"
ESC_RESET = "\x1b[0m"
ESC_HIDE = "\x1b[?25l"
ESC_SHOW = "\x1b[?25h"


class NsigiiError(Exception):
    pass


# ---------------------------------------------------------------------------
# container parsing
# ---------------------------------------------------------------------------

def detect_variant(head, path):
    """
    Two different containers share the .nsigii extension and the NSIGII magic:

      byte 7 == 0x00, bytes 8..16 = ASCII version   -> codec video stream (main.go)
      byte 7 == 0x07, 512-byte header, ENDSIGII tail -> constitutional wrapper
                                                        (@obinexusltd/nsigii)

    This player reads the codec video stream. Wrapped containers must be
    unwrapped first.
    """
    if head[7] == 0x07:
        return "wrapped"
    tail = b""
    try:
        with open(path, "rb") as probe:
            probe.seek(max(0, os.path.getsize(path) - 4096))
            tail = probe.read()
    except OSError:
        pass
    if b"ENDSIGII" in tail:
        return "wrapped"
    return "codec"


def read_header(f, path=None):
    head = f.read(HDR_SIZE)
    if len(head) < HDR_SIZE:
        raise NsigiiError("file is shorter than the 32-byte header")
    if head[:6] != MAGIC:
        raise NsigiiError(
            "bad magic %r (expected b'NSIGII') - not an NSIGII container" % head[:6]
        )

    if path is not None and detect_variant(head, path) == "wrapped":
        raise NsigiiError(
            "this is a CONSTITUTIONAL WRAPPER container (@obinexusltd/nsigii), not a\n"
            "       codec video stream. The two formats share the magic and the\n"
            "       extension but are not interchangeable. Unwrap it first:\n\n"
            "           npx @obinexusltd/nsigii inspect  \"%s\"\n"
            "           npx @obinexusltd/nsigii extract  \"%s\"\n\n"
            "       then play the extracted payload with this script."
            % (os.path.basename(path), os.path.basename(path))
        )

    version = head[8:16].rstrip(b"\0").decode("ascii", "replace")
    width, height, declared, reserved = struct.unpack("<IIII", head[16:32])
    if width == 0 or height == 0:
        raise NsigiiError("header reports %dx%d - unusable dimensions" % (width, height))
    return version, width, height, declared, reserved


def payload_kind(version):
    """
    '7.0.0'   -> 'video'  : DEFLATE'd I420 frames, played on a timeline
    '7.1.0A'  -> 'ascii'  : DEFLATE'd char/r/g/b planes on a 2-D rotation grid,
                            navigated with the cursor rather than played
    """
    return "ascii" if version.endswith("A") else "video"


def iter_frames(f):
    """
    Yield (index, raw_size, i420_bytes) for each frame.

    Streams to EOF and does NOT trust the header frame count: main.go patches
    that field with a seek AFTER the encode loop, so an interrupted encode
    leaves it at 0 while the frame data is perfectly readable.
    """
    idx = 0
    while True:
        raw = f.read(4)
        if len(raw) < 4:
            return
        (size,) = struct.unpack("<I", raw)
        if size == 0:
            idx += 1
            continue
        blob = f.read(size)
        if len(blob) < size:
            return                                  # truncated tail, stop cleanly
        try:
            # Go's compress/flate emits RAW deflate with no zlib wrapper,
            # hence wbits=-15. Plain zlib.decompress() fails here.
            data = zlib.decompress(blob, -15)
        except zlib.error as exc:
            raise NsigiiError(
                "frame %d failed to inflate (%s) - stream desync at this point" % (idx, exc)
            )
        yield idx, size, data
        idx += 1


# ---------------------------------------------------------------------------
# colour conversion tables (BT.601 full range, matching main.go's forward matrix)
# ---------------------------------------------------------------------------

_R_V = [int(round(1.402 * (i - 128))) for i in range(256)]
_G_U = [-0.344136 * (i - 128) for i in range(256)]
_G_V = [-0.714136 * (i - 128) for i in range(256)]
_G_UV = [[int(round(gu + gv)) for gv in _G_V] for gu in _G_U]
_B_U = [int(round(1.772 * (i - 128))) for i in range(256)]

# clamp table covering -256..511 -> 0..255
_CLAMP = [0] * 256 + list(range(256)) + [255] * 256


def _nn_map(src, dst):
    """nearest-neighbour index map of length dst into range(src)"""
    if dst <= 0:
        return []
    return [min(src - 1, (i * src) // dst) for i in range(dst)]


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

def fit_to_terminal(width, height, reserve_rows=1):
    cols, rows = shutil.get_terminal_size(fallback=(80, 24))
    avail_rows = max(1, rows - reserve_rows)
    max_px_h = avail_rows * 2

    out_w = cols
    out_h = int(round(cols * height / width))
    if out_h > max_px_h:
        out_h = max_px_h
        out_w = int(round(max_px_h * width / height))
    out_w = max(1, min(out_w, cols))
    out_h = max(2, out_h)
    if out_h % 2:
        out_h += 1
    return out_w, out_h, cols, rows


def render_frame(buf, width, height, xmap, ymap, gray):
    """
    Sample the I420 buffer at the mapped points and return an ANSI string.
    Only len(xmap) * len(ymap) source pixels are touched.
    """
    y_size = width * height
    c_w = width // 2
    c_size = (width // 2) * (height // 2)
    u_off = y_size
    v_off = y_size + c_size

    have_chroma = (not gray) and len(buf) >= v_off + c_size
    have_luma = len(buf) >= y_size
    if not have_luma:
        return None

    out = []
    push = out.append
    clamp = _CLAMP
    rv, guv, bu = _R_V, _G_UV, _B_U

    n_rows = len(ymap) // 2
    for r in range(n_rows):
        y_top = ymap[r * 2]
        y_bot = ymap[r * 2 + 1]
        base_t = y_top * width
        base_b = y_bot * width
        ct_base = (y_top >> 1) * c_w
        cb_base = (y_bot >> 1) * c_w

        last_fg = last_bg = None
        push(ESC_HOME if r == 0 else "")
        for x in xmap:
            yt = buf[base_t + x]
            yb = buf[base_b + x]

            if have_chroma:
                ci_t = ct_base + (x >> 1)
                ci_b = cb_base + (x >> 1)
                ut, vt = buf[u_off + ci_t], buf[v_off + ci_t]
                ub, vb = buf[u_off + ci_b], buf[v_off + ci_b]
                rt = clamp[yt + rv[vt] + 256]
                gt = clamp[yt + guv[ut][vt] + 256]
                bt = clamp[yt + bu[ut] + 256]
                rb = clamp[yb + rv[vb] + 256]
                gb = clamp[yb + guv[ub][vb] + 256]
                bb = clamp[yb + bu[ub] + 256]
            else:
                rt = gt = bt = yt
                rb = gb = bb = yb

            fg = (rt, gt, bt)
            bg = (rb, gb, bb)
            if fg != last_fg:
                push("\x1b[38;2;%d;%d;%dm" % fg)
                last_fg = fg
            if bg != last_bg:
                push("\x1b[48;2;%d;%d;%dm" % bg)
                last_bg = bg
            push(UPPER_HALF)
        push(ESC_RESET + "\n")

    return "".join(out)


# ---------------------------------------------------------------------------
# terminal / input plumbing
# ---------------------------------------------------------------------------

def enable_vt():
    """Turn on ANSI escape processing on Windows consoles."""
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)          # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


class KeyReader:
    """Non-blocking single-key reader for Windows and POSIX."""

    QUIT = {b"q", b"Q", b"\x1b", b"\x1a", b"\x03"}   # q, Esc, Ctrl-Z, Ctrl-C
    PAUSE = {b" "}

    def __init__(self):
        self.win = os.name == "nt"
        self._saved = None
        self._fd = None

    def __enter__(self):
        if not self.win:
            try:
                import termios, tty
                self._fd = sys.stdin.fileno()
                self._saved = termios.tcgetattr(self._fd)
                tty.setcbreak(self._fd)
            except Exception:
                self._saved = None
        return self

    def __exit__(self, *exc):
        if not self.win and self._saved is not None:
            try:
                import termios
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved)
            except Exception:
                pass

    def poll(self):
        try:
            if self.win:
                import msvcrt
                if msvcrt.kbhit():
                    return msvcrt.getch()
                return None
            import select
            if select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.buffer.read(1)
        except Exception:
            pass
        return None


# ---------------------------------------------------------------------------
# info / diagnostic mode
# ---------------------------------------------------------------------------

def do_info(path, sample_frames):
    with open(path, "rb") as f:
        version, width, height, declared, reserved = read_header(f, path)
        file_size = os.path.getsize(path)

        print("file          %s" % os.path.basename(path))
        print("size          %s bytes" % format(file_size, ","))
        print("magic         NSIGII")
        print("version       %s" % version)
        kind = payload_kind(version)
        print("kind          %s" % ("interactive coloured ASCII" if kind == "ascii"
                                    else "I420 video timeline"))
        print("dimensions    %dx%d %s" % (width, height,
              "cells" if kind == "ascii" else "pixels"))
        print("declared      %s frames (header offset 24)" % format(declared, ","))
        if kind == "ascii":
            ga, gb = (reserved >> 16) & 0xFFFF, reserved & 0xFFFF
            print("rotation grid %dx%d  (%.1f deg per step in A, %.1f in B)"
                  % (ga, gb, 360.0/max(1,ga), 360.0/max(1,gb)))
            print("interaction   gain %.1f..%.1f scaled by cursor speed "
                  "(ref %.0f cells/s)" % (GAIN_MIN, GAIN_MAX, SPEED_REF))
        print("reserved      0x%08x" % reserved)
        if kind == "ascii":
            print("frame payload %s bytes  (char|r|g|b planes, %d cells each)"
                  % (format(width * height * 4, ","), width * height))
        else:
            print("expected I420 %s bytes/frame" % format(width * height * 3 // 2, ","))
        print()

        y_size = width * height
        count = 0
        total_raw = 0
        smallest = None
        largest = 0
        zero_fracs = []
        split_rows = []
        bad_size = 0

        try:
            for idx, size, buf in iter_frames(f):
                count += 1
                total_raw += size
                largest = max(largest, size)
                smallest = size if smallest is None else min(smallest, size)
                expect = width * height * 4 if kind == "ascii" else width * height * 3 // 2
                if len(buf) != expect:
                    bad_size += 1

                if kind != "ascii" and len(zero_fracs) < sample_frames and len(buf) >= y_size:
                    # sample 64 columns per row to estimate the zero fraction
                    step = max(1, width // 64)
                    zeros = 0
                    total = 0
                    first_dead = None
                    for row in range(height):
                        base = row * width
                        row_nonzero = 0
                        for col in range(0, width, step):
                            total += 1
                            if buf[base + col] == 0:
                                zeros += 1
                            else:
                                row_nonzero += 1
                        if row_nonzero == 0 and first_dead is None:
                            first_dead = row
                        elif row_nonzero:
                            first_dead = None
                    if total:
                        zero_fracs.append(zeros / total)
                    if first_dead is not None:
                        split_rows.append(first_dead)
        except NsigiiError as exc:
            print("!! %s" % exc)
            print()

        print("frames read   %s" % format(count, ","))
        if declared and declared != count:
            print("              MISMATCH: header says %s. A count of 0 means the" % format(declared, ","))
            print("              encoder was interrupted before it patched the header.")
        if bad_size:
            print("odd-sized     %d frames did not inflate to the expected length" % bad_size)
        if count:
            print("frame bytes   min %s / mean %s / max %s (compressed)" % (
                format(smallest, ","),
                format(total_raw // count, ","),
                format(largest, ","),
            ))
            raw_total = count * (width * height * 4 if kind == "ascii"
                                 else width * height * 3 // 2)
            print("ratio         %s -> %s  (%.2f%% of raw)" % (
                format(raw_total, ","), format(total_raw, ","),
                100.0 * total_raw / raw_total if raw_total else 0.0,
            ))
        print()

        if zero_fracs:
            mean_zero = sum(zero_fracs) / len(zero_fracs)
            print("Y-plane diagnostic (first %d frames)" % len(zero_fracs))
            print("  zero luma     %.1f%% of sampled pixels" % (100.0 * mean_zero))
            if split_rows:
                mean_split = sum(split_rows) / len(split_rows)
                print("  goes black at row %d of %d  (%.0f%% down the frame)" % (
                    mean_split, height, 100.0 * mean_split / height))
            if mean_zero > 0.35:
                print()
                print("  A large all-zero region is the signature of the rgbToYUV420")
                print("  buffer-length bug: the function receives the ROPEN-halved")
                print("  payload but indexes it as full-length RGB24, so every pixel")
                print("  past the halfway point is skipped and left at zero.")
        return 0


# ---------------------------------------------------------------------------
# playback
# ---------------------------------------------------------------------------

def do_play(path, fps, gray, loop, max_frames, start_frame):
    enable_vt()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    with open(path, "rb") as probe:
        version, width, height, declared, _ = read_header(probe, path)

    out_w, out_h, cols, rows = fit_to_terminal(width, height)
    xmap = _nn_map(width, out_w)
    ymap = _nn_map(height, out_h)
    interval = 1.0 / fps if fps > 0 else 0.0

    status = "%dx%d v%s -> %dx%d cells  %g fps   [q/Esc/Ctrl-Z quit, space pause]" % (
        width, height, version, out_w, out_h // 2, fps)

    shown = 0
    dropped = 0
    decoded = 0
    quit_now = False

    sys.stdout.write(ESC_HIDE + ESC_CLEAR)
    sys.stdout.flush()

    try:
        with KeyReader() as keys:
            while not quit_now:
                with open(path, "rb") as f:
                    f.seek(HDR_SIZE)
                    clock = time.perf_counter()
                    try:
                        for idx, _size, buf in iter_frames(f):
                            decoded += 1
                            if idx < start_frame:
                                continue

                            key = keys.poll()
                            if key in KeyReader.QUIT:
                                quit_now = True
                                break
                            if key in KeyReader.PAUSE:
                                while True:
                                    k2 = keys.poll()
                                    if k2 in KeyReader.QUIT:
                                        quit_now = True
                                        break
                                    if k2 in KeyReader.PAUSE:
                                        break
                                    time.sleep(0.03)
                                clock = time.perf_counter() - (idx - start_frame) * interval
                                if quit_now:
                                    break

                            elapsed = time.perf_counter() - clock
                            target = (idx - start_frame) * interval
                            if elapsed < target:
                                time.sleep(target - elapsed)
                            elif interval and elapsed > target + interval:
                                dropped += 1
                                continue          # behind: decode but don't draw

                            painted = render_frame(buf, width, height, xmap, ymap, gray)
                            if painted is None:
                                dropped += 1
                                continue
                            shown += 1
                            sys.stdout.write(painted)
                            sys.stdout.write(
                                "\x1b[%d;1H\x1b[2K frame %d  shown %d  dropped %d   %s" % (
                                    rows, idx, shown, dropped, status)
                            )
                            sys.stdout.flush()

                            if max_frames and shown >= max_frames:
                                quit_now = True
                                break
                    except NsigiiError as exc:
                        sys.stdout.write(ESC_RESET + "\n")
                        sys.stdout.flush()
                        print("stream stopped: %s" % exc, file=sys.stderr)
                        quit_now = True

                if not loop:
                    break
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(ESC_RESET + ESC_SHOW + "\n")
        sys.stdout.flush()

    print("played %d frames (%d decoded, %d dropped to keep pace)" % (shown, decoded, dropped))
    return 0



# ---------------------------------------------------------------------------
# interactive ASCII kind ("7.1.0A"): a 2-D rotation grid driven by the cursor
# ---------------------------------------------------------------------------

# Interaction contract. The gain applied to cursor motion scales with how fast
# the cursor is moving, between these bounds - a slow drag nudges, a fast flick
# spins. GAIN_MIN/GAIN_MAX are the 2.5..5.0 range.
GAIN_MIN = 2.5
GAIN_MAX = 5.0
SPEED_REF = 60.0          # cells/sec at which the gain reaches GAIN_MAX
RAD_PER_CELL = 0.0314     # ~ one full turn per 80-cell drag at GAIN_MIN
IDLE_SPIN = 0.9           # rad/sec when the cursor is not moving

MOUSE_ON = "\x1b[?1003h\x1b[?1006h"     # any-motion tracking + SGR coordinates
MOUSE_OFF = "\x1b[?1006l\x1b[?1003l"


def enable_vt_input():
    """
    Windows consoles need VT input mode for mouse escape sequences to arrive,
    and QuickEdit must be off or the console eats the mouse for text selection.
    Returns the previous mode so it can be restored.
    """
    if os.name != "nt":
        return None
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-10)              # STD_INPUT_HANDLE
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return None
        ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
        ENABLE_EXTENDED_FLAGS = 0x0080
        ENABLE_QUICK_EDIT_MODE = 0x0040
        ENABLE_MOUSE_INPUT = 0x0010
        new = (mode.value | ENABLE_VIRTUAL_TERMINAL_INPUT
                          | ENABLE_EXTENDED_FLAGS
                          | ENABLE_MOUSE_INPUT) & ~ENABLE_QUICK_EDIT_MODE
        kernel32.SetConsoleMode(handle, new)
        return mode.value
    except Exception:
        return None


def restore_vt_input(saved):
    if os.name != "nt" or saved is None:
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), saved)
    except Exception:
        pass


class InputStream:
    """
    Byte-level reader that pulls out SGR mouse reports and plain keys.

    SGR mouse report:  ESC [ < Cb ; Cx ; Cy (M|m)
      Cb 35 = motion, no button held
      Cb 32 = motion with button 1 held (a drag)
    """

    def __init__(self):
        self.win = os.name == "nt"
        self.buf = bytearray()
        self._saved_termios = None
        self._fd = None
        self._saved_conmode = None

    def __enter__(self):
        self._saved_conmode = enable_vt_input()
        if not self.win:
            try:
                import termios, tty
                self._fd = sys.stdin.fileno()
                self._saved_termios = termios.tcgetattr(self._fd)
                tty.setcbreak(self._fd)
            except Exception:
                self._saved_termios = None
        return self

    def __exit__(self, *exc):
        if not self.win and self._saved_termios is not None:
            try:
                import termios
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved_termios)
            except Exception:
                pass
        restore_vt_input(self._saved_conmode)

    def _pump(self):
        try:
            if self.win:
                import msvcrt
                while msvcrt.kbhit():
                    self.buf += msvcrt.getch()
            else:
                import select
                while select.select([sys.stdin], [], [], 0)[0]:
                    chunk = sys.stdin.buffer.read(1)
                    if not chunk:
                        break
                    self.buf += chunk
        except Exception:
            pass

    def events(self):
        """Yield ('key', b'x') and ('mouse', (button, col, row, pressed))."""
        self._pump()
        out = []
        while self.buf:
            if self.buf[:3] == b"\x1b[<":
                end = -1
                for i in range(3, len(self.buf)):
                    if self.buf[i] in (0x4D, 0x6D):      # 'M' or 'm'
                        end = i
                        break
                if end < 0:
                    if len(self.buf) > 32:
                        del self.buf[0]                  # malformed, drop a byte
                        continue
                    break                                # partial, wait for more
                body = bytes(self.buf[3:end]).decode("ascii", "replace")
                pressed = self.buf[end] == 0x4D
                del self.buf[:end + 1]
                try:
                    cb, cx, cy = (int(v) for v in body.split(";"))
                    out.append(("mouse", (cb, cx, cy, pressed)))
                except ValueError:
                    pass
                continue
            if self.buf[:1] == b"\x1b" and len(self.buf) < 3 and not self.win:
                break                                    # maybe a partial escape
            out.append(("key", bytes(self.buf[:1])))
            del self.buf[:1]
        return out


def load_ascii_grid(path):
    """Read every frame of an ASCII-kind container into memory, keyed by index."""
    with open(path, "rb") as f:
        version, w, h, declared, reserved = read_header(f, path)
        if payload_kind(version) != "ascii":
            raise NsigiiError("not an interactive ASCII container (version %r)" % version)
        grid_a = (reserved >> 16) & 0xFFFF
        grid_b = reserved & 0xFFFF
        if grid_a == 0 or grid_b == 0:
            raise NsigiiError("header declares a %dx%d rotation grid" % (grid_a, grid_b))
        cells = []
        for _idx, _size, data in iter_frames(f):
            cells.append(data)
    if len(cells) < grid_a * grid_b:
        raise NsigiiError("expected %d frames for a %dx%d grid, found %d"
                          % (grid_a * grid_b, grid_a, grid_b, len(cells)))
    return version, w, h, grid_a, grid_b, cells


def render_ascii(planes, w, h):
    """char/r/g/b planes -> one ANSI screen, emitting colour codes only on change."""
    size = w * h
    if len(planes) < size * 4:
        return None
    cp, rp, gp, bp = 0, size, size * 2, size * 3
    out = [ESC_HOME]
    push = out.append
    last = None
    for row in range(h):
        base = row * w
        for col in range(w):
            o = base + col
            ch = planes[cp + o]
            if ch == 32:                     # background: no colour needed
                if last is not None:
                    push(ESC_RESET)
                    last = None
                push(" ")
                continue
            fg = (planes[rp + o], planes[gp + o], planes[bp + o])
            if fg != last:
                push("\x1b[38;2;%d;%d;%dm" % fg)
                last = fg
            push(chr(ch))
        push(ESC_RESET + "\n")
        last = None
    return "".join(out)


def do_play_ascii(path, spin):
    enable_vt()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    version, w, h, grid_a, grid_b, cells = load_ascii_grid(path)

    A = B = 0.0
    last_pos = None
    last_t = time.perf_counter()
    last_idx = -1
    gain_now = GAIN_MIN
    speed_now = 0.0
    quit_now = False
    autospin = spin

    sys.stdout.write(ESC_HIDE + ESC_CLEAR + MOUSE_ON)
    sys.stdout.flush()

    try:
        with InputStream() as stream:
            while not quit_now:
                now = time.perf_counter()
                dt_frame = now - last_t
                last_t = now
                moved = False

                for kind, payload in stream.events():
                    if kind == "key":
                        if payload in (b"q", b"Q", b"\x1b", b"\x1a", b"\x03"):
                            quit_now = True
                        elif payload == b" ":
                            autospin = not autospin
                        elif payload in (b"r", b"R"):
                            A = B = 0.0
                        continue

                    cb, cx, cy, _pressed = payload
                    if last_pos is not None:
                        dx = cx - last_pos[0]
                        dy = cy - last_pos[1]
                        if dx or dy:
                            dt = max(dt_frame, 1e-3)
                            speed_now = math.hypot(dx, dy) / dt
                            frac = speed_now / SPEED_REF
                            frac = 0.0 if frac < 0 else (1.0 if frac > 1 else frac)
                            gain_now = GAIN_MIN + (GAIN_MAX - GAIN_MIN) * frac
                            B += dx * gain_now * RAD_PER_CELL
                            A += dy * gain_now * RAD_PER_CELL
                            moved = True
                    last_pos = (cx, cy)

                if autospin and not moved:
                    B += IDLE_SPIN * dt_frame
                    A += IDLE_SPIN * 0.37 * dt_frame

                tau = 2.0 * math.pi
                ai = int((A % tau) / tau * grid_a) % grid_a
                bi = int((B % tau) / tau * grid_b) % grid_b
                idx = ai * grid_b + bi

                if idx != last_idx:
                    last_idx = idx
                    painted = render_ascii(cells[idx], w, h)
                    if painted:
                        sys.stdout.write(painted)
                        sys.stdout.write(
                            "\x1b[2K A %5.1f  B %5.1f   cell %2d,%2d/%dx%d   "
                            "gain %.2f  %4.0f cells/s   [drag to spin, "
                            "space idle-spin, r reset, q quit]"
                            % (math.degrees(A % tau), math.degrees(B % tau),
                               ai, bi, grid_a, grid_b, gain_now, speed_now)
                        )
                        sys.stdout.flush()

                time.sleep(0.008)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(MOUSE_OFF + ESC_RESET + ESC_SHOW + "\n")
        sys.stdout.flush()
    return 0


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Play an OBINexus .nsigii container in the terminal.")
    ap.add_argument("file", help="path to the .nsigii file")
    ap.add_argument("--fps", type=float, default=30.0,
                    help="playback rate (default 30; the container stores no fps)")
    ap.add_argument("--gray", action="store_true",
                    help="luma only - skips chroma, faster and shows the Y plane raw")
    ap.add_argument("--loop", action="store_true", help="repeat when the stream ends")
    ap.add_argument("--info", action="store_true",
                    help="print header, frame stats and Y-plane diagnostic, then exit")
    ap.add_argument("--sample", type=int, default=3, metavar="N",
                    help="frames to analyse in --info mode (default 3)")
    ap.add_argument("--max-frames", type=int, default=0, metavar="N",
                    help="stop after N drawn frames")
    ap.add_argument("--start", type=int, default=0, metavar="N",
                    help="skip the first N frames")
    ap.add_argument("--no-spin", action="store_true",
                    help="interactive kind: no idle rotation, cursor only")
    args = ap.parse_args()

    if not os.path.isfile(args.file):
        print("no such file: %s" % args.file, file=sys.stderr)
        return 2

    try:
        with open(args.file, "rb") as probe:
            version, _w, _h, _n, _r = read_header(probe, args.file)
        kind = payload_kind(version)

        if args.info:
            return do_info(args.file, max(1, args.sample))
        if kind == "ascii":
            return do_play_ascii(args.file, spin=not args.no_spin)
        return do_play(args.file, args.fps, args.gray, args.loop,
                       max(0, args.max_frames), max(0, args.start))
    except NsigiiError as exc:
        print("nsigii: %s" % exc, file=sys.stderr)
        return 1
    except BrokenPipeError:
        # piped into head/less and the reader went away - exit quietly
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
        except Exception:
            pass
        return 0


if __name__ == "__main__":
    sys.exit(main())
