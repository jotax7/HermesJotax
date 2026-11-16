---
name: bouldertech-estado-intake
description: "File raw work inputs into Drive ESTADO and update index."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [bouldertech, drive, intake, estado, workflow]
    related_skills: [google-workspace, voice-note-transcription]
    category: productivity
---

# BoulderTech ESTADO intake

## When to Use

Load when Joaco (jshaw@bouldertech.fi) sends work material out of band — a voice note, photo,
screenshot, loose text, PDF, or link about BoulderTech — and expects it filed properly, or when he asks
what the current business state is, or when a claim he makes contradicts a document in Drive.

## The convention (agreed 14/11/2026)

He sends material in any format; we structure it. Drive is the source of truth, not the chat.

- **Folder:** `BOULDER TECH / ESTADO` — id `1MKqV3b7L9PeFzduspR1HZVLnsPm9i6YY`
  (parent `BOULDER TECH ` — note the trailing space — id `1AAYDdtahUC2eLtYPvhQls37TAXs8WM77`)
- **Index doc:** "Estado del negocio (indice)" — id `1J5beIfVHv3xGtoME75o_e7rf_g_tgANbXtym_kbrrQQ`
  Six blocks: pricing · clientes en producción · producto · comercial · trabas de hoy · métricas.

## Procedure

1. **Capture the raw input.** Voice note → transcribe (`voice-note-transcription` skill, `medium` model
   when names/emails appear). Image → read it. Document → extract text. Never paraphrase away the source.
2. **Archive the raw file** in the `ESTADO` folder with a dated name (`2026-11-14 — <tema>`), so the
   original is never lost.
3. **Create or update the structured note** with the extracted facts, each one tied to its source.
4. **Update the index doc.** Replace the placeholder in the right block; do not duplicate the note.
5. **Reply with the link** and state exactly what changed.

Use `/home/bldt/.hermes/venvs/google/bin/python` with `google_api.py` / the API for all of this — the
Hermes python lacks the Google libs.

## Rules that matter

- **The index wins conflicts.** If a new datum contradicts another Drive document, the index is
  correct and the other doc gets corrected or archived. Example found in practice: the "rueda
  comercial" says 12 clients in production, the September whitepaper says 6.
- **Never invent a figure to fill a placeholder.** Leave `pendiente` and ask; a wrong number in the
  source of truth is worse than a gap.
- **Flag stale documents explicitly.** Docs that describe an abandoned stack (e.g. `CLAUDE TRASPASO`
  still presenting OpenClaw as the orchestrator) are active liabilities in a due diligence — say so.
- Dates in these documents are the fastest way to catch bad advice: a roadmap built on a folder that
  reflects October is wrong in November. Check the newest item before recommending anything.

## Known gaps to watch

- Emails and proper nouns are the one thing local transcription mangles — ask for the address typed
  out rather than reconstructing it.
- Some Drive docs export empty or 500 on first attempt (`PROYECTO RETAIL`, `mensaje a prospectos`,
  `GRUPO MASRI NOTAS`); retry once before reporting them as missing.
