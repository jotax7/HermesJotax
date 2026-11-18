---
name: voice-agent-integration
description: "Add a voice interface to an existing AI agent, self-hosted."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [voice, speech, stt, tts, agents, self-hosted, latency]
    related_skills: [commercial-proposal-pricing, market-research]
    category: business
---

# Voice on top of a knowledge agent

## When to Use

- A client who already has a working text agent asks to talk to it and hear it answer.
- Scoping, prototyping or costing a voice channel for an enterprise assistant.
- Someone asks which open-source speech-to-speech model to use.

## Decision: match the requirement's own wording first

Before choosing an architecture, find the word the buyer uses for the capability — *bidireccional*,
*tiempo real*, *full-duplex*, *conversacional*. That word is the acceptance criterion whether or not it is
technically precise, and a model that does not match it gets rejected even when it is the better product.
Two different things hide behind it:

| Sense | What it means | Worth for a Q&A agent |
|---|---|---|
| Audio in **and** audio out in one model | A conversation of turns, streaming output | **This is the requirement** |
| Simultaneous duplex | Speaking while listening | ~None: the user asks, waits, listens |

Satisfy the word if a model that satisfies it exists. If none does, make the trade-off the **subject of a
section in the document** — define both senses in a table, state which one the project delivers, argue why
the other adds nothing here. A buyer who discovers the gap on his own kills the deal; a buyer who reads it
in section 2 with an argument attached signs.

For an agent that answers from a client's data, a staged pipeline (**VAD → STT → the existing LLM with
tools → TTS**) or a turn-based omni model both beat a duplex model on the merits:

- Tool calling and retrieval stay deterministic and auditable — you can log what was retrieved and why.
- The agent keeps one source of truth; voice becomes input and output, not a second brain.
- **No open duplex model combines Spanish with tool calling.** The duplex ones that call tools are English
  (Nemotron VoiceChat); the one that speaks Spanish is a base model with no instruction following and no
  tools (Haru-4B). Check `references/model-inventory.md` for the current table.
- A duplex model that cannot call tools still serves the agent through a **frontend/backend split**: the
  duplex model holds the conversation and emits a delegation token plus the transcript, the existing agent
  runs the RAG and the tools, and the answer is fed back for the duplex model to speak. Only reach for it
  when the buyer's word is non-negotiable; otherwise the turn-based path is less work for the same result.
  The recipe is in `references/model-inventory.md`.

Sell a session layer that abstracts the model so the front end can be swapped later without touching the
RAG.

**When the user overrides your pick, defend his pick.** He knows the account and the buyer; you know the
models. Write the document around his choice, state the one risk that could cost money or credibility
*once*, then drop it — re-opening it next turn is friction, not diligence.

## Procedure

1. **Prototype on the reference pipeline before writing anything.** `huggingface/speech-to-speech`
   (Apache-2.0) ships the cascade with an OpenAI-Realtime-compatible server, every stage swappable. Replace
   its LLM with the client's agent. Half a day, and it gives you real latency numbers.
2. **Record the client's own audio, not benchmark clips.** 200-300 real utterances from their environment
   (counter, corridor, phone) with double human reference. The whole point is their vocabulary.
3. **Measure with the right metric.** Overall WER is misleading: **error on proper nouns (locations, brands,
   people) runs 3-4× the headline WER**. Track a name-error rate separately over the client's own list.
4. **Choose STT and TTS per language, not per leaderboard.** A model with slightly worse average WER but
   real streaming beats one that has to wait for the end of the sentence.
5. **Measure latency with the real transport**, p50 and p95 — never on localhost only.
6. **Test interruption behaviour explicitly**: count how many times an "ok" said over the agent got
   committed to the context as agreement. It is the failure users notice and the one defaults get wrong.
7. **Only then quote it.** Add the voice module as a separate, named line with its own caps. The pricing
   shape (own vs rent, break-even, licence traps) lives in the `commercial-proposal-pricing` skill.

## Stack to start from (check the licence of *outputs*, not just the weights)

| Layer | Starting point | Why |
|---|---|---|
| VAD / turn | Silero VAD (short silence threshold) + a turn-end classifier | Cheap, and it sets how the conversation feels |
| STT | A streaming multilingual ASR with Spanish in its training mix | Streaming matters more than 0.3 points of WER |
| LLM | The client's existing agent | One source of truth |
| TTS | A permissively licensed model with streaming and a Spanish voice | Clone from the client's own consented recording if they want a brand voice |
| Orchestration | Pipecat (or LiveKit when the audio is WebRTC) | Handles barge-in, cancellation and commit semantics |

Never hardcode a model name into the proposal. Name the layer and the criteria; the checkpoint changes
every quarter.

## Latency budget to quote

- **Stages local and colocated: ~0.75-1.0 s** to first audio. This is what an on-premise deployment buys.
- **Stages as hosted providers over the network: 2.5-3.1 s p50** — measured for the same architecture.
  Transport and endpointing dominate, not model size, so never promise sub-second with a hosted chain.
- **A tool call adds ~0.9-1.1 s.** Budget it, or start speaking a holding line while the tool runs.

## Pitfalls

- **Prompt-based hotwords collapse at scale.** Listing a hundred location names in a prompt degrades
  recognition; a bias list applied to the top candidates plus fuzzy correction against the catalog is what
  works. Test with the client's full list before promising name accuracy.
- **Models normalise dialect.** Regional forms (voseo and the like) get flattened; naming the dialect in the
  prompt recovers most of it. Verify the retention rate, do not assume it.
- **Code-switching is where open models break.** Business Spanish mixes English jargon (dashboard, ticket,
  POI) and some STT models translate instead of transcribing when they detect the mix. Test with those
  sentences explicitly.
- **Barge-in is a context problem, not an audio problem.** Cutting playback is the easy half; deciding what
  gets committed to the conversation when the user talks over the agent is the half that produces wrong
  answers. Review it in code, not by ear.
- **Telephone audio is 8 kHz**, browser audio is 16 kHz. Accuracy measured on a headset demo does not carry
  over to a real call.
- **Do not promise a voice module as "included" in an existing fee.** It carries real variable cost per
  minute and real maintenance; price it as its own line.
- **Buying a GPU for voice alone rarely pays.** Below a few thousand conversations a month the box idles;
  ride on the server the text product already uses.
- **Check the hardware floor before quoting a single model.** A 30B omni model reports around 79 GB of GPU
  memory in BF16 — more than most client servers carry — and ~20 GB only after int4 quantisation. A
  proposal that assumes "it runs on their existing server" without an audit puts the whole setup fee at
  risk: make the audit a paid, dated phase with a written go/no-go, and put the VRAM requirement in the
  client's responsibilities, not in a supuestos paragraph.
- **One model is not a smaller project than three.** A single omni model removes the STT/TTS glue and adds
  a serving stack, quantisation-quality risk and a VRAM floor. Price it as integration plus a technical
  gate, never as "fewer moving parts".
- **Model cards overstate scope.** Verify that "supports tool calling" was tested with *audio* input and
  that a language list for text also applies to generated speech. Reading the card is not testing it.

## Validation gates before the commercial promise

Agree the thresholds with the client up front, then measure: word error rate in their environment, name
accuracy on their own list, dialect retention, hallucination rate in silence, mean opinion score on the
voice with a handful of listeners, and p95 latency over the real transport. A module that fails one gate
is a pilot with a fix list, not a delivery.

## References

- `references/model-inventory.md` — open speech-to-speech models with duplex / Spanish / tool-calling /
  licence / VRAM / latency, plus the benchmark picture for Spanish.
