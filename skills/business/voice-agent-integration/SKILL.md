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

## Decision: cascade, and say why in one line

Use a staged pipeline (**VAD → STT → the existing LLM with tools → TTS**) unless the request is
literally "entertain me with a duplex demo". For an agent that answers from a client's data the reasons
are decisive:

- Tool calling and retrieval stay deterministic and auditable — you can log what was retrieved and why.
- The agent keeps one source of truth; voice becomes input and output, not a second brain.
- Open end-to-end duplex models that speak Spanish are either nonexistent or **base models without
  instruction following or tool calling**. The good ones with native tool calling are English/Chinese.

Sell a session layer that abstracts the model so the front end can be swapped later without touching the
RAG.

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

## Validation gates before the commercial promise

Agree the thresholds with the client up front, then measure: word error rate in their environment, name
accuracy on their own list, dialect retention, hallucination rate in silence, mean opinion score on the
voice with a handful of listeners, and p95 latency over the real transport. A module that fails one gate
is a pilot with a fix list, not a delivery.
