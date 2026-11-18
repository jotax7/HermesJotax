# Open speech-to-speech models — selection table

Verified around November 2026. Re-check licences and numbers before quoting: this market moves monthly.

## The three questions that decide it

1. Does it produce **speech output in Spanish** (not just understand Spanish)?
2. Does it execute **tool calls natively** — from audio, not just from text?
3. Is the **licence** usable commercially for weights *and* outputs?

Almost no open model answers all three. Say which one fails and why, instead of ranking by vibes.

## Full-duplex (speaks while listening)

| Model | Languages | Tools | Weights / licence | VRAM | Notes |
|---|---|---|---|---|---|
| Nemotron VoiceChat 11B (NVIDIA) | **English only** | **Yes, native** — first open duplex model with tool calling | OpenMDW-1.1, commercial | ~22 GB | The best duplex architecture; unusable for a Spanish client |
| Haru-4B (higurashi) | **9, Spanish among them** | **No** | Apache-2.0 | ~12 GB | 7.5 Hz, 133 ms frames, ~65 ms p50 on an M1 Max int8. Released as a **base model**: its own card says it is not a reliable fact source and does not follow instructions. Needs SFT before it can be an agent |
| Moshi (Kyutai) | English | No | CC-BY-4.0 / Apache | 24 GB | Historic reference, ~200 ms on an L4 |
| PersonaPlex (NVIDIA) | English | No | NVIDIA Open Model | ~17 GB | Voice and persona, ~170 ms to interruption |
| MiniCPM-o 4.5 | English / Chinese | Not documented | Apache-2.0 | 19 GB (12 GB streaming) | Lightest of the duplex set |
| DuplexOmni / XDuplexOmni | Chinese / English | Yes, extra reasoning layer | Apache-2.0 | 8× H20 | Hardware floor rules it out |

## Turn-based omni (audio in, audio out, one model)

| Model | Languages | Tools | Weights / licence | VRAM | Notes |
|---|---|---|---|---|---|
| **Qwen3-Omni 30B-A3B** | Speech in 19, **speech out 10 including Spanish** | **Yes, function calling over audio** | Apache-2.0, commercial | ~20 GB in int4; BF16 needs ~79 GB | MoE (30B total, ~3B active) + Thinker/Talker. TTFP ~0.93 s on vLLM-Omni. **Not duplex** — turns with streaming. Say so explicitly |

Its successor line shipped API-only, so fix the checkpoint version in the contract and keep the weights
on the client's infrastructure.

## Cascade (VAD → STT → agent → TTS)

Still the most controllable option and the only one where you can measure each stage separately. Reference
implementation: `huggingface/speech-to-speech` (Apache-2.0) — but note its own README says it is **not
full-duplex out of the box**: it is a turn-taking loop.

- **VAD / turn end**: Silero VAD (MIT) plus a turn-end classifier (Apache).
- **STT**: a streaming multilingual ASR with Spanish in the mix. Streaming beats a fraction of a WER point.
- **TTS**: a permissive model with streaming and a Spanish voice (Qwen3-TTS, CosyVoice 3, Gepard 1.0).
  **Check the licence of the outputs, not only the weights** — some popular clone models forbid commercial
  use of generated audio.
- **Orchestration**: Pipecat, or LiveKit when the audio is WebRTC.

## When the buyer insists on duplex and the agent needs tools

No open duplex model calls tools in Spanish, so having both is a **split**, not a model choice:

1. The duplex model holds the conversation and, when a question needs data, emits a delegation token
   while it keeps talking (small talk, a holding phrase).
2. The existing agent receives the transcript and runs the RAG and the tools.
3. The answer comes back and the duplex model speaks it in its own voice, without dropping the turn.

This is the published frontend/backend pattern for tool calls in full-duplex speech models. Price it as
extra R&D, not as integration: the only duplex model with Spanish ships as a base model, so it also needs
supervised fine-tuning (a few thousand question-answer pairs from the client's own corpus) before it
behaves as an assistant. Weeks, not days — and keep the turn-based path as the documented fallback.

## Benchmark reality for Spanish

- **There is no dedicated full-duplex benchmark in Spanish.** The field's own benchmark map says so
  explicitly for Spanish, Portuguese, French, German, Russian and Korean.
- The only Spanish duplex evidence comes from a multilingual voice-agent benchmark over commercial systems:
  Spanish lands within ~3 points of English on task completion, and it evaluated **no open-weight model**.
- Consequence: Spanish quality of any open model is something **you measure** on the client's own audio.
  Make that measurement the first paid phase, not the last.

## Naming rule for documents

Never hardcode a checkpoint as "the architecture". Name the layer and the criteria, then name the current
checkpoint as *the reference implementation we validated*, with the version pinned. The checkpoint changes
every quarter; the integration and the agent do not.
