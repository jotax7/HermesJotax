---
name: voice-note-transcription
description: "Transcribe voice notes locally with faster-whisper (no API)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [transcription, whisper, audio, telegram, voice]
    category: media
---

# Voice note transcription (local, no API)

## When to Use

Load this when the user sends a voice message that arrives untranscribed (`.ogg` / `.mp3` / `.m4a`
path in the message), or asks you to transcribe, summarize, or act on an audio clip.

Telegram voice messages sometimes arrive untranscribed as an `.ogg` file. Transcribe locally with
`faster-whisper` — no API key, works offline, ~1 min of CPU per minute of audio on a Pi 5.

## Recipe

```bash
# 1. decode to 16 kHz mono PCM (faster-whisper wants a flat array, see pitfall below)
ffmpeg -y -v error -i "$SRC" -ar 16000 -ac 1 -c:a pcm_s16le voice.wav
```

```python
# 2. transcribe (run with the venv that has faster-whisper installed)
import wave, numpy as np
from faster_whisper import WhisperModel

w = wave.open("voice.wav")
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype("float32") / 32768.0

m = WhisperModel("small", device="cpu", compute_type="int8")   # medium for proper nouns
segs, info = m.transcribe(a, language="es", vad_filter=True, beam_size=5)
for s in segs:
    print(f"[{s.start:.1f}] {s.text.strip()}")
```

Install once: `pip install faster-whisper numpy` (ffmpeg must be on PATH; Hermes bundles one under
`~/.hermes/tools/ffmpeg-*`).

## Choosing the model

| Content | Model | Flags |
|---|---|---|
| Normal speech, summary | `small` | `vad_filter=True, beam_size=5` |
| Names, emails, addresses, technical terms | `medium` | `vad_filter=False, beam_size=8, condition_on_previous_text=False, temperature=0.0` |

`medium` is ~4-5x slower but is what recovers spelled-out addresses. On a short 12 s clip it is
worth just using `medium` from the start when the message likely contains contact data.

## Pitfalls

- **`decode_audio` raises `TypeError: open() got an unexpected keyword argument 'metadata_errors'`**
  — newer `av`/PyAV dropped that kwarg. Pass a numpy array (as above) instead of a file path.
- **Emails and proper nouns get mangled by `small`.** If a transcription contains something that
  looks like a contact, re-run with `medium` before guessing; if still unclear, ask the user to
  spell it out or send a screenshot. Never reconstruct an address from a bad transcription.
- **The user may already have spelled it out.** "ce de corta doble ene manuel arroba gimeil punto com"
  is a dictated email, not noise — transcribe it and confirm with the user, do not assume it failed.
- First run downloads model weights from Hugging Face (needs network, prints an "unauthenticated
  requests" warning — harmless).
- Long audio: run in background (`timeout_s` over 600 s becomes background automatically) and poll.

## After transcribing

Give the user the transcription verbatim, then act on the request it contains. If the note is
material for the Drive (see the `ESTADO` folder convention in the BoulderTech workflow), archive
the original audio plus the structured note.
