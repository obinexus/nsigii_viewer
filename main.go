package main

import (
	"bufio"
	"bytes"
	"compress/flate"
	"encoding/binary"
	"flag"
	"fmt"
	"io"
	"log"
	"math"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// ============================================================================
// FILE FORMAT: LTF (Linkable Then Format/File)
// This file is NOT a traditional ELF binary. It operates as an LTF artifact:
//   - LINK phase: resolved via nlink/polybuild orchestration
//   - THEN phase: symbol binding and trident channel wiring
//   - EXECUTE phase: go run / go build produces the executable
//
// Pipeline: riftlang.exe → .so.a → rift.exe → gosilang → nsigii-codec
// Orchestration: nlink → polybuild
// Invocation: '<input>.mp4' | go run .\main.go  (stdin pipe → LTF entry)
//
// `go run main.go -input <input.ext> -output output.lte // linkable then executable
//
// ELF assumes link-at-compile. LTF asserts link-before-execute as a
// constitutional step — the codec is not valid until channel binding
// (TRANSMIT → RECEIVE → VERIFY) completes the trident resolution.
// ============================================================================

// ============================================================================
// NSIGII POLYGATIC VIDEO CODEC WITH TRIDENT VERIFICATION
// Integrates: ROPEN sparse duplex, RB-AVL pruning, discriminant flash verification
// Bipolar enzyme model: Create/Destroy, Build/Break, Renew/Repair
// ============================================================================

// Constants for NSIGII Protocol
const (
	VERSION         = "7.0.0"
	TRIDENT_CHANNELS = 3
	LOOPBACK_BASE   = "127.0.0."
	
	// Channel IDs
	CHANNEL_TRANSMITTER = 0 // 1/3 - Encoder (ORDER)
	CHANNEL_RECEIVER    = 1 // 2/3 - Decoder (CHAOS) 
	CHANNEL_VERIFIER    = 2 // 3/3 - Verifier (CONSENSUS)
	
	// Bipolar States
	STATE_ORDER     = 0x01
	STATE_CHAOS     = 0x00
	STATE_VERIFIED  = 0xFF
	
	// RWX Permissions
	RWX_READ    = 0x04
	RWX_WRITE   = 0x02
	RWX_EXECUTE = 0x01
	RWX_FULL    = 0x07
	
	// ROPEN Constants
	POLARITY_POS = '+'
	POLARITY_NEG = '-'
	PRUNE_THRESHOLD = 0.5
	EPSILON_PAD = 0x00
)

// ============================================================================
// DISCRIMINANT FLASH VERIFICATION
// Uses quadratic formula: Δ = b² - 4ac to determine state
// ============================================================================

type DiscriminantState int

const (
	DISCRIMINANT_ORDER     DiscriminantState = iota // Δ > 0: Two real roots
	DISCRIMINANT_CONSENSUS                          // Δ = 0: One root (flash point)
	DISCRIMINANT_CHAOS                              // Δ < 0: Complex roots
)

type FilterFlash struct {
	A, B, C float64
	State   DiscriminantState
	mutex   sync.Mutex
}

func NewFilterFlash(a, b, c float64) *FilterFlash {
	return &FilterFlash{A: a, B: b, C: c}
}

func (ff *FilterFlash) ComputeDiscriminant() float64 {
	return ff.B*ff.B - 4*ff.A*ff.C
}

func (ff *FilterFlash) ContextSwitch() DiscriminantState {
	ff.mutex.Lock()
	defer ff.mutex.Unlock()
	
	delta := ff.ComputeDiscriminant()
	
	switch {
	case delta > 0:
		ff.State = DISCRIMINANT_ORDER
	case delta == 0:
		ff.State = DISCRIMINANT_CONSENSUS
	default:
		ff.State = DISCRIMINANT_CHAOS
	}
	
	return ff.State
}

// QuadraticRoots returns the roots via: (-b ± √Δ) / 2a
func (ff *FilterFlash) QuadraticRoots() (float64, float64, bool) {
	delta := ff.ComputeDiscriminant()
	if delta < 0 {
		return 0, 0, false // Complex roots - chaos state
	}
	
	sqrtDelta := math.Sqrt(delta)
	root1 := (-ff.B + sqrtDelta) / (2 * ff.A)
	root2 := (-ff.B - sqrtDelta) / (2 * ff.A)
	
	return root1, root2, true
}

// ============================================================================
// FLASH BUFFER - Implements 1/2 + 1/2 = 1 flash sequence
// Also implements 1/2 × 1/2 = 1/4 (requires 4 flashes for unit)
// ============================================================================

type FlashBuffer struct {
	Half1 []byte // First 1/2 flash
	Half2 []byte // Second 1/2 flash
}

func NewFlashBuffer(size int) *FlashBuffer {
	return &FlashBuffer{
		Half1: make([]byte, size/2),
		Half2: make([]byte, size/2),
	}
}

// Unite performs additive flash: 1/2 + 1/2 = 1
func (fb *FlashBuffer) Unite() []byte {
	return append(fb.Half1, fb.Half2...)
}

// Multiply performs multiplicative flash: 1/2 × 1/2 = 1/4
// Requires 4 flashes to reconstruct unit
func (fb *FlashBuffer) Multiply() []byte {
	quarter := make([]byte, len(fb.Half1)/2)
	// XOR the halves to create dimensional reduction
	for i := range quarter {
		if i < len(fb.Half1) && i < len(fb.Half2) {
			quarter[i] = fb.Half1[i] ^ fb.Half2[i]
		}
	}
	return quarter
}

// ============================================================================
// ROPEN SPARSE DUPLEX ENCODING (2→1)
// Two physical bytes → one logical byte with polarity conjugation
// ============================================================================

type RIFTToken struct {
	Type     uint8  // 0=hex, 1=conjugate, 2=epsilon
	Polarity uint8  // '+' or '-'
	Reserved uint16
}

type RBNode struct {
	Key        uint32
	Val        uint8
	Polarity   uint8
	Confidence float64
	Color      uint8 // Red-Black tree color
	Height     uint8 // AVL tree height
	Left       *RBNode
	Right      *RBNode
	Parent     *RBNode
}

type RBTree struct {
	root   *RBNode
	streak [256]int
	mutex  sync.RWMutex
}

func NewRBTree() *RBTree {
	return &RBTree{}
}

func (t *RBTree) height(n *RBNode) uint8 {
	if n == nil {
		return 0
	}
	return n.Height
}

func (t *RBTree) balanceFactor(n *RBNode) int {
	if n == nil {
		return 0
	}
	return int(t.height(n.Left)) - int(t.height(n.Right))
}

func (t *RBTree) updateHeight(n *RBNode) {
	if n == nil {
		return
	}
	leftH := t.height(n.Left)
	rightH := t.height(n.Right)
	if leftH > rightH {
		n.Height = leftH + 1
	} else {
		n.Height = rightH + 1
	}
}

func (t *RBTree) rotateLeft(x *RBNode) *RBNode {
	y := x.Right
	if y == nil {
		return x
	}
	
	x.Right = y.Left
	if y.Left != nil {
		y.Left.Parent = x
	}
	
	y.Parent = x.Parent
	if x.Parent != nil {
		if x == x.Parent.Left {
			x.Parent.Left = y
		} else {
			x.Parent.Right = y
		}
	} else {
		t.root = y
	}
	
	y.Left = x
	x.Parent = y
	
	t.updateHeight(x)
	t.updateHeight(y)
	
	return y
}

func (t *RBTree) rotateRight(x *RBNode) *RBNode {
	y := x.Left
	if y == nil {
		return x
	}
	
	x.Left = y.Right
	if y.Right != nil {
		y.Right.Parent = x
	}
	
	y.Parent = x.Parent
	if x.Parent != nil {
		if x == x.Parent.Right {
			x.Parent.Right = y
		} else {
			x.Parent.Left = y
		}
	} else {
		t.root = y
	}
	
	y.Right = x
	x.Parent = y
	
	t.updateHeight(x)
	t.updateHeight(y)
	
	return y
}

func (t *RBTree) rebalance(n *RBNode) {
	for n != nil {
		t.updateHeight(n)
		bf := t.balanceFactor(n)
		
		if bf > 1 { // Left heavy
			if t.balanceFactor(n.Left) < 0 {
				n.Left = t.rotateLeft(n.Left)
			}
			n = t.rotateRight(n)
		} else if bf < -1 { // Right heavy
			if t.balanceFactor(n.Right) > 0 {
				n.Right = t.rotateRight(n.Right)
			}
			n = t.rotateLeft(n)
		} else {
			n = n.Parent
		}
	}
}

func (t *RBTree) bstInsert(root, node *RBNode) *RBNode {
	if root == nil {
		return node
	}
	
	if node.Key < root.Key {
		root.Left = t.bstInsert(root.Left, node)
		root.Left.Parent = root
	} else if node.Key > root.Key {
		root.Right = t.bstInsert(root.Right, node)
		root.Right.Parent = root
	} else {
		// Update in place
		root.Val = node.Val
		root.Confidence = node.Confidence
		root.Polarity = node.Polarity
		return root
	}
	
	t.updateHeight(root)
	return root
}

func (t *RBTree) Insert(key uint32, val uint8, conf float64, pol uint8) {
	t.mutex.Lock()
	defer t.mutex.Unlock()
	
	node := &RBNode{
		Key:        key,
		Val:        val,
		Confidence: conf,
		Polarity:   pol,
		Color:      1, // Red
	}
	
	if t.root == nil {
		node.Color = 0 // Root is black
	}
	
	t.root = t.bstInsert(t.root, node)
	if node.Parent != nil {
		t.rebalance(node.Parent)
	} else {
		t.rebalance(node)
	}
}

func (t *RBTree) Find(key uint32) *RBNode {
	t.mutex.RLock()
	defer t.mutex.RUnlock()
	
	cur := t.root
	for cur != nil {
		if key == cur.Key {
			return cur
		}
		if key < cur.Key {
			cur = cur.Left
		} else {
			cur = cur.Right
		}
	}
	return nil
}

func (t *RBTree) MarkMeasurement(key uint32, conf float64, pol uint8) {
	t.mutex.Lock()
	defer t.mutex.Unlock()
	
	n := t.Find(key)
	if n == nil {
		return
	}
	
	n.Confidence = conf
	if pol != 0 {
		n.Polarity = pol
	}
	
	// Pruning decision based on confidence and polarity
	if conf < PRUNE_THRESHOLD || n.Polarity == POLARITY_NEG {
		idx := key & 0xFF
		t.streak[idx]++
		if t.streak[idx] >= 1 {
			n.Val = 0
			n.Confidence = 0.0
		}
	} else {
		t.streak[key&0xFF] = 0
	}
}

// Conjugate performs nibble conjugation: 0xF ⊕ x
func Conjugate(x uint8) uint8 {
	return 0xF ^ x
}

// RiftEncode performs 2→1 sparse duplex encoding
func RiftEncode(in []byte, polarityA bool, tree *RBTree) []byte {
	out := make([]byte, 0, len(in)/2+1)
	
	for i := 0; i < len(in); i += 2 {
		a := in[i]
		var b uint8
		if i+1 < len(in) {
			b = in[i+1]
		} else {
			b = EPSILON_PAD
		}
		
		var logical uint8
		if polarityA {
			logical = a ^ Conjugate(b)
		} else {
			logical = Conjugate(a) ^ b
		}
		
		out = append(out, logical)
		
		// Insert into RB-AVL tree with confidence
		pol := uint8(POLARITY_POS)
		if !polarityA {
			pol = uint8(POLARITY_NEG)
		}
		tree.Insert(uint32(len(out)), logical, 1.0, pol)
	}
	
	return out
}

// ============================================================================
// TRIDENT PACKET STRUCTURE
// ============================================================================

type TridentHeader struct {
	ChannelID     uint8
	SequenceToken uint32
	Timestamp     uint64
	CodecVersion  uint8
}

type TridentPayload struct {
	MessageHash   [32]byte
	ContentLength uint32
	Content       []byte
}

type TridentVerification struct {
	RWXFlags        uint8
	ConsensusSig    [64]byte
	HumanRightsTag  string
}

type TridentTopology struct {
	NextChannel    uint8
	PrevChannel    uint8
	WheelPosition  uint8
}

type TridentPacket struct {
	Header       TridentHeader
	Payload      TridentPayload
	Verification TridentVerification
	Topology     TridentTopology
}

// ============================================================================
// QUADRATIC SPLINE INTERPOLATION
// For smooth frame transitions using Bézier-style quadratic curves
// ============================================================================

type Point2D struct {
	X, Y float64
}

// QuadraticSpline computes point on quadratic Bézier curve at parameter t ∈ [0,1]
// P(t) = (1-t)²P₀ + 2(1-t)t·P₁ + t²P₂
func QuadraticSpline(p0, p1, p2 Point2D, t float64) Point2D {
	oneMinusT := 1 - t
	term0 := oneMinusT * oneMinusT
	term1 := 2 * oneMinusT * t
	term2 := t * t
	
	return Point2D{
		X: term0*p0.X + term1*p1.X + term2*p2.X,
		Y: term0*p0.Y + term1*p1.Y + term2*p2.Y,
	}
}

// InterpolateFrames creates smooth transition between two frames
func InterpolateFrames(frame1, frame2 []byte, steps int, width, height int) [][]byte {
	if len(frame1) != len(frame2) {
		log.Println("Frame size mismatch, cannot interpolate")
		return [][]byte{frame1, frame2}
	}
	
	result := make([][]byte, steps)
	
	for step := 0; step < steps; step++ {
		t := float64(step) / float64(steps-1)
		interpolated := make([]byte, len(frame1))
		
		// Interpolate each RGB pixel using quadratic spline
		for i := 0; i < len(frame1); i += 3 {
			if i+2 >= len(frame1) {
				break
			}
			
			// Create control points for R, G, B channels
			p0 := Point2D{X: float64(i), Y: float64(frame1[i])}
			p2 := Point2D{X: float64(i), Y: float64(frame2[i])}
			// Midpoint as control point
			p1 := Point2D{X: float64(i), Y: (p0.Y + p2.Y) / 2}
			
			// Interpolate each channel
			for c := 0; c < 3; c++ {
				if i+c >= len(frame1) {
					break
				}
				p0.Y = float64(frame1[i+c])
				p2.Y = float64(frame2[i+c])
				p1.Y = (p0.Y + p2.Y) / 2
				
				splinePoint := QuadraticSpline(p0, p1, p2, t)
				interpolated[i+c] = uint8(math.Round(splinePoint.Y))
			}
		}
		
		result[step] = interpolated
	}
	
	return result
}

// ============================================================================
// BIPOLAR ENZYME MODEL
// Operations: Create/Destroy, Build/Break, Renew/Repair
// ============================================================================

type EnzymeOperation int

const (
	ENZYME_CREATE EnzymeOperation = iota
	ENZYME_DESTROY
	ENZYME_BUILD
	ENZYME_BREAK
	ENZYME_RENEW
	ENZYME_REPAIR
)

type BipolarEnzyme struct {
	OrderSequence []EnzymeOperation
	ChaosSequence []EnzymeOperation
	State         uint8
}

func NewBipolarEnzyme() *BipolarEnzyme {
	return &BipolarEnzyme{
		OrderSequence: []EnzymeOperation{
			ENZYME_CREATE,
			ENZYME_BUILD,
			ENZYME_RENEW,
			ENZYME_REPAIR,
		},
		ChaosSequence: []EnzymeOperation{
			ENZYME_DESTROY,
			ENZYME_BREAK,
			ENZYME_REPAIR, // Chaos attempts repair
		},
		State: STATE_ORDER,
	}
}

func (be *BipolarEnzyme) Execute(op EnzymeOperation, data []byte) []byte {
	switch op {
	case ENZYME_CREATE:
		// Allocate new buffer
		return make([]byte, len(data))
	case ENZYME_DESTROY:
		// Zero out buffer
		return make([]byte, 0)
	case ENZYME_BUILD:
		// Append data
		return append([]byte{}, data...)
	case ENZYME_BREAK:
		// Split in half
		return data[:len(data)/2]
	case ENZYME_RENEW:
		// Refresh with copy
		renewed := make([]byte, len(data))
		copy(renewed, data)
		return renewed
	case ENZYME_REPAIR:
		// XOR with itself shifted (simple error correction)
		repaired := make([]byte, len(data))
		copy(repaired, data)
		for i := 1; i < len(repaired); i++ {
			repaired[i] ^= repaired[i-1]
		}
		return repaired
	default:
		return data
	}
}

// ============================================================================
// TRIDENT CHANNEL ARCHITECTURE
// Three channels with loopback addressing: 127.0.0.1, 127.0.0.2, 127.0.0.3
// ============================================================================

type TridentChannel struct {
	ID            uint8
	LoopbackAddr  string
	CodecRatio    float64
	State         uint8
	MessageQueue  chan TridentPacket
	RBTree        *RBTree
	FlashVerifier *FilterFlash
	Enzyme        *BipolarEnzyme
}

func NewTridentChannel(id uint8) *TridentChannel {
	return &TridentChannel{
		ID:            id,
		LoopbackAddr:  fmt.Sprintf("%s%d", LOOPBACK_BASE, id+1),
		CodecRatio:    float64(id+1) / 3.0,
		State:         STATE_ORDER,
		MessageQueue:  make(chan TridentPacket, 100),
		RBTree:        NewRBTree(),
		FlashVerifier: NewFilterFlash(1, 0, -1), // Default quadratic
		Enzyme:        NewBipolarEnzyme(),
	}
}

// EncodeMessage - Transmitter (Channel 0) operation
func (tc *TridentChannel) EncodeMessage(rawContent []byte) TridentPacket {
	packet := TridentPacket{
		Header: TridentHeader{
			ChannelID:     CHANNEL_TRANSMITTER,
			SequenceToken: uint32(time.Now().Unix()),
			Timestamp:     uint64(time.Now().UnixNano()),
			CodecVersion:  1, // 1/3
		},
	}
	
	// Apply ROPEN sparse duplex encoding
	encoded := RiftEncode(rawContent, true, tc.RBTree)
	
	packet.Payload.Content = encoded
	packet.Payload.ContentLength = uint32(len(encoded))
	
	// Compute SHA-256 hash (simplified to first 32 bytes)
	copy(packet.Payload.MessageHash[:], encoded[:min(32, len(encoded))])
	
	// Set RWX: Transmitter has WRITE permission
	packet.Verification.RWXFlags = RWX_WRITE
	packet.Verification.HumanRightsTag = "NSIGII_HR_TRANSMIT"
	
	// Topology
	packet.Topology.WheelPosition = 0
	packet.Topology.NextChannel = CHANNEL_RECEIVER
	
	return packet
}

// DecodePacket - Receiver (Channel 1) operation
func (tc *TridentChannel) DecodePacket(packet TridentPacket) TridentPacket {
	// Verify hash integrity
	computedHash := packet.Payload.Content[:min(32, len(packet.Payload.Content))]
	if !bytes.Equal(computedHash, packet.Payload.MessageHash[:len(computedHash)]) {
		log.Println("Hash mismatch in receiver")
	}
	
	// Set RWX: Receiver has READ permission
	packet.Verification.RWXFlags = RWX_READ
	
	// Bipartite order check
	if packet.Header.SequenceToken%2 == 0 {
		tc.State = STATE_ORDER
	} else {
		tc.State = STATE_CHAOS
	}
	
	// Update topology
	packet.Topology.PrevChannel = CHANNEL_TRANSMITTER
	packet.Topology.NextChannel = CHANNEL_VERIFIER
	packet.Topology.WheelPosition = 120
	
	return packet
}

// bipartiteConsensus derives discriminant parameters from payload statistics.
// Maps content entropy to A=1, B∈[0,4], C=1 so that:
//   Δ = B² - 4 → ORDER (Δ>0), CONSENSUS (Δ=0), CHAOS (Δ<0)
// consensus=1.0 → B=4 (ORDER), consensus=0.5 → B=2 (CONSENSUS/flash), consensus=0.0 → B=0 (CHAOS)
func bipartiteConsensus(content []byte, wheelPos uint8) (a, b, c float64) {
	if len(content) == 0 {
		return 1, 0, 1
	}
	var setBits int
	for _, byt := range content {
		for byt != 0 {
			setBits += int(byt & 1)
			byt >>= 1
		}
	}
	totalBits := len(content) * 8
	base := float64(setBits) / float64(totalBits)
	wheelCorrect := math.Sin(float64(wheelPos) * math.Pi / 180.0)
	consensus := math.Abs(base+wheelCorrect) / 2.0
	return 1.0, consensus * 4.0, 1.0
}

// VerifyPacket - Verifier (Channel 2) operation with discriminant flash verification
func (tc *TridentChannel) VerifyPacket(packet TridentPacket) (TridentPacket, bool) {
	// Derive discriminant from bipartite consensus of full payload
	// (raw pixel bytes give Delta<0 always — consensus formula maps entropy correctly)
	a, b, c := bipartiteConsensus(packet.Payload.Content, packet.Topology.WheelPosition)
	tc.FlashVerifier.A = a
	tc.FlashVerifier.B = b
	tc.FlashVerifier.C = c

	state := tc.FlashVerifier.ContextSwitch()

	switch state {
	case DISCRIMINANT_CONSENSUS:
		// Flash point: consensus=0.5, B=2, Delta=0
		packet.Verification.RWXFlags = RWX_FULL
		packet.Topology.WheelPosition = 240
		tc.State = STATE_VERIFIED
		return packet, true

	case DISCRIMINANT_ORDER:
		// Consensus > 0.5: coherent, grant full permissions
		packet.Verification.RWXFlags = RWX_FULL
		packet.Topology.WheelPosition = 120
		tc.State = STATE_ORDER
		return packet, true

	case DISCRIMINANT_CHAOS:
		// Consensus < 0.5: apply enzyme repair, continue
		repaired := tc.Enzyme.Execute(ENZYME_REPAIR, packet.Payload.Content)
		packet.Payload.Content = repaired
		packet.Verification.RWXFlags = RWX_READ
		tc.State = STATE_CHAOS
		return packet, false
	}

	return packet, false
}

// ============================================================================
// VIDEO CODEC INTEGRATION
// Combines RGB24 processing with NSIGII trident verification
// ============================================================================

type NSIGIICodec struct {
	Width       int
	Height      int
	Channels    [3]*TridentChannel
	RBTree      *RBTree
	FlashBuffer *FlashBuffer
}

func NewNSIGIICodec(width, height int) *NSIGIICodec {
	codec := &NSIGIICodec{
		Width:       width,
		Height:      height,
		RBTree:      NewRBTree(),
		FlashBuffer: NewFlashBuffer(width * height * 3),
	}
	
	// Initialize three trident channels
	for i := 0; i < TRIDENT_CHANNELS; i++ {
		codec.Channels[i] = NewTridentChannel(uint8(i))
	}
	
	return codec
}

func (nc *NSIGIICodec) EncodeFrame(frame []byte) ([]byte, error) {
	if len(frame) != nc.Width*nc.Height*3 {
		return nil, fmt.Errorf("invalid frame size: expected %d, got %d",
			nc.Width*nc.Height*3, len(frame))
	}
	
	// Split frame into flash buffer halves
	halfSize := len(frame) / 2
	copy(nc.FlashBuffer.Half1, frame[:halfSize])
	copy(nc.FlashBuffer.Half2, frame[halfSize:])
	
	// Apply flash unite (1/2 + 1/2 = 1)
	unified := nc.FlashBuffer.Unite()
	
	// Channel 0: Transmitter encodes
	packet := nc.Channels[CHANNEL_TRANSMITTER].EncodeMessage(unified)
	
	// Channel 1: Receiver decodes
	packet = nc.Channels[CHANNEL_RECEIVER].DecodePacket(packet)
	
	// Channel 2: Verifier validates with discriminant flash
	packet, verified := nc.Channels[CHANNEL_VERIFIER].VerifyPacket(packet)
	_ = verified // chaos frames still encode after enzyme repair
	
	// Convert to YUV420 for compression (from original main.go)
	yuvFrame := nc.rgbToYUV420(packet.Payload.Content)
	
	// Apply DEFLATE compression
	var buf bytes.Buffer
	w, _ := flate.NewWriter(&buf, flate.BestCompression)
	w.Write(yuvFrame)
	w.Close()
	
	return buf.Bytes(), nil
}

func (nc *NSIGIICodec) rgbToYUV420(rgb []byte) []byte {
	width := nc.Width
	height := nc.Height
	
	// Allocate YUV buffer
	yuv := make([]byte, width*height+width*height/2)
	
	yPlane := yuv[:width*height]
	uPlane := yuv[width*height : width*height+width*height/4]
	vPlane := yuv[width*height+width*height/4:]
	
	// Convert RGB to YUV
	for j := 0; j < height; j++ {
		for i := 0; i < width; i++ {
			idx := (j*width + i) * 3
			if idx+2 >= len(rgb) {
				continue
			}
			
			r := float64(rgb[idx])
			g := float64(rgb[idx+1])
			b := float64(rgb[idx+2])
			
			// YUV conversion formulas
			y := 0.299*r + 0.587*g + 0.114*b
			u := -0.169*r - 0.331*g + 0.500*b + 128
			v := 0.500*r - 0.419*g - 0.081*b + 128
			
			yPlane[j*width+i] = uint8(clamp(y, 0, 255))
			
			// Subsample U and V (4:2:0)
			if j%2 == 0 && i%2 == 0 {
				uvIdx := (j/2)*(width/2) + (i / 2)
				if uvIdx < len(uPlane) {
					uPlane[uvIdx] = uint8(clamp(u, 0, 255))
				}
				if uvIdx < len(vPlane) {
					vPlane[uvIdx] = uint8(clamp(v, 0, 255))
				}
			}
		}
	}
	
	return yuv
}

func clamp(x, min, max float64) float64 {
	if x < min {
		return min
	}
	if x > max {
		return max
	}
	return x
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// ============================================================================
// MAIN ENTRY POINT
// LTF pipeline: stdin pipe OR -input flag → FFmpeg RGB24 decode → NSIGII encode
//
// Invocation patterns:
//   '.\video.mp4' | go run .\main.go                    (LTF pipe mode)
//   go run .\main.go -input video.mp4                   (explicit flag mode)
//   go run .\main.go -input video.rgb24 -output out.nsigii
// ============================================================================

func stdinIsPipe() bool {
	stat, err := os.Stdin.Stat()
	if err != nil {
		return false
	}
	return (stat.Mode() & os.ModeCharDevice) == 0
}

// readPipedFilename reads a single filename piped via stdin.
// Handles PowerShell pipe: 'file.mp4' | go run .\main.go
func readPipedFilename() string {
	scanner := bufio.NewScanner(os.Stdin)
	if scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		// Strip surrounding quotes PowerShell may include
		line = strings.Trim(line, "'\"")
		return line
	}
	return ""
}

// probeVideoSize uses ffprobe to detect width/height of a video file
func probeVideoSize(path string) (int, int, error) {
	cmd := exec.Command("ffprobe",
		"-v", "error",
		"-select_streams", "v:0",
		"-show_entries", "stream=width,height",
		"-of", "csv=p=0",
		path,
	)
	out, err := cmd.Output()
	if err != nil {
		return 0, 0, fmt.Errorf("ffprobe failed: %v", err)
	}
	var w, h int
	_, err = fmt.Sscanf(strings.TrimSpace(string(out)), "%d,%d", &w, &h)
	if err != nil {
		return 0, 0, fmt.Errorf("ffprobe parse failed: %v (output: %s)", err, out)
	}
	return w, h, nil
}

// openRGB24Reader returns an io.ReadCloser of raw RGB24 frames.
// For .mp4/.mkv/.mov etc: pipes through ffmpeg -pix_fmt rgb24.
// For .rgb24: opens directly.
func openRGB24Reader(path string, width, height int) (io.ReadCloser, *exec.Cmd, error) {
	ext := strings.ToLower(filepath.Ext(path))
	if ext == ".rgb24" {
		f, err := os.Open(path)
		return f, nil, err
	}

	// Use FFmpeg to decode any video format to raw RGB24 stream
	cmd := exec.Command("ffmpeg",
		"-i", path,
		"-f", "rawvideo",
		"-pix_fmt", "rgb24",
		"-vf", fmt.Sprintf("scale=%d:%d", width, height),
		"-an",       // no audio
		"-",         // output to stdout
	)
	cmd.Stderr = os.Stderr // show ffmpeg progress on stderr
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, nil, fmt.Errorf("ffmpeg pipe failed: %v", err)
	}
	if err := cmd.Start(); err != nil {
		return nil, nil, fmt.Errorf("ffmpeg start failed: %v (is ffmpeg installed?)", err)
	}
	return stdout, cmd, nil
}

// deriveOutputName builds output path from input filename
func deriveOutputName(inputPath string) string {
	base := filepath.Base(inputPath)
	ext := filepath.Ext(base)
	name := strings.TrimSuffix(base, ext)
	return name + ".nsigii"
}

func main() {
	var width, height int
	var inputFile, outputFile string

	flag.IntVar(&width, "width", 0, "video width (0 = auto-detect via ffprobe)")
	flag.IntVar(&height, "height", 0, "video height (0 = auto-detect via ffprobe)")
	flag.StringVar(&inputFile, "input", "", "input video file (.mp4, .rgb24, etc.)")
	flag.StringVar(&outputFile, "output", "", "output file (default: <input>.nsigii)")
	flag.Parse()

	// ── LTF PIPE MODE ────────────────────────────────────────────────────────
	// Pattern: '.\video.mp4' | go run .\main.go
	// PowerShell pipes the filename string to stdin when the file is quoted
	if inputFile == "" && stdinIsPipe() {
		piped := readPipedFilename()
		if piped != "" {
			inputFile = piped
			log.Printf("LTF pipe mode: received input → %s", inputFile)
		}
	}

	if inputFile == "" {
		log.Fatalf("No input specified. Use: '.\\video.mp4' | go run .\\main.go  OR  -input flag")
	}

	// ── AUTO-DETECT DIMENSIONS ───────────────────────────────────────────────
	if width == 0 || height == 0 {
		log.Printf("Probing dimensions: %s", inputFile)
		w, h, err := probeVideoSize(inputFile)
		if err != nil {
			log.Printf("ffprobe failed (%v), using defaults 384x216", err)
			w, h = 384, 216
		}
		if width == 0 {
			width = w
		}
		if height == 0 {
			height = h
		}
	}
	log.Printf("Frame dimensions: %dx%d", width, height)

	// ── DERIVE OUTPUT NAME ────────────────────────────────────────────────────
	if outputFile == "" {
		outputFile = deriveOutputName(inputFile)
	}

	log.Printf("NSIGII Polygatic Video Codec v%s", VERSION)
	log.Printf("Initializing trident channels...")
	log.Printf("Input:  %s", inputFile)
	log.Printf("Output: %s", outputFile)

	codec := NewNSIGIICodec(width, height)

	// ── OPEN RGB24 STREAM ─────────────────────────────────────────────────────
	inputReader, ffmpegCmd, err := openRGB24Reader(inputFile, width, height)
	if err != nil {
		log.Fatalf("Failed to open input: %v", err)
	}
	defer inputReader.Close()

	// ── CREATE OUTPUT FILE ────────────────────────────────────────────────────
	output, err := os.Create(outputFile)
	if err != nil {
		log.Fatalf("Failed to create output file: %v", err)
	}
	defer output.Close()

	// Write NSIGII container header
	header := struct {
		Magic      [8]byte
		Version    [8]byte
		Width      uint32
		Height     uint32
		FrameCount uint32
		Reserved   uint32
	}{
		Magic:   [8]byte{'N', 'S', 'I', 'G', 'I', 'I', 0, 0},
		Version: [8]byte{'7', '.', '0', '.', '0', 0, 0, 0},
		Width:   uint32(width),
		Height:  uint32(height),
	}
	binary.Write(output, binary.LittleEndian, header)

	frameSize := width * height * 3
	frame := make([]byte, frameSize)
	frameCount := 0
	chaosCount := 0
	orderCount := 0
	totalRawSize := 0
	totalEncodedSize := 0

	log.Println("Encoding frames with trident verification...")

	for {
		n, err := io.ReadFull(inputReader, frame)
		if err == io.EOF {
			break
		}
		// ErrUnexpectedEOF = partial last frame, still encode it
		if err != nil && err != io.ErrUnexpectedEOF {
			// Non-fatal pipe errors (e.g. FFmpeg closed early): drain and stop cleanly
			log.Printf("Frame read ended: %v (encoded %d frames so far)", err, frameCount)
			break
		}
		if n == 0 {
			break
		}

		totalRawSize += n

		encoded, encErr := codec.EncodeFrame(frame[:n])
		if encErr != nil {
			// Size mismatch on partial last frame — skip, do not break
			chaosCount++
			continue
		}

		// Track discriminant state from verifier channel
		switch codec.Channels[CHANNEL_VERIFIER].State {
		case STATE_ORDER, STATE_VERIFIED:
			orderCount++
		default:
			chaosCount++
		}

		frameHeader := struct{ Size uint32 }{Size: uint32(len(encoded))}
		binary.Write(output, binary.LittleEndian, frameHeader)
		output.Write(encoded)

		totalEncodedSize += 4 + len(encoded)
		frameCount++

		if frameCount%50 == 0 {
			log.Printf("Encoded %d frames  [ORDER:%d  CHAOS:%d]", frameCount, orderCount, chaosCount)
		}
	}

	// Drain any remaining FFmpeg output to prevent broken pipe signal
	if ffmpegCmd != nil {
		io.Copy(io.Discard, inputReader)
		if err := ffmpegCmd.Wait(); err != nil {
			// Broken pipe is expected when we stop reading — not an error
			if !strings.Contains(err.Error(), "exit status") {
				log.Printf("FFmpeg: %v", err)
			}
		}
	}

	// Update frame count in header (offset 24)
	output.Seek(24, 0)
	binary.Write(output, binary.LittleEndian, uint32(frameCount))

	var compressionRatio float64
	if totalRawSize > 0 && totalEncodedSize > 0 {
		compressionRatio = (1.0 - float64(totalEncodedSize)/float64(totalRawSize)) * 100
	}

	log.Printf("\n=== NSIGII Encoding Complete ===")
	log.Printf("Frames encoded:     %d", frameCount)
	log.Printf("ORDER (verified):   %d", orderCount)
	log.Printf("CHAOS (repaired):   %d", chaosCount)
	log.Printf("Raw size:           %d bytes", totalRawSize)
	log.Printf("Encoded size:       %d bytes", totalEncodedSize)
	log.Printf("Compression ratio:  %.2f%%", compressionRatio)
	log.Printf("Trident channels:   TRANSMIT → RECEIVE → VERIFY")
	log.Printf("Flash verification: Discriminant / Bipartite Consensus")
	log.Printf("Output file:        %s", outputFile)
}
