# NSIGII Protocol Specification

**Trident Packet Verification via Bipolar CISCO Order/Chaos Separation of Concerns**

| Field | Value |
|---|---|
| Document ID | OBINEXUS-NSIGII-SPEC |
| Version | 0.3 — Draft |
| Status | Working draft, derived from primary transcript corpus |
| Revision | v0.2 — §7.1 addressing triad completed and named.<br>v0.3 — Three Nevers bound one-per-addressing-mode; "never fails" renamed to its canonical "never a problem"; §11.3 tension resolved (author ratification, 25 Aug 2026) |
| Author of record | Nnamdi Michael Okpala, OBINexus Computing |
| Editor | Distilled from `NSIGII.txt` (6 recorded sessions, Jan–Jun 2026) |
| Compiled | 25 August 2026 |
| Companion | `nsigii-spec.tex` (LaTeX source, same content) |

---

## 0. Document Status and Provenance

### 0.1 What this document is

This is a **derived specification**. It is not a transcript and not an
independent design. Every normative statement below traces to a claim made in
the NSIGII recording corpus. Where the corpus is internally inconsistent, this
document states the inconsistency rather than silently choosing a side.

### 0.2 Source corpus

`NSIGII.txt` contains six recorded working sessions, transcribed by
speech-to-text. Segment numbering used throughout this document:

| Seg | Date given in recording | Working title |
|---|---|---|
| S1 | 30 January 2026, 05:39 | Trident packet verification via bipolar CISCO — order/chaos separation of concerns |
| S2 | 13 January 2026, 10:15 | Filter/flash interdependency — CISCO sequence and series instruction execution order via inverse relay trident messages |
| S3 | 13 January 2026, 18:08 | NSIGII protocol overview — human rights protocol, pointer problem, OX-STAR |
| S4 | 7 February 2026, 11:07 + 2 March 2026 | Formalising suffering; here-and-now/stillness; radio jamming and the maybe lattice |
| S5 | (undated, short) + 12 February 2026 | Trilateral governance; reference implementation demonstration |
| S6 | 28 June 2026 + (undated) | Dimensional principality and non-linearity; the NSIGII codec and language classifiers |

### 0.3 Transcription caveat

The corpus is machine-transcribed speech. Proper nouns, symbols and numbers are
frequently corrupted (`in sigi`, `insigi`, `insidity`, `ciggy`, `sympathy pro
called` all denote **NSIGII**; `Cisco` denotes **CISCO** as defined in §4, not
the network vendor; `rift` denotes the **RIFT** toolchain; `lapis` denotes
**LAPIS**, §7.4). Numeric claims are reproduced in Appendix A with corrected
values.

### 0.4 Conformance language

**MUST**, **MUST NOT**, **SHOULD**, **MAY** are used in the RFC 2119 sense.
Statements marked *(unresolved)* are recorded intent that is not yet
specifiable.

---

## 1. Overview

### 1.1 Name

**NSIGII** — spelled in the corpus as November–Sierra–India–Golf–India–India.
The name is drawn from Igbo (Niger–Congo). Igbo is described in the corpus as a
tonal, verb–noun–constructed language, and that construction is load-bearing:
the protocol's instruction model is a verb–noun pairing (§9.1), and its tonal
distinction is used as the canonical example of a message whose meaning depends
on a channel the encoding must preserve.

The corpus gives the tonal example directly: *eze* under one tone contour means
**king**; under another it means **teeth**. The protocol's stated position is
that "the king has teeth" — the governance layer and the enforcement layer are
the same word under different tone. A codec that drops tone drops meaning; this
is the motivating case for schema-level rather than message-level verification
(§3.8).

### 1.2 Purpose

NSIGII is a **command-and-control protocol for safety-critical delivery of
human-rights entitlements** — stated in the corpus, repeatedly and without
metaphor, as *food, water and shelter, here and now*. Its technical content is
in service of that: a message that says "I need food at this address now" must
survive corruption, must be verifiable by a third party, must not be silently
dropped, and must leave an auditable record that a duty-holder received it.

The protocol is explicitly **not** an AI system. The corpus is emphatic that
natural-language understanding here is structural (§9), not learned.

### 1.3 Governance invariants — the Three Nevers

NSIGII implementations **MUST** satisfy three invariants (S5). They are **not
three independent rules.** Each is the invariant of one **addressing mode**
(§7.1) — the Three Nevers and the addressing triad are the same structure seen
twice (author ratification, 25 Aug 2026):

> **here and now — never a toy**
> **there and then — never a weapon**
> **where and whenever — never a problem**

| Mode | Never | Requirement |
|---|---|---|
| **HERE AND NOW** | **never a toy** | The system **MUST NOT** be shipped as a demonstration or a game. |
| **THERE AND THEN** | **never a weapon** | The system **MUST NOT** be usable as an instrument of harm against the person it serves. |
| **WHERE AND WHENEVER** | **never a problem** | The system **MUST NOT** crash and **MUST NOT** accumulate debt. It fails *gracefully*: times out, resolves outstanding state, saves, closes. |

**Why each never belongs to its mode:**

1. **HERE AND NOW → never a toy.** The deictic mode is where the need is
   *actual* — food, at this address, now. Both dimensions bound means both are
   real. A toy is a thing played with in the present; the mode that owns the
   present is therefore the mode that must forbid play. The corpus: *"it's not
   a toy, that's not how to play with it — it's something that gives people
   food and shelter."*

2. **THERE AND THEN → never a weapon.** **Displacement is what makes a weapon
   possible.** Targeting *is* a there-and-then operation: a specified
   elsewhere, a specified later, acted on at a distance. Every reach the
   protocol has — OX-STAR injection, guiding a craft in flight, disarming a
   running system (§6.4) — lives in this mode. The prohibition is therefore
   placed exactly where the reach is. A protocol that can act at a distance
   **MUST NOT** act at a distance to harm.

3. **WHERE AND WHENEVER → never a problem.** The unbound mode **cannot fail
   into a fault, because it has no slot to miss.** A claim quantified over all
   place and time is never overdue, so it never accrues debt; it is not failing,
   it is unresolved. Graceful failure is not a behaviour bolted onto this mode —
   it is what unboundedness *is*. This is the same result §7.1.2 reaches from
   the other direction: an unbound claim cannot time out into nothing.

> **Naming note (v0.3).** v0.1–0.2 of this document rendered the first invariant
> as "never fails." That is the corpus's *gloss*, not its name. S5 states
> **"never a problem"** and then explains it as *"it never fails — it fails
> gracefully, it times out, it resolves all issues and saves."* The canonical
> name is restored here.

> **Tension (§11.3, now largely resolved).** S5 states "never a weapon — you
> cannot sue people" while S5b develops NSIGII explicitly as a **litigation
> system** (§11.2). The mode pairing gives the resolution a precise locus:
> "never a weapon" is the invariant of **there and then** — the protocol's own
> reach across space and time. A claimant using their own verified record to
> enforce their own entitlement is not the protocol reaching out to harm; it is
> the claimant acting in **here and now**, under a different invariant
> entirely. See §11.3.

### 1.4 Governance topology

NSIGII is described as **trilateral**, over a lattice of three governance modes:

- **Unilateral** — one party acts; the protocol records.
- **Bilateral** — two parties; the yes/no axis.
- **Trilateral** — three parties; the yes/no/**maybe** axis, which is the
  protocol's native consensus form (§5.4).

The transport topology is **peer-to-peer**, not blockchain. The corpus rejects
blockchain explicitly while retaining the property it wants from it — that a
record, once made, has teeth.

### 1.5 Position in the OBINexus toolchain

NSIGII sits above the OBINexus build and language stack and consumes its
artefacts:

```
riftlang.exe  →  .so.a  →  rift.exe  →  gosilang
                    ↑
                 nlink  →  polybuild
```

Concretely, per the corpus:

- **RIFT** supplies the token model NSIGII packets carry: the triplet
  *(token type, token value, token data)* — §3.5.
- **`.rift` files** carry the macro/meta control sequences that NSIGII relays.
- **gosilang** is the stated implementation target for the clause/`then`
  control-flow model in §9.4.
- The reference implementation demonstrated in S5b is C, built with `make`,
  with a Go codec (§8.2).

---

## 2. Foundational Model

### 2.1 The six operators

NSIGII organises all state change into **three complementary pairs**:

| Pair | Constructive | Destructive |
|---|---|---|
| Existence | **create** | **destroy** |
| Structure | **build** | **break** |
| Restoration | **repair** | **renew** |

The corpus's governing statement: *if you can build something you can break it;
if you can create something you can destroy it; if you can repair something you
can renew it.* Capability is symmetric. An implementation that offers one half
of a pair **MUST** account for the other half — either by implementing it or by
declaring it structurally impossible (§2.3).

Note that *repair* and *renew* are **both** constructive in ordinary usage; the
corpus treats **renew** as the operator that replaces a value the receiver
cannot resolve (a `ε` or `θ`, §3.7), and **repair** as the operator that
corrects a value the receiver resolved wrongly. That distinction is preserved
here.

### 2.2 Order and Chaos sequences

Two opposed instruction sequences run over the six operators.

- **ORDER** — the coherent sequence. The system is working with itself.
  Canonical form: `create → build → repair → renew`.
- **CHAOS** — the inverse sequence. The system is working against itself.
  Canonical form: `destroy → break → renew → repair` (the reverse traversal).

**CHAOS is not an error state.** This is the protocol's central move: chaos is
the *observable*, and order is inferred from it. The corpus: *"you check chaos
for order just by observing the dimension of order and chaos where the program
was running."* A receiver observes the chaos sequence and computes what the
order sequence must have been. The system is described as *a system that knows
what it is doing via observe-then-consume*.

Every channel therefore carries a **status** of `ORDER` or `CHAOS`. The
demonstration in S5b shows a receiver reporting status `chaos` and resolving
toward `order` — this is nominal behaviour, not a fault.

### 2.3 The isolation principle (enzyme model)

The corpus's founding analogy is salivary enzyme:

- It has **no nucleus**. It does not replicate itself.
- It **breaks down** food. It does not build.
- It **cannot repair or rebuild itself**. It is replaced from outside, by the
  gland, at a **constant rate — not exponential**.
- It nonetheless *does a job as a system* without being a conscious organism.

The design rule extracted from this: **a verifying component MUST be isolated
from the thing it verifies, and MUST NOT be able to repair itself.** A verifier
that can rewrite itself can be made to agree with anything. Replacement of a
verifier comes from outside the verification path, at a bounded constant rate.

This is the structural argument for the three-channel separation in §5.

### 2.4 Filter and Flash

Two interdependent phases (S2, S5b).

**FILTER** — sorting, searching, merging, splicing, slicing. Filter operations
are **pure**: they mutate *data* but **MUST NOT** mutate *program state*. The
corpus enumerates merge sort and splice as canonical filters and notes that
splice prunes an index without touching the state of the program.

**FLASH** — storing, sending, clearing, deleting. Flash is the phase that
*commits*: it writes the message out, or writes it down.

**Interdependency.** Neither is meaningful alone. Filter without flash computes
and discards; flash without filter commits noise. The ratio between them is
fixed by the CISCO read/write budget in §4.3: **two filter operations per one
flash operation.**

Marshalling (§8.3) is described as a flash operation — *"if you can marshal,
you're doing a flash."*

---

## 3. The Trident Packet

### 3.1 Why three

The world is three-dimensional; therefore an interpretation that is to be
served over it is three-dimensional. A **trident packet** carries the message
across three axes — **X**, **Y**, **Z** — and preserves it under any one of
them.

The three axes are **not** three copies. They are three *readings* of one
message, which is why two of the three suffice to verify (§3.6).

### 3.2 Frame geometry

The canonical frame derives from the reference string `OBINEXUS`:

| Quantity | Value | Derivation |
|---|---|---|
| Reference symbol count | 8 | `O B I N E X U S` |
| Index space per axis | 8 | indices 0–7 |
| **Frame size** | **512 bytes** | 8³ — the index space over three axes |
| Bytes per symbol slot | 64 | 8² = 512 / 8 |
| Trident total (3 frames) | 1536 bytes | 512 × 3 |
| Half-frame | 256 bytes | 512 / 2 |
| **Allocation quantum** | **4 bytes** | 256 / 64 |

The 4-byte quantum is the unit the corpus insists on: memory **MUST** be
allocated *ahead of time*, in 4-byte sequences, per §10.

> **Errata A.2, A.3.** The generalisation to the full Latin alphabet is stated
> in S2 as 15,625 (= 25³, using the *maximum index* 25 as the base). For 26
> symbols indexed 0–25 the correct figure is **26³ = 17,576**. The 8-symbol
> case (8³ = 512) is correct as stated.

### 3.3 Axis pairs and sequence

Two axes generate four ordered readings:

```
XX    XY    YX    YY
```

- `XX` — the message read along X against itself. The **verification axis**.
- `XY`, `YX` — the cross readings. These carry direction of flow.
- `YY` — the message read along Y against itself.

The corpus's rule: **"you cannot have a Y-axis without an X-axis."** Y is
computable from two X readings (one positive, one negative) via the polar
relation in §7.4. Z is the projection — the tangent relation between X and Y —
and is used for **rotation**, not for carrying payload.

Therefore: **verification operates on the X axis only.** A verifier that needs
Y or Z to decide has been given an incomplete frame.

### 3.4 Index-pair addressing

Positions in the frame are addressed as **index pairs**, not scalars:

```
(0,0) (1,1) (2,2) (3,3) (4,4) (5,5) (6,6) (7,7)
```

for the 8 symbol slots of `OBINEXUS`. The pair is *(my index, your index)*: the
diagonal `(n,n)` asserts agreement between sender and receiver on slot *n*.

An **off-diagonal pair received where a diagonal was expected is a detected
corruption.** The corpus's worked case: receiving `(3,2)` for a slot whose
schema says `(3,3)` means the message is wrong *automatically*, with no need to
inspect the payload. Similarly `(1,2)` decodes to `B`/`I` disagreement and is
rejected on the index alone.

**Negative indices** are the polar inverse: `(-3, 3)` addresses the same slot
from the opposite end of the axis. The corpus's use: when the receiver cannot
resolve a symbol at all, the sender transmits *both* poles — `-3` and `3` — so
the receiver can locate the slot from whichever end it is reading from. This is
why a repair transmission carries **up to three packets, two at a time**
(§3.6).

### 3.5 Token triplet

Each addressed unit carries a RIFT triplet:

| Field | Meaning |
|---|---|
| **token type** | the type of the value |
| **token value** | the value itself |
| **token data** | the datum the value acts on / is logged as |

The corpus's phrasing — *"a token of valuable type... the shared token value
and a token type"* — makes type and value independently transmissible, which is
what allows a receiver to repair a value while keeping its type (§3.7).

### 3.6 The 3→2 verification mapping

A trident sends **three** messages; verification consumes **two**.

With each of the three labelled `ORDER` (O) or `CHAOS` (C), the receiver may be
handed any of:

```
OO    OC    CO    CC
```

— four ordered pairs, three unordered combinations `C(3,2) = 3`. The corpus
names them as "two orders, one order one chaos, two chaos."

**Rule.** A receiver **MUST** reach a verdict from any two of the three. It
**MUST NOT** require all three. The third is the spare — it is what makes the
system survive a single-channel loss, and it is why the corpus notes that *"two
homogeneous transistors can fail"* while the system still resolves.

**Springs.** The 3→2 relation is modelled on spring physics: the message is
pushed and returns. The operational consequence is the space/time duality of
§10.2 — *half the message, double the time*, and its inverse.

### 3.7 Corruption classes

The corpus works a single example throughout. Sender transmits `OBINEXUS`;
receiver reports:

```
sent:      O    B    I    N    E    X    U    S
received:  O    I    ε    θ    ε    X    U    S
```

Three distinct failure classes, which **MUST** be handled differently:

| Class | Symbol | Meaning | Operator |
|---|---|---|---|
| **Substitution** | a wrong symbol (`I` for `B`) | receiver resolved, resolved wrongly | **repair** |
| **Empty** | `ε` (epsilon, written as slashed E) | receiver resolved to nothing | **renew** |
| **Uncertain** | `θ` (theta) | receiver is unsure between candidates | **renew** with disambiguation table |

`ε` is the corpus's "you don't know what this is." `θ` is "you're not sure what
this is" — a *bounded* ambiguity, where the receiver has candidates but cannot
choose. The corpus's worked θ case: `N` may be read as `E`, `I` or `M`
depending on where the reader started on the lookup grid, because *"my N is
your E, my E is your X, my X is your S"* — a uniform off-by-one shift of the
reader's frame.

### 3.8 Repair procedure

Repair is **index-first, payload-second**. The sender **MUST NOT** retransmit
the payload for a slot the receiver resolved correctly.

For the worked example:

1. **`O` at slot 0** — received correctly. **No action.** The corpus is
   explicit: *"O is fine. I verified. I didn't need to send O again."*
2. **`B` at slot 1, received as `I`** — substitution. The sender transmits the
   **index pair** `(1,1)`, not the letter. The receiver's `(2,2)` reading is
   corrected to `(1,1)`.
3. **`ε` at slot 2** — empty. The sender **renews** the slot, transmitting
   `(2,2)` plus the value.
4. **`θ` at slot 3** — uncertain. The sender transmits the polar pair
   `(-3, 3)` so the receiver can locate the slot from either end, plus a
   **shift-of-view** instruction (§3.9).
5. **`X`, `U`, `S`** — received correctly. **No action.**

**Schema, not message.** The verification target is the **schema**, not the
payload. The corpus: *"the schema is supposed to verify, not the message...
message can be tampered with but not the schema."* This is the reason index
pairs are the repair currency: they are schema-level assertions.

### 3.9 Lookup grid and shift-of-view

Where a `θ` cannot be resolved by index alone, the sender transmits a
**shift-of-view**: a relative move on a 2-D lookup grid of the symbol set,
expressed as `(Δrow, Δcolumn)`.

The corpus's example: to get from `I` to `N` on the grid is *"one right, one
down"*; the inverse is `(-1, -1)`. The sender may transmit either the single
move, the pair of moves, or — as a last resort — the whole substructure of the
table.

Permitted transformations on the grid are the standard four:

```
rotation    reflection    translation    enlargement
```

parameterised by θ, with a full rotation being 2π. The search space is the area
swept; §7.2 gives the parity rule that bounds it.

### 3.10 XOR parity

Verification across the trident uses **XOR**, on the stated ground that XOR
*remembers state*: it is an operator that encodes the prior value into the
result and is its own inverse.

The corpus works the hex directly: `O = 0x4F`, `B = 0x42`, `I = 0x49`. Where a
slot survives unchanged, `v ⊕ v = 0` and the parity contributes nothing; where
it differs, the parity carries the difference. *"When you verify a message over
XOR you get another message — a parity message — and the parity sequence gives
you the result you need."*

The polar sign convention: a right-hand-side XOR preserves the byte; the
negative operator is the left-hand-side reading of the same structure. The
poles multiply rather than add, because they are dimensional rather than
scalar.

---

## 4. CISCO Order

### 4.1 Definition

**CISCO** in this specification denotes the corpus's bottom-up self-balancing
tree discipline. It has nothing to do with the network vendor.

A CISCO tree is:

- **self-balancing**, and specifically a red-black tree *that never needs
  pruning* — the corpus's requirement is that the message structure never has
  to be discarded to stay balanced;
- traversed **root → left → right**;
- parsed **bottom-up** (leaves to root), while the *top-down* model shares the
  same two poles at each step;
- the structure over which the message `OBINEXUS` is held, with `O` at the
  root, `B` left, `I` right, and so on.

The Riemann hypothesis is invoked in S3 as the intended means of deciding, from
signal structure alone, whether a given number was produced by bottom-up
traversal. *(Unresolved — see Appendix C.1.)*

### 4.2 Read / Write / Execute permutations

Three permissions generate six orderings; the corpus works with them as a
3 × 3 selection problem:

```
R W X        W R X        X R W
R X W        W X R        X W R
```

The **diagonals** are where a permission is shared between two positions —
`R R` on one diagonal, `W W` on the other. Those shared cells are what make the
matrices composable: two matrices that share a diagonal can be verified against
each other.

Octal permission tags follow POSIX and are carried on the wire (S5b):

```
r = 4    w = 2    x = 1
```

> **Errata A.10.** S5b states "one would be easy to write." Under POSIX,
> `1` is **execute** and `2` is **write**.

### 4.3 The 2R → 1W → 1X ratio

The corpus's execution budget, stated repeatedly:

```
2 reads  →  1 write
2 writes →  1 execute
```

One read alone is a write in progress; **two** reads complete a write. A write
is thus one *implicit* filter plus one *explicit* flash (§2.4). In frame terms:

```
512 bytes  per  2 read operations  =  1 execute operation
```

### 4.4 Hops, and rotation instead of traversal

Moving between R, W and X states costs **hops**: minimum one, **maximum two**
left hops to reach the execute root.

The optimisation the corpus insists on: **the two hops are not serial.** They
are not to be walked. Instead the tree is **rotated** — *"you don't have to do
the hops per se, you just have to do one context switch... you just change the
angle of the message."* Two hops become **two rotations of the CISCO tree**,
and the message is unchanged; only the reader's frame moves.

This is the same mechanism as the shift-of-view in §3.9, applied to the
permission tree rather than the symbol grid. Under rotation:

```
my execute  →  your read
my read     →  your write
my write    →  your execute
```

and the dimension of the system is preserved because the flash was already
sent — only the angle changed.

### 4.5 Determinant sharing

Two 2×3 (or 3×2) permission matrices are reconciled by exchanging
**transposes**, not the matrices themselves, and computing a determinant
relation over the pair.

The corpus's worked figures: `R_w = [1, 0, 1]`, `R_r = [0, 1, 2]`, with
transposes exchanged so that the shared cells (`0` and `1`) are visible to both
parties without either disclosing its full matrix.

> **Errata A.11.** The determinant arithmetic in S2 is not recoverable from the
> transcript — the audio degrades into repeated self-correction and the stated
> products do not reconcile. The *mechanism* (exchange transposes, verify via a
> determinant relation, disclose no full matrix) is clear and is what is
> normative here. The specific figures are not.

---

## 5. Channel Model

### 5.1 Roles

Three channels, three roles (S5b):

| Channel | Role | Function |
|---|---|---|
| **CH0** | **Transmitter** | encodes raw message into packet format; computes SHA-256 message hash; attaches r/w/x permission tag and the order/chaos status |
| **CH1** | **Receiver** | deserialises the packet; decodes from the wire form |
| **CH2** | **Verifier** | brokers consensus; broadcasts the verdict |

The three roles map onto the three verbs the corpus names as the only ones the
system has: **receive, transmit, verify** — in all six orderings, per §4.2.

The channels **MUST** be independently verifiable and **MAY** be run
independently of one another. The isolation principle (§2.3) requires that CH2
cannot repair itself.

> **Inconsistency.** S5b describes the ring as *"channel 0 sender, channel 2
> receiver, channel 3 verifier"* in one passage and demonstrates
> `make ch0` / `make ch1` with a channel-2 verifier in another. This document
> normalises on **CH0 / CH1 / CH2** as tabulated.

### 5.2 Ring topology

```
        CH1 (receiver)
       ╱               ╲
   CH0 ───────────────── CH2
 (sender)            (verifier)
```

CH0 broadcasts; CH1 receives locally; CH2 verifies and broadcasts the verdict.
The corpus's worked exchange:

```
CH0 →  "Hello. I am here for food."
CH1 →  "Yes. Here is your food."
CH2 →  "Verified."
```

### 5.3 Observed failure modes

The S5b demonstration produced three failures, all of which are **specified
behaviour** and **MUST** be reported rather than masked:

| Failure | Meaning |
|---|---|
| `hash mismatch` | SHA-256 digest of the received frame ≠ transmitted digest. The message may still be legible; the frame is not verified. |
| `consensus failed` | CH2 could not reach a verdict from two of three. The system **MUST NOT** exit; it holds. |
| `phantom ID` | An identifier appeared on the ring with no originating channel. Not fatal — the corpus classes it as a phantom network condition, to be observed rather than acted on. |

Note that in the demonstration the message *arrived and was legible* while the
hash failed. That is the intended separation: legibility and verification are
different verdicts.

### 5.4 RGB tomographic state

Channel state is carried as an RGB triple, where the three components are
**pointers to state**, not colours (S3):

| Component | Meaning |
|---|---|
| **Red** | **drift.** A party that is drifting appears more red. Two reds (light/dark) are distinguished by hue, saturation and lightness. |
| **Green** | **verified.** Green is the consistency check. A message is *not green until it is sent and verified.* |
| **Blue** | **neutral / character state.** Blue is the observing state: neither drifted nor verified. |

The three parties share the *dimension* (hue), not the value. Agreement is the
qualification between two reds; the green is the anchor state that is
measurable by a third party. The corpus explicitly frames this as a
**zero-knowledge** arrangement: the verifier confirms agreement without holding
either party's value.

Grey/brown are named as the decayed state — information loss, measured by ratio
(K, thousand) over the shared π-frequency.

### 5.5 Consensus and channel eviction

Where a channel becomes hostile or is captured, the remaining channels
**vote it out** (S4b). The corpus's worked case: channels `A4`, `B4`, `C4`
observe that `D3` has lied to `B4`; the three vote, `D3` is crossed out
(`XXX`), and connections to `D3` are killed until the real-world cause is
established.

Requirements:

- Eviction **MUST** be by consensus of the remaining channels, never
  unilateral.
- Eviction **MUST** be reversible on re-establishment of the cause.
- The vote **SHOULD** use XOR over the open channel, per §3.10.

### 5.6 Actors

The corpus names two protocol actors, from Igbo:

- **Obi** — heart, soul; king or leader. The **local observer**. Obi sees the
  system from the inside out, observes tomographically, and is *not directly
  involved in the command and control.*
- **Uche** — knowledge (Charlie–Hotel–Echo). The **acting party**.

Each can create and destroy the other. Neither is the verifier of itself.

---

## 6. Signal Model

### 6.1 The noise/signal quadrants

Four states, generated by two independent binaries (S3):

|  | **signal** | **no signal** |
|---|---|---|
| **noise** | noise + signal | noise, no signal |
| **no noise** | no noise + signal | **no noise, no signal** |

The corpus's reading of each:

- **no noise, no signal** — the system is on, potential, quiescent. *Not* off.
- **no noise + signal** — clean channel; connection may be established.
- **noise + signal** — live and degraded; the working case.
- **noise, no signal** — losing connection, or drifting out of detection.

Machine states map on: **on**, **standby**, **hibernate** (regulating
resources), **sleep** (off for a short time).

### 6.2 Your noise is my signal

The protocol's inversion principle, from the radio session (S4b): *"your noise
is my signal."* An adversary jamming a band is emitting structure; that
structure is itself information about the adversary. An NSIGII receiver
**SHOULD** treat detected jamming as a signal source rather than only as a
degradation.

Consequently: **a complete system is one that knows it can be jammed.** The
corpus: *"a system that can be jammed knows it can be jammed — so it can be
anti-jammed."* Self-knowledge of the failure mode is a completeness criterion.

### 6.3 The maybe lattice

The two binaries of §6.1 are crossed with the **maybe / maybe-not** operator to
give a 4 × 4 state lattice:

```
maybe noise          maybe no noise          maybe signal          maybe no signal
maybe-not noise      maybe-not no noise      maybe-not signal      maybe-not no signal
```

**maybe-not** is a *nullifying* operator: it nullifies a state in order to
verify it — "check for noise; test for no noise." It is the interrogative form
of the state, and it is what makes the lattice a calibration procedure rather
than a classification.

The balloon model: each channel is a balloon that inflates and deflates.
Inflation is signal emerging from noise; deflation is signal collapsing into
noise. Three balloons — maybe, maybe-not, and the popped/ground case — give the
trident its physical reading.

> **Errata A.9.** The worked figure in S4b (`2^-1 × 3 = -0.1`) does not
> reconcile. `2^-1 × 3 = 1.5`; `(-2)^-1 × 3 = -1.5`. The intended quantity is
> not recoverable.

### 6.4 OX-STAR and NOISE-STAR

**OX-STAR** (auxiliary star) is the on-the-fly injection mechanism: a sequence
that turns a system on, off, or into a new mode **while it is running**,
without a human at the location.

The canonical OX-STAR sequence is the **Konami code**:

```
↑  ↑  ↓  ↓  ←  →  ←  →  B  A  START
```

This is not decoration. The corpus's reading of it is precise and is the
protocol's own send-rule:

- **`↑` once** is *half* the instruction — held, not sent.
- **`↑ ↑`** is the complete instruction — **sent**.
- Likewise `↓ ↓`, `← →`, `← →`.
- **`B A`** are the bounded terminals — button-plural rules, a stop-and-place.
- **`START`** commits; **`SELECT`** requests more options.

This is the *half the structure, double the send* rule (§10.2) made concrete:
an OX-STAR is a **scalar tensor that takes half a dimension up**, so each
instruction must be pressed twice to be sent once.

**NOISE-STAR** is the complementary state family — `ox-noise`, `ox-no-noise`,
`ox-signal`, `ox-no-signal` — carrying the §6.1 quadrant into the injection
layer, so that an injected command knows the standby state of the system it is
entering.

Stated applications: guiding a drone in real time; disarming a system mid-
flight; switching a running program's mode without unloading it.

### 6.5 Probing

**Processing** is executing what the system already knows how to do.
**Probing** is the system seeking a *new* solution structure for the same
problem. The distinction is normative: a probe **MUST NOT** be logged as a
process.

Two probe directions:

```
external probe:   P(state)  →  data
internal probe:   P(data)   →  state
```

A probe asks the five interrogatives — **who, what, when, where, why** — and it
does so **without a human in the loop**. The corpus distinguishes *human in the
loop*, *human on the loop*, and *human out of the loop*; probing is out-of-loop
by construction, which is why §6.5's constraints matter.

Probe health is a scalar in `[0, 1]` on each node. A structurally healthy node
probes for more inputs; a degraded node probes for more statements. This makes
protocol functions **dynamic**: they can resolve ambiguity by interpretation.
The corpus's minimal case — *"I am Python." "No, I am Python." Who is
right?* — is the ambiguity a probe exists to settle.

---

## 7. Here-and-Now, There-and-Then, Stillness

### 7.1 The temporal-spatial matrix

The protocol addresses place and time as a **2 × 3 matrix** over three modes
(S4a, S5, ratified 25 Aug 2026). The canonical statement of the triad is:

> **here and now — there and then — where and whenever**

Each mode names a **degree of binding**, and each has two orderings — space
first, or time first — which is what makes the matrix 2 × 3 rather than a list
of three.

| Mode | Binding | Invariant (§1.3) | **space first** | **time first** |
|---|---|---|---|---|
| **HERE AND NOW** | both bound, **deictic** | never a toy | *here and now* — present in space, then time | *now and here* — present in time, then space |
| **THERE AND THEN** | both bound, **displaced** | never a weapon | *there and then* — there in space, then in time | *then and there* — there in time, then in space |
| **WHERE AND WHENEVER** | both **unbound** | never a problem | *where and whenever* — in space, for all time | *whenever and where* — in time, for all space |

Each mode carries exactly one of the Three Nevers. The invariants are not a
separate governance layer — they are the conformance conditions on the
addressing modes, and §1.3 derives each pairing.

Each cell is a **dimensionless quantity** occurring on **one axis only** — one
place and one time at a time. The corpus likens the arrangement to a gimbal,
and to latitude/longitude. The corpus states both orderings of the first mode
explicitly: *"I need food here and now, or now and here."*

### 7.1.1 The binding progression

The three modes are not three locations. They are three **quantifier states**
over the same pair of dimensions:

1. **HERE AND NOW** — place = *this*, time = *this*. Both anchored to the
   speaker. The corpus gives this mode a **loopback address**, so that a system
   can address its own present.
2. **THERE AND THEN** — place = *that*, time = *that*. Displaced, but still
   **specified**: a particular elsewhere, a particular past or future.
3. **WHERE AND WHENEVER** — place and time are **quantified, not specified**.
   This is the **interrogative** mode: *where* and *when* are interrogative
   pronouns, and *whenever* is their free-choice form. The claim is open, and
   resolves at whatever place and time the need arises.

The third mode is where **probing** lives (§6.5). A probe asks *who, what,
when, where, why* — and the two dimensions it quantifies over are exactly the
two this mode leaves unbound.

### 7.1.2 Stillness

**Stillness** is not a fourth mode. It is the **property** the unbound mode has:
the state in which a claim persists without further action. *"You don't need
anything to be still."*

The corpus's demonstration is the cup — a drink set down out of frame, still
there when you return, returnable to indefinitely.

> **Normative consequence.** A claim entered under **WHERE AND WHENEVER**
> **MUST NOT** expire, and **MUST NOT** be discharged by the passing of a
> specific place or time. *"I need food at this address at 18:00 Tuesday"* is a
> bound claim and can be missed. *"I need food"* — unbound — is a **standing
> claim**: it is honoured wherever the claimant is and whenever the need
> arises. Food ordered under stillness arrives when it is needed, not when it
> was asked for.

This is what makes a duty-holder unable to discharge an obligation by pointing
at a missed slot, and it is precisely the content of this mode's invariant,
***never a problem*** (§1.3): an unbound claim cannot time out into nothing,
because it has no slot to miss and therefore accrues no debt. It is not
failing; it is unresolved.

Its one failure mode is **relaxation** (§10.4) — a standing claim that quietly
stops being honoured — which is why relaxation is specified as a *failure* and
not as an *expiry*. Relaxation is the only way the unbound mode can become a
problem, and is therefore the only thing this invariant has to guard.

### 7.1.3 Structural note

Three modes × two orderings = **six cells**, matching the 3 + 3 dimensional
count of §7.6 (three axes forward, three back) and the six R/W/X permutations
of §4.2. Whether these three sixes are the same six, or a coincidence of
structure, is left open (Appendix C.8).

### 7.2 Parity

Parity is treated as a **dimension**, not a predicate.

```
x mod 2 == 0   →  even
x mod 2 == 1   →  odd
```

A parity check runs on **one axis** and determines the even/odd ratio for that
axis. A **negative** quantity (`-2`) is not merely a sign: the minus is an
**operator on the negative axis**, and under it the ordinary parity rules bend.
Encoding **MUST** therefore be checkable for bit-flip pairs on both poles.

Where the rules bend, the transformation set of §3.9 applies —
rotation, reflection, translation, enlargement — and the *edge cases where the
rules break* are precisely what the stateless protocol must encode, so that
statelessness survives them.

### 7.3 The holding problem

The corpus's central engineering complaint (S6): a system that computes an
intermediate result **holds it in memory**, and holding is the cost.

Worked as a matrix product: given two vectors, the intermediate outer-product
table is what the system is forced to hold, when what it wants is the row sums.
The stated goal: **look up the result from a tabulation constructed by polar
rules, rather than compute-and-hold.**

> **Errata A.6.** The intermediate table stated in S6 —
> `[[6,10],[12,15],[16,20]]` with row sums `16, 27, 36` — is **not** a
> consistent outer product of any single vector pair. For `u = (2,3,4)` and
> `v = (3,5)` the correct outer product is `[[6,10],[9,15],[12,20]]`, row sums
> `16, 24, 32`. The *intent* — memoise intermediates so the result is a lookup,
> not a computation — is sound and is what is normative.

**Gravity well / rope and bucket.** The physical statement of the same problem:
a well has a depth (density); a rope holds a bucket; the rope **MUST** hold
indefinitely. *"Nothing likes to hold anything."* The design consequence is
that indefinite holding must be structural, not effortful — encoded into the
geometry, not maintained by a process.

### 7.4 LAPIS — polar quadrants

**LAPIS** is the corpus's polar-calculus mnemonic for the four cardinal
bearings. As given in S2:

```
π/4  =  north       π/3  =  east
π/2  =  south       π    =  west
```

> **Errata A.5.** This mapping is not consistent with standard polar
> convention, and is not internally consistent either — π/4 and π/3 are 45° and
> 60°, which are not cardinal. Under the convention the corpus itself invokes
> ("the sun rises in the east and sets in the west"), the cardinal bearings are:
>
> ```
> 0     = east        π/2   = north
> π     = west        3π/2  = south
> ```
>
> The *intent* — that the four quadrants are addressed by angle, and that a
> message chooses its bearing (θ) before it moves — is preserved. Only the
> constants are wrong. Implementations **MUST** use the standard convention.

The associated rule is real and independent of the constants: **you determine
the angle you want to move before you move**, and θ (rotation) and λ (power
distribution) are chosen together.

### 7.5 The i-cycle and the trident mismatch

S6 develops a rotation table over the imaginary unit:

```
i¹ = i     i² = −1     i³ = −i     i⁴ = 1        (period 4)
```

and alternates `i, −i, 1, −1` across axes.

> **Errata A.7 — and a proposed correction.** A period-**4** cycle is a poor
> algebraic fit for a **trident**. The natural object for a three-axis rotation
> is the **cube roots of unity**:
>
> ```
> ω = e^(2πi/3),   ω³ = 1,   1 + ω + ω² = 0
> ```
>
> The identity `1 + ω + ω² = 0` is exactly the property a trident wants: three
> readings that sum to nothing when the message is intact, and to a non-zero
> residue when it is not. That is a parity check for free, on three axes, which
> is what §3.10 is reaching for with XOR. This is offered as an improvement,
> not as a transcription of the corpus.

### 7.6 Dimensional principality

The stated axiom (S6): **dimensions have principles they obey without being
told.** A system **MUST NOT** need to be given time to think in order to
respect them — the rules are implicit and hold structurally.

Non-linearity is defined accordingly: *any structure that can be computed by
looking at it must be isomorphic under transposition.* The transpose is an
**axis of reflection** — `XYZ → ZYX` — under which a row vector becomes a
column vector and the data structure is preserved while the system moves.

The 3 + 3 count: three axes forward (`x, y, z`) and three back (`−x, −y, −z`),
because what is behind you is real whether or not you can see it. The corpus
demonstrates this with a mirror: the cup out of frame is still there.

> **Errata A.8.** S6 states `3 + 6 + 9 = 15` and derives a "minimum consensus"
> from it. `3 + 6 + 9 = 18`. It also states `3³ = 9`; `3² = 9`, `3³ = 27`.
> `6 × 9 = 54` is correct as stated.

---

## 8. Codec and File Formats

### 8.1 `.nsigii` — symbolic expression of intent

The protocol's own file format is described as a **symbolic expression of
intent** file. Properties:

- It holds space **indefinitely** — once a point is allocated, the program
  holds it. It cannot be removed, only **reallocated**.
- It is **stateless but remembering**: statelessness here does not mean "does
  not remember." It means the state is encoded into the *geometry* of the
  system rather than held in a variable. *"It remembers stuff, it doesn't need
  to forget, ever."*
- New symbol sets can be added as language evolves, without invalidating
  existing files.

The name is also given as **SIGI intent files** and, in one passage, as
`.n` (November) session/intent files. This document uses **`.nsigii`**.

### 8.2 Linkable-then-executable coding

The NSIGII codec (S6b) is **LTE-coding — linkable *then* executable**. The
demonstrated pipeline:

```
cat image.png | go run main.go   →  raw, linkable, stateless encoding
```

Properties as stated:

- The codec takes **any** input format and produces a raw encoding that
  *"can never die"* — it survives re-encoding.
- The output is **linkable as a library** and **executable on demand** — the
  corpus likens it to a DLL or a **macro system for other systems**, not a
  direct call.
- It encodes the **buffering**, which is the point: a conventional stream
  buffers before it plays; NSIGII encodes the buffer so that the receiver
  already holds the state.

The stated repositories: `github.com/obinexus/nuko-operating-system` (NUKO-OS,
the human-rights operating system) and `github.com/obinexus/legislation`.

### 8.3 Marshalling

Marshalling is the codec's serialisation contract, explicitly compared to
Python's `pickle` (`load`/`dump`):

> a receiver that holds the *codec of the function* can reconstitute an object
> it did not construct, because it knows the **shape** of the function without
> computing it.

Marshalling is classed as a **flash** operation (§2.4). Comparable wire formats
named in the corpus: **Protocol Buffers**, **gRPC**, JSON, and a binary IR.
NSIGII is schema-based like these, which is what §3.8's schema-verification
requires.

---

## 9. Dimensional Classifiers — the Natural Language Layer

### 9.1 Statement / Expression / Intent

Three poles, likened to **latitude, longitude and altitude**:

| Pole | Carries | Truth-apt? |
|---|---|---|
| **Statement** | the assertion | yes — true or false |
| **Expression** | the meaning of the assertion | no — it means |
| **Intent** | the abstract model behind it | no — it aims |

The bipolar question of an expression is *"what could this mean?"* — and that
is where a natural-language codec must operate.

The corpus's worked pair: `John likes Mary` / `Mary likes John` are two
statements over one relation, whose conjunction is positive or negative by
pole. The corpus reaches for the **discriminant** `b² − 4ac` as the object that
decides how many resolutions such a relation has. *(Unresolved as stated —
Appendix C.3.)*

### 9.2 Verb–noun construction

Following Igbo construction, the instruction unit is a **verb–noun pair**.

- A **verb** describes an action — *"to" + action*.
- An **adverb** describes the verb, and situates it in past, present or future.
- A **noun** is the classifier of the thing — and a *person* is only one
  category of noun. The corpus is deliberate here: nouns include animals and
  things, so that intent can be read from non-human experience.

### 9.3 The four sentence types

Every natural language, per the corpus, follows four **dimensional
classifiers**:

| Type | Example | Protocol role |
|---|---|---|
| **Declarative** | *I am Nnamdi.* | assertion — carries a statement |
| **Interrogative** | *Can you introduce yourself?* | **probe** (§6.5) — requests input |
| **Imperative** | *Introduce yourself.* / *Close the door.* | **command** — carries control |
| **Exclamative** | *What a funny thing he told us!* | signals surprise — an unexpected-state marker |

Crossed with four **sentence structures**:

```
short / simple        →  "I am Nnamdi."
simple (personal)     →  "My name is Nnamdi."
compound              →  one dependent + one independent clause
complex               →  two independent + one dependent clause
compound-complex      →  two compound clauses joined
```

The corpus draws a **CISC / RISC** analogy across the classifiers: the reduced
set and the complex set operate on different instruction models, but a receiver
must resolve intent from either.

### 9.4 Clauses as control flow, and the `then` marker

Clauses map directly onto control flow. The corpus develops:

```
do  →  while          do { x++ } while (x <= 25)
do  →  then  →  while  do { x++ } then LABEL while (...)
if  →  then  →  else  →  then  →  if
```

The key construct is **`then` as a block label**:

> The `then` keyword **labels code blocks**, and labelled blocks are what a
> `goto` targets — so `then` is a **switchable goto marker**.

`then` is part of the language construct. It **MUST NOT** be switched out or
broken by a consuming implementation; a language that cannot express it cannot
interpret NSIGII clauses. The stated implementation target is **gosilang**.

Traversal order matters and is carried: pre-order (`++x`) and post-order
(`x++`) produce different ranges over the same loop, and the corpus treats the
difference as an **execution-order** property of the clause, not an idiom.

---

## 10. Sizing and Timing Model

### 10.1 Frame budget

| Quantity | Value |
|---|---|
| Frame | 512 bytes (8³) |
| Trident | 1536 bytes (512 × 3) |
| Half-frame | 256 bytes |
| Pre-allocation | 2048 bytes (512 × 4) |
| Allocation quantum | 4 bytes |
| Digest | 32 bytes (SHA-256) |
| Payload after digest | 480 bytes |

Memory **MUST** be allocated ahead of time, in 4-byte sequences. The corpus is
explicit that this is *per* four bytes, not *over* four bytes — the allocation
is a grid, and the grid is what is searched for meaning.

> **Errata A.1.** `512 / 3 = 170.666…`, not an integer. The trident split of a
> 512-byte frame across three axes does **not** divide evenly. Implementations
> **MUST** choose one of:
>
> - a **510-byte payload** split `170 / 170 / 170`, with 2 bytes reserved for
>   parity — this preserves the corpus's `170 = 0b10101010` alternating
>   pattern, which is itself load-bearing (§3.4); **or**
> - an uneven split `171 / 171 / 170`.
>
> The first is recommended: `170 = 10101010₂` is the alternating index pattern
> the addressing model already uses, and the 2-byte remainder gives the XOR
> parity of §3.10 somewhere to live.

### 10.2 Space–time duality

The protocol's core trade, stated in both directions:

```
half the space  ⟷  double the time
double the space ⟷  half the time
```

A message may be halved and sent over twice the interval, or doubled and sent
in half. The **worst case is the time case** — the corpus optimises for
bounded latency, not bounded memory.

The spring model gives the mechanism: a message is *pushed* and *returns*, and
the return is what verifies it. This is why the 3→2 mapping (§3.6) works —
the third packet is the spring's return path.

### 10.3 Bit-rate derivation

> **Errata A.4 — corrected derivation.**
>
> S2 states: *"2 seconds = 6,000 milliseconds"* and derives `6000 / 1024 =
> 5.859375 → 5.86`. The division is arithmetically correct; the **input is
> not**. 2 seconds = **2,000 ms**, not 6,000 — the transcript applies a
> seconds-to-minutes factor of 60 where none belongs.
>
> Corrected, for a 512-byte frame over a 2-second window:
>
> ```
> throughput        =  512 bytes / 2 s      =  256 bytes/s  =  2,048 bit/s
> doubled frame     =  1,024 bytes
> per-unit interval =  2,000 ms / 1,024     =  1.953125 ms
> two-unit interval =  3.90625 ms
> ```
>
> S2's later figure of `51.72 ms` derives from `25.86 × 2`, where `5.86` was
> transcribed as `25.86`. Neither the 5.86 nor the 51.72 figure survives the
> corrected input.

### 10.4 Spring and damping

Springs are the protocol's model for **storing and absorbing** energy — a
message pushed against resistance stores what it will need to return.

Named failure modes, all of which have protocol analogues:

| Spring failure | Protocol analogue |
|---|---|
| **fatigue** — repeated cycles grow microscopic cracks | accumulated retransmission degrades the channel |
| **overload** — permanent deformation or breakage | a frame beyond budget does not recover |
| **corrosion** — environmental degradation over time | schema drift |
| **relaxation** — loss of tension over time | a stillness claim that stops being honoured |

A **damping factor of 2.85** is stated in S3, attributed to *"Roth theory,
clustering, nearest neighbour."*

> **Errata A.12 (unresolved).** A damping *ratio* ζ = 2.85 is heavily
> overdamped (ζ = 1 is critical). Neither "Roth theory" nor the relation of
> 2.85 to the clustering/nearest-neighbour method is recoverable from the
> transcript. Flagged for the author.

---

## 11. Governance and Enforcement Layer

### 11.1 The pointer problem

The protocol's ethical core, stated as a computing problem (S3):

> **Breathing and living are pointers that MUST hold in all contexts. Work is
> optional.**

The argument: a pointer that must not be null is the thing a system is built to
guarantee. If the breathing pointer drifts, someone is dying. If the living
pointer drifts, someone is not living. Work is a pointer that **may** be null —
and a system that forces work by dereferencing it anyway *"causes fatigue and
confusion."*

NSIGII is therefore specified as a **human-rights broker**, not a work broker.
It holds the demographic state, and it holds **negative space for work** —
because work becomes possible when space and time are already held.

### 11.2 Litigation as enforcement

S5b develops the enforcement mechanism concretely: NSIGII composes a
verified, timestamped, hash-anchored record of a request for food, water or
shelter, and of the duty-holder's response or non-response. The record is
transmitted by ordinary means — the corpus demonstrates it over **SMTP** — and
is intended to be usable as evidence that a statutory duty was engaged and not
discharged.

Statutes named in the corpus as the intended encoding targets (UK):

- Care Act 2014 (and the Health and Social Care Act 2012)
- Children Act 1989 — ss. 17, 21, 23C (accommodation; care leavers)
- Housing Act
- Equality Act 2010

The stated design goal is that a person can assert an entitlement **without
first knowing the statute**, because the protocol encodes which duty a given
request engages.

> **Note.** This specification describes an evidentiary and record-keeping
> mechanism. Whether a given record supports a given claim is a question of law
> and of the specific facts, and needs a qualified solicitor — a protocol
> cannot supply that, and this document does not.

### 11.3 Reconciliation of "never a weapon"

The mode pairing of §1.3 resolves the tension by giving it a locus. "Never a
weapon" is the invariant of **THERE AND THEN** — the displaced mode, which is
where all of the protocol's reach across space and time lives.

> **"Never a weapon" scopes to the protocol's own reach.** NSIGII **MUST NOT**
> be constructible into an instrument that acts at a distance to harm — it
> cannot be turned against its user, cannot be used to surveil them, cannot be
> used to deny them. Its OX-STAR injection, remote command and mid-flight
> control capabilities (§6.4) are all there-and-then operations, and all fall
> under this prohibition.
>
> It does **not** scope to the actions a claimant takes with the record the
> protocol produces. A person using their own verified record to enforce their
> own statutory entitlement is acting in **HERE AND NOW**, under the invariant
> *never a toy* — which is a requirement that the matter be treated as serious,
> not a prohibition on acting. That is the protocol working, not the protocol
> weaponised.

The two are separable because they are invariants of *different modes*. The
protocol's reach is constrained; the claimant's presence is not.

*Ratified in structure by the author's mode/never pairing (25 Aug 2026);
the wording above remains open to refinement.*

---

## 12. Conformance

An implementation conforms to NSIGII 0.3 if it:

1. Implements all six operators of §2.1, or declares in its manifest which
   half of a pair is structurally impossible and why.
2. Carries an `ORDER` / `CHAOS` status on every channel, and treats `CHAOS` as
   an observable rather than a fault (§2.2).
3. Isolates the verifier such that it cannot repair itself (§2.3).
4. Maintains the 2-filter-to-1-flash ratio (§2.4, §4.3).
5. Emits trident packets of the frame geometry in §3.2 and §10.1, with the
   `512 / 3` split resolved per Errata A.1.
6. Addresses slots by index pair, and repairs index-first (§3.4, §3.8).
7. Distinguishes the three corruption classes — substitution, `ε`, `θ` — and
   applies the matching operator to each (§3.7).
8. Reaches a verdict from any two of three readings and never requires all
   three (§3.6).
9. Verifies the **schema**, not the payload (§3.8).
10. Implements CH0 / CH1 / CH2 as independently runnable, and reports
    `hash mismatch`, `consensus failed` and `phantom ID` rather than masking
    them (§5.1, §5.3).
11. Holds — does not exit — on consensus failure (§5.3).
12. Requires consensus of remaining channels for eviction (§5.5).
13. Never mistakes `no noise, no signal` for `off` (§6.1).
14. Logs probes distinctly from processes (§6.5).
15. Addresses every claim in one of the three modes of §7.1, and **never
    expires a claim entered under WHERE AND WHENEVER** (§7.1.2).
16. Allocates memory ahead of time in 4-byte quanta (§10.1).
17. Satisfies the Three Nevers of §1.3 **as mode invariants** — *never a toy*
    on HERE AND NOW, *never a weapon* on THERE AND THEN, *never a problem* on
    WHERE AND WHENEVER — and does not treat them as a separate governance
    layer.

---

## Appendix A — Arithmetic Errata

Every numeric claim in the corpus, checked. **Stated** is what the transcript
says; **Correct** is the computed value; **Intent** is what the figure was
reaching for and is preserved.

| # | Claim | Stated | Correct | Disposition |
|---|---|---|---|---|
| **A.1** | Trident split of a frame | `512 / 3` treated as clean | `170.666…` — **does not divide** | Use 510-byte payload split `170/170/170` + 2 parity bytes. `170 = 0b10101010` preserved. §10.1 |
| **A.2** | Frame size from index space | `8³ = 512` | **512** ✓ | Correct as stated |
| **A.3** | Latin-alphabet index space | `15,625` (= 25³) | **26³ = 17,576** | Off-by-one: max index 25 used as base instead of symbol count 26 |
| **A.4** | Milliseconds in 2 seconds | `6,000 ms` | **2,000 ms** | Seconds→minutes factor of 60 wrongly applied. `6000/1024 = 5.859375` is correct division of a wrong input. Corrected chain in §10.3 |
| **A.4b** | Derived interval | `5.86 → 51.72 ms` | `2000/1024 = 1.953125 ms`; ×2 = `3.90625 ms` | `51.72` comes from `25.86 × 2`; `5.86` was transcribed as `25.86` |
| **A.5** | LAPIS cardinal bearings | `π/4 = N, π/3 = E, π/2 = S, π = W` | `0 = E, π/2 = N, π = W, 3π/2 = S` | Not internally consistent (π/4, π/3 are 45°, 60° — not cardinal). Intent — bearing chosen before movement — preserved. §7.4 |
| **A.6** | Outer-product intermediates | `[[6,10],[12,15],[16,20]]`, sums `16, 27, 36` | For `(2,3,4)⊗(3,5)`: `[[6,10],[9,15],[12,20]]`, sums `16, 24, 32` | Stated table is not a consistent outer product. Intent — memoise intermediates, look up don't recompute — sound. §7.3 |
| **A.7** | Rotation cycle | `i, −1, −i, 1` — period **4** | Correct for `i`, but a **trident wants period 3** | Use cube roots of unity `ω = e^(2πi/3)`; `1 + ω + ω² = 0` gives a three-axis parity check directly. §7.5 |
| **A.8** | Consensus minimum | `3 + 6 + 9 = 15`; `3³ = 9` | `3 + 6 + 9 = 18`; `3² = 9`, `3³ = 27`; `6 × 9 = 54` ✓ | Two slips; the 54 is right |
| **A.9** | Probe scalar | `2^-1 × 3 = −0.1` | `2^-1 × 3 = 1.5`; `(−2)^-1 × 3 = −1.5` | Not recoverable — flagged |
| **A.10** | POSIX permission octals | "`1` would be easy to write" | `r = 4`, `w = 2`, `x = 1` | `1` is execute, `2` is write |
| **A.11** | Matrix determinant exchange | figures do not reconcile | — | Mechanism normative (§4.5); specific figures are not |
| **A.12** | Damping factor | `2.85`, "Roth theory" | — | ζ = 2.85 is heavily overdamped (ζ = 1 critical). Attribution not recoverable. Flagged for author |
| **A.13** | Suffering equation | `Σ = (N − R) × K`; "if R ≥ N collapses to 0"; "if K → ∞, suffering regardless" | Needs clamping and a finite K | As stated, `R ≥ N` gives `Σ ≤ 0` (negative suffering), and `N = R` with `K → ∞` is `0 × ∞`, undefined. See A.14 |
| **A.14** | Suffering equation, corrected | — | `Σ = K · max(0, N − R)`, `K ∈ (0, ∞)` | Preserves both stated behaviours: `R ≥ N ⟹ Σ = 0`, and `K` large with `N > R` ⟹ Σ large. Recommended form |
| **A.15** | Happiness model | `H = S + C + …` (set point, circumstances, control/goals) | `H = S + C + V` | This is the Lyubomirsky–Sheldon–Schkade model (genetic **set point** S, **circumstances** C, **voluntary activity** V). Attribution added; note the model's original 50/10/40 weighting is contested in the later literature |
| **A.16** | Trident total | `512 × 3` | **1,536** ✓ | Correct (transcript garbles the digits) |
| **A.17** | Pre-allocation | `512 × 4 = 2,048` | **2,048** ✓ | Correct |
| **A.18** | Half-frame and quantum | `512/2 = 256`; `256/64 = 4` | **256**, **4** ✓ | Correct |
| **A.19** | 170 in binary | `10101010` | **`0b10101010 = 170`** ✓ | Correct — and the alternating pattern is load-bearing for §3.4 |
| **A.20** | Hex of reference symbols | `O = 4F`, `B = 42`, `I = 49` | **`0x4F`, `0x42`, `0x49`** ✓ | Correct ASCII |
| **A.21** | Konami sequence | eventually stated correctly | `↑↑↓↓←→←→ B A` | Correct; `START`/`SELECT` roles per §6.4 |
| **A.22** | Digest | "SH 56" | **SHA-256**, 32-byte digest | Leaves 480 payload bytes in a 512-byte frame |

---

## Appendix B — Reference Alphabet

The corpus uses NATO phonetics throughout, with two consistent personal
substitutions preserved here for fidelity to the source:

| Letter | Standard NATO | Corpus usage |
|---|---|---|
| O | Oscar | Oscar |
| B | Bravo | Bravo |
| I | India | India / **Indigo** |
| N | November | November |
| E | Echo | Echo |
| X | X-ray | X-ray |
| U | Uniform | **Umbrella** |
| S | Sierra | **Sarah** |
| G | Golf | Golf |
| C | Charlie | Charlie |
| H | Hotel | Hotel / *hamburger* |

Reference string: **`OBINEXUS`** — 8 symbols, indices 0–7, the basis of the
512-byte frame (§3.2).

Protocol name: **`NSIGII`** — November, Sarah/Sierra, Indigo/India, Golf,
India, India.

---

## Appendix C — Open Questions

**C.1 — Riemann and bottom-up decidability (§4.1).** S3 asserts that the
Riemann hypothesis "allows you to verify whether the number was determined via
CISCO, which is bottom-up." No mechanism is given connecting the distribution
of zeta zeros to traversal order. Either a concrete construction is needed, or
the claim should be restated as an analogy.

**C.2 — Damping factor 2.85 (§10.4, A.12).** Source and role unrecovered.

**C.3 — Discriminant in the language layer (§9.1).** `b² − 4ac` is invoked to
decide the resolution count of a two-party relation. The mapping from a
declarative pair to the coefficients `a`, `b`, `c` is not given.

**C.4 — "Never a weapon" vs. litigation (§1.3, §11.3). RESOLVED v0.3.** The
mode pairing scopes "never a weapon" to THERE AND THEN — the protocol's own
reach — while a claimant enforcing their own record acts in HERE AND NOW under
*never a toy*. The two are invariants of different modes and are therefore
separable. Wording in §11.3 remains open to refinement.

**C.5 — Channel numbering (§5.1).** CH2 vs CH3 as verifier — normalised here to
CH2, pending confirmation.

**C.6 — Igbo tone in the wire format (§1.1).** The tonal `eze` example is the
motivating case for schema-level verification, but no encoding for tone is
specified. If tone is meaning, the frame needs a tone channel — this may be
what the Z axis is for.

**C.7 — Cube roots of unity (§7.5, A.7).** Whether to adopt ω in place of i is
a design decision, not a correction. Recommended, but the author's call.

**C.8 — The three sixes (§7.1.3).** Three addressing modes × two orderings, the
3 + 3 dimensional count, and the six R/W/X permutations all give six. Whether
these are the same six under different names — which would let a claim's
addressing mode be derived from its permission tag, or vice versa — or a
coincidence of structure, is open. If they are the same six, the addressing mode
need not be carried on the wire at all.

---

## Appendix D — Traceability

| Spec section | Corpus segment |
|---|---|
| §1.1 Name, Igbo tone | S3, S5b |
| §1.2 Purpose | S3, S5, S5b |
| §1.3 Three Nevers (as mode invariants) | S5; mode pairing ratified by author 25 Aug 2026 |
| §1.4 Governance topology | S5, S5b |
| §1.5 Toolchain | S3 (RIFT tokens), S6b (gosilang), S5b (build) |
| §2.1 Six operators | S1 |
| §2.2 Order/Chaos | S1 |
| §2.3 Enzyme model | S1 |
| §2.4 Filter/Flash | S2, S5b |
| §3 Trident packet | S1, S2 |
| §3.7 Corruption classes | S1 |
| §3.10 XOR parity | S1, S4a |
| §4 CISCO order | S1, S2 |
| §5 Channel model | S5b |
| §5.4 RGB tomographic | S3 |
| §5.5 Eviction | S4b |
| §5.6 Obi / Uche | S3 |
| §6.1–6.2 Signal model | S3, S4b |
| §6.3 Maybe lattice | S4b |
| §6.4 OX-STAR | S3 |
| §6.5 Probing | S3, S4a |
| §7.1 Here-and-now / there-and-then / where-and-whenever | S4a, S5; triad ratified by author 25 Aug 2026 |
| §7.2 Parity | S4a |
| §7.3 Holding problem | S6a |
| §7.4 LAPIS | S2 |
| §7.5–7.6 Dimensionality | S6a |
| §8 Codec | S6b, S5b |
| §9 Language layer | S6b |
| §10 Sizing and timing | S1, S2, S3 |
| §11 Governance | S3, S5, S5b |

---

*End of NSIGII Protocol Specification v0.3 (Draft).*
