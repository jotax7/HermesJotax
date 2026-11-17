# Cascada de voz open source en tiempo real — estado del arte, noviembre 2026

Alcance: agente de conocimiento self-hosted, español, RAG + tool calling, objetivo < 1,5 s hasta el primer audio. Cada latencia lleva hardware y tipo de estadístico (p50/p95); donde no hay dato publicado dice **no verificado**.

## 0. Veredicto

- La cascada sigue siendo la única arquitectura self-hosted de producción. El tutorial de Salesforce mide 755 ms de time-to-first-audio (mejor caso 729 ms) con function calling completo, contra ~146 s del único speech-to-speech open que corre 100 % local (Qwen3-Omni en Transformers, 1×H200).[1]
- El proyecto de ~13,7 mil estrellas que tenías en el radar es exactamente eso: `huggingface/speech-to-speech`, 13.706 estrellas, Apache-2.0, pipeline por defecto Silero VAD → Parakeet TDT → Qwen3.5-4B → Qwen3-TTS, servidor compatible OpenAI Realtime por WebSocket y WebRTC.[41]
- La trampa del < 1,5 s no es el modelo: es el *endpointing* y el transporte. Con el stack hosteado por defecto (Deepgram + gpt-4.1-mini + ElevenLabs) sobre red, un estudio en español mide 2.616 ms p50 en Pipecat y 3.090 ms p50 en LiveKit.[2] Con las mismas etapas locales y colocalizadas el mismo tipo de cascada baja a 0,75–1,0 s.[1][46]
- Una sola GPU de 24–32 GB alcanza para STT + LLM 4B + TTS en bf16 (≈16 GB de pesos sumados). Para concurrencia real, 48 GB.

## 1. STT comparado

| Modelo | Licencia | Idiomas (español) | Streaming | WER reportado (benchmark) | Latencia medida | Pesos / VRAM | Runtime recomendado |
|---|---|---|---|---|---|---|---|
| **Qwen3-ASR-0.6B** | Apache-2.0[5] | 30 idiomas + 22 dialectos chinos; es incluido[5] | Unificado streaming/offline, por chunks (ventana flash-attn 1–8 s)[6] | Promedio multilingüe FLEURS 7,57 % (30 idiomas); **español específico no publicado en la card**; 3,0 % en español según medición de terceros en MLX[49] | TTFT p50 92 ms / p95 105 ms con concurrencia 1, vLLM 0.14 + CUDA graphs, GPU no especificada ("single typical compute resource")[6] | 1,9 GB en disco[5] | vLLM 0.14+, Transformers ≥5.13[5] |
| **Qwen3-ASR-1.7B** | Apache-2.0[4] | ídem[4] | ídem[6] | FLEURS multilingüe 4,90 %[4]; Open ASR Leaderboard mean 5,59 % (26/06/2026)[5] | TTFT p50 102 ms / p95 113 ms, conc. 1, vLLM, misma salvedad de hardware[6] | 4,7 GB[4] | vLLM, Transformers[4] |
| **Nemotron 3.5 ASR Streaming 0.6B** | OpenMDW-1.1[7] | 40 locales; es-US y es-ES en el tier "transcription-ready"[7] | **Streaming nativo** cache-aware FastConformer-RNNT, chunks 80/160/320/560/1120 ms[7] | FLEURS-es: 4,87 / 4,64 / 4,39 / 4,26 / 4,11 % (LangID); 5,04 / 4,82 / 4,48 / 4,34 / 4,13 % (auto-detect)[7] | TTFS p50 236 ms / p95 253 ms / p99 266 ms (Pipecat, self-hosted, 1.000 clips en inglés)[3] | 2,55 GB[7] | NeMo 3.x, NeMo-Speech.cpp (GGUF q8), Transformers[7] |
| **Nemotron Speech Streaming EN 0.6B** | NVIDIA Open Model License[8] | Solo inglés[8] | Streaming nativo, 80–1120 ms[8] | LibriSpeech clean 2,32 % / other 4,84 % con frame 1,12 s[8] | no verificado | 2,5 GB | NeMo[8] |
| **Parakeet TDT 0.6B v3** | CC-BY-4.0[9] | 25 idiomas europeos; es incluido[9] | **No streaming** (offline / long-form hasta 24 min)[9] | FLEURS-es 3,45 % (es_419)[9]; RTFx mediana 151,7 en RTX 3090 24 GB, batch offline[19] | no hay TTFS publicado; en la práctica agrega el costo de cierre de turno | 2,5 GB[9] | NeMo, nano-parakeet, Transformers[41] |
| **Voxtral Mini 4B Realtime 2602** | Apache-2.0[10] | 13 idiomas; es incluido[10] | **Streaming nativo**, delay configurable 80 ms–2,4 s[10] | FLEURS-es: 3,31 % @480 ms, 2,98 % @960 ms, 4,59 % @240 ms[10] | TTFS p50 525 ms / p95 973 ms / p99 1.913 ms (servicio hosteado, Pipecat, inglés)[3] | 17,7 GB bf16; corre en GPU ≥16 GB[10] | **solo vLLM** por ahora[10] |
| **Voxtral Small 24B (2507)** | Apache-2.0[11] | 8 idiomas (en, fr, de, es, it, pt, nl, hi)[11] | No (offline)[11] | WER macro inglés 6,31 %[11] | no verificado | ~48 GB bf16 | vLLM[11] |
| **Whisper large-v3** | Apache-2.0[12] | 99 idiomas | No nativo (chunked) | FLEURS-es **2,9 %** (50 utterances, MLX en M3, julio 2026)[12] | 10× realtime en RTX 4090 con faster-whisper int8/fp16[13] | 10 GB fp16 / 5 GB int8[13] | faster-whisper, whisper.cpp[13] |
| **Whisper large-v3-turbo** | Apache-2.0[12] | 99 idiomas[12] | No nativo (chunked) | FLEURS-es **3,3 %** (misma medición)[12] | 17× realtime en RTX 4090[13]; whisper.cpp q8_0 es el STT del pipeline de DGX Spark[47] | 6 GB fp16 / 3 GB int8[13] | faster-whisper, whisper.cpp[13] |
| **Canary-Qwen 2.5B** | CC-BY-4.0[14] | Solo inglés[14] | No[14] | SOTA inglés; 418 RTFx reportado por NVIDIA[14] | no verificado (RTFx, no latencia) | ~5 GB | NeMo[14] |
| **Moonshine Streaming (34M/123M/245M)** | MIT[15] | Solo inglés[15] | **Streaming nativo** (encoder de ventana deslizante)[15] | WER no publicado en la card[15] | no verificado (el claim de 107 ms para el 245M viene de un resumen de terceros) | 0,07–0,5 GB | Transformers / Moonshine Voice; el path de Transformers "no implementa streaming plenamente eficiente"[15] |
| **Vosk** | Apache-2.0[16] | 20+ idiomas y dialectos, es incluido[16] | **Streaming nativo**, modelo pequeño por idioma[16] | no verificado | no verificado (corre en CPU, Raspberry Pi)[16] | 0,04–1 GB por modelo | Kaldi-based, bindings Python/Java/C#/Node[16] |
| **IBM Granite Speech 4.1 2B** | Apache-2.0[17] | 6 idiomas: en, fr, de, **es**, pt, ja[17] | No (offline; variantes AR/NAR/plus)[17] | WER solo como figuras en la card[17] | no verificado | ~5 GB | Transformers[17] |
| **Nemotron 3.5 Transcribe 30B-A4B** | OpenMDW-1.1[18] | 40 idiomas[18] | **No: es offline por diseño** — "its internal 30-second encoder chunks are an implementation detail: the model is offline, not a real-time streaming recognizer"[18] | no aplica para voz en vivo | requiere 1×H100 80 GB (BF16) o 1×RTX PRO 6000 96 GB (FP8)[18] | ~60 GB bf16 | NeMo Speech / NIM[18] |

Notas de lectura:

- **El único trío con streaming nativo, español explícito y licencia usable** es Nemotron 3\.5 ASR Streaming 0.6B (OpenMDW-1.1), Voxtral Mini 4B Realtime (Apache-2.0) y Qwen3-ASR (Apache-2.0, streaming unificado pero no cache-aware).
- **Ojo con el benchmark ibérico**: sobre RTX 3090 24 GB, en batch offline, el orden de RTFx es Parakeet 151,7 > Whisper large-v3 11,5 > Qwen3-ASR-1.7B 10,0 > Voxtral Realtime 1,4.[19] Ese 1,4 no significa que Voxtral sea lento en streaming: el propio paper aclara que el encoder causal penaliza en evaluación offline por lotes.[19]
- Los WER de Whisper (2,9 %) y Parakeet (3,45 %) salen de FLEURS, que es lectura limpia de un solo hablante en estudio. En teléfono con ruido y solapamientos, los WER del estudio en español suben a 4,93–6,03 % **a nivel de pipeline completo**.[2]

## 2. TTS comparado

| Modelo | Licencia y restricciones | Idiomas (español) | Streaming | TTFA publicado | Pesos / VRAM | Calidad (Artificial Analysis Elo, Provider Voice, nov-2026) |
|---|---|---|---|---|---|---|
| **Qwen3-TTS 12Hz 1.7B / 0.6B** (VoiceDesign, CustomVoice, Base) | Apache-2.0, sin tope de ingresos ni restricción de reventa[20][21] | 10 idiomas: zh, en, ja, ko, de, fr, ru, pt, **es**, it[20] | Dual-track, texto-in y audio-out; primer paquete tras un carácter[20] | 97 ms extremo a extremo según el vendor[20]; **134 ms p95** medido por Coval sobre "Qwen3 TTS 1.7b" hosteado en Baseten[35] | 4,5 GB (1.7B)[21] | La API hosteada de Qwen puntúa 929; los pesos abiertos no están rankeados[33] |
| **Fun-CosyVoice 3.0 (0.5B-2512)** | Apache-2.0[22] | 9 idiomas: zh, en, ja, ko, de, **es**, fr, it, ru + 18 dialectos chinos[22] | Bi-streaming (texto-in y audio-out)[22] | 150 ms según el vendor[22] | 6,45 GB en disco[22] | No rankeado en AA[33] |
| **Chatterbox Multilingual V3** | MIT, pero **toda salida lleva watermark Perth**[23][33] | 23+ idiomas, es incluido[23] | Por chunks (no streaming nativo); existe Chatterbox-Turbo 350M "para menor latencia"[33] | no verificado | ~2 GB (500M) | 1023 (modelo inglés); proyecto declarado "retired research" por Cartesia en agosto 2026[33] |
| **Fish Audio Drama 3** | **Fish Audio Research License: no comercial**, tampoco los outputs[24][33] | 80+ idiomas, es incluido[24] | Streaming por chunk[24] | 443 ms p95 para `drama3-preview` hosteado (Coval)[35] | 35B MoE / 3B activos, FP8 → ~35 GB (estimado) | **1279, puesto 7 global**[34] |
| **Ming-3.0-tts (0.5B dense / tiny 7.9B-A1.3B)** | MIT[25] | zh, en, de, **es**, fr, ko, ja + sichuanés y cantonés[25] | no verificado | no verificado | ~1 GB / ~16 GB (estimado) | 1069 Controlled Voice (**1.º open weights**, 13.º global); 1188 Provider Voice (3.º open weights, 17.º global); 93,2 % en Pronunciation Robustness (1.º global)[25] |
| **Kokoro-82M** | Apache-2.0[26] | 8 idiomas; español con 1 voz femenina y 2 masculinas[26] | No nativo (por oración) | no verificado | 0,33 GB, corre en CPU[26] | 1064[33] |
| **Piper (piper1-gpl)** | **Motor GPL-3.0**; cada voz tiene su propia licencia de dataset[27][33] | 40+ locales, incluye es_AR, es_ES, es_MX[27] | Por oración (chunked) | no verificado (es el más rápido en CPU por diseño, sin cifra pública) | ~20–60 MB por voz | No rankeado[33] |
| **VibeVoice-Realtime 0.5B** | MIT en pesos, pero la card lo limita a investigación y **Microsoft no lo recomienda para uso comercial**[28][33] | Inglés; 9 idiomas "exploratorios" entre ellos español, "use with caution"[28] | Streaming de texto de entrada + audio[28] | ~200 ms hasta primer audio audible (docs)[28]; la web de marketing dice <300 ms; RTF 0,48 en GB10[47] | 2,0 GB[28] | 953 para VibeVoice 1.5B[33] |
| **XTTS v2 (Coqui)** | **Coqui Public Model License: solo no comercial, incluidos los outputs**; la empresa cerró y ya no vende licencia comercial[29][33] | 17 idiomas[33] | Por chunks | no verificado | ~2 GB | 915[33] |
| **F5-TTS** | Código MIT, **pesos CC-BY-NC-4.0**[30][33] | Enfocado en en/zh[30] | No (flow matching, clip completo) | no verificado | ~0,6 GB (0.3B) | No rankeado[33] |
| **Orpheus 3B** | Apache-2.0 sobre backbone Llama-3B (leer también la licencia Llama)[31][33] | Inglés; el multilingüe (es/it) es research preview[33] | Streaming[33] | ~200 ms streaming, ~100 ms con input streaming, cifra del vendor[33] | ~6 GB | No rankeado[33] |
| **Dia 1.6B** | Apache-2.0[32] | Solo inglés[32][33] | No | no verificado | ~3 GB | No rankeado[33] |

Notas de lectura:

- Para un producto comercial en español, la decisión es entre **Qwen3-TTS** (Apache-2.0, 10 idiomas, 97 ms declarados, sin restricciones de reventa), **Ming-3.0-tts** (MIT, mejor Elo abierto en voz controlada, pero sin latencia publicada) y **Fun-CosyVoice 3.0** (Apache-2.0, 150 ms declarados). Todo lo demás suma una traba: Drama 3 y XTTS no son comerciales, F5-TTS tiene pesos NC, VibeVoice es research-only, Chatterbox marca el agua y está sin mantenimiento, Piper arrastra GPL-3.0 en el motor.
- Los Elo de Artificial Analysis son de *provider voice* (cada modelo con sus voces nativas) y no miden latencia bajo carga ni pronunciación de códigos y montos; la propia AA lista a Ming 1.º en robustez de pronunciación con 93,2 %.[25][34]

## 3. VAD y detección de fin de turno

| Componente | Licencia | Qué aporta | Costo de latencia | Números |
|---|---|---|---|---|
| **Silero VAD v5** | MIT[36] | Segmentación voz/no-voz por chunk de 30 ms | < 1 ms por chunk de 30 ms en un solo hilo de CPU[36] | Es el VAD por defecto de `speech-to-speech`, con `--min_speech_ms 384` y `--min_silence_ms 64`[41] |
| **TEN VAD** | Apache-2.0 **con cláusula adicional**: no se puede desplegar "in a way that competes with Agora's offerings" ni habilitar a terceros a desarrollar aplicaciones[37] | VAD en 16 kHz pensado para agentes | no verificado | Descartable para una plataforma que otros revendan |
| **smart-turn v3.2** | BSD-2-Clause, datasets y pesos abiertos[38] | Modelo de audio nativo (8M params) que decide si el turno terminó; 23 idiomas, español incluido[38] | 10 ms en algunas CPUs, ~65 ms en una instancia 1× de Pipecat Cloud, <100 ms en la mayoría de las nubes[38] | eot-bench: 35,2 % de falsos cortes con presupuesto de 300 ms; 739 ms de latencia media al 10 % de cortes[39] |
| **LiveKit Turn Detector v1 / v1-mini** | Parte de `livekit/agents` (Apache-2.0); `v1` se sirve por LiveKit Inference, `v1-mini` corre local en CPU[43][50] | Detector de audio de fin de turno, 14 idiomas con español y umbral calibrado por idioma; con él el endpointing baja a `min_delay` 0,3 s y `max_delay` 2,5 s (default 0,5/3,0 s)[50] | v1: 295 ms de latencia media al 10 % de cortes; v1-mini: 698 ms[39] | v1: 9,9 % de falsos cortes @300 ms (mejor de la tabla); VAD puro: 55,6 %[39] |

### Cómo se implementa barge-in

- **Pipecat**: las interrupciones vienen activadas por defecto. Cuando la estrategia de inicio de turno dispara, el agregador emite un `InterruptionFrame` (SystemFrame) que (1) cancela la tarea de cada procesador y descarta DataFrames en cola, (2) corta la completion del LLM en vuelo y emite `FunctionCallCancelFrame` para las tools con `cancel_on_interruption`, (3) limpia buffers de TTS y timestamps, y (4) drena la cola de audio del transporte. El bot queda en silencio "within roughly one audio write" y el contexto conserva solo lo efectivamente pronunciado.[40]
- **Anti-falsos positivos**: `MinWordsUserTurnStartStrategy(min_words=3)` para que un "ok" no corte, estrategia Krisp VIVA para distinguir backchannels de interrupciones reales, y mute strategies si querés que el bot termine de hablar.[40]
- **`speech-to-speech`**: usa reapertura especulativa — `--speculative_reopen_ms 800` para turnos que parecen cerrados, `--smart_turn_incomplete_delay_ms 600` y `--smart_turn_max_wait_ms 2000` para turnos incompletos; si vuelve el habla, la revisión anterior se descarta. En parlantes hace falta `--echo-cancellation`.[41]
- **La advertencia empírica más fuerte**: en el estudio en español, con settings por defecto, Pipecat y LiveKit cortaban ante casi cualquier backchannel; un "ok" dicho encima del agente terminó registrado como acuerdo en 3 de 15 llamadas de Pipecat y 2 de 15 de LiveKit, contra 0 de 15 en GPT-Live.[2] Un agente de conocimiento necesita mínimo `min_words≥2` o un clasificador de backchannels.

## 4. Frameworks de orquestación

| Proyecto | Estrellas | Licencia | Transporte | Reemplazo de etapas | Madurez / notas |
|---|---|---|---|---|---|
| **Pipecat** | 17.304[42] | BSD-2-Clause[42] | WebSocket, WebRTC vía transports | Processor/frame pipeline; cada servicio es un processor intercambiable; 68+ integraciones según el survey de Salesforce[1] | El más granular para barge-in y para meter etapas propias; usado como orquestador de referencia en el paper en español (v1.6.0)[2] |
| **LiveKit Agents** | 15.258[43] | Apache-2.0[43] | WebRTC rooms + SIP telefónico | Plugins por etapa, turn detector y VAD propios, métricas por componente | Mejor transporte de producción (SIP/WebRTC), pero el estudio en español le mide 423 ms de transporte de entrada y 214 ms de salida contra 186/2,6 ms de Pipecat por WebSocket local[2] |
| **`huggingface/speech-to-speech`** | 13.706[41] | Apache-2.0[41] | OpenAI Realtime sobre WS y WebRTC, más `/v1/audio/transcriptions` y `/v1/audio/speech` | Cada etapa tiene backends intercambiables por flag/CLI y YAML; corre en producción en robots Reachy Mini[41] | Es el que mejor encaja con "quiero el protocolo de OpenAI Realtime apuntando a mi máquina"; loguea STT, LLM, primer audio de TTS y duración speech-to-audio por respuesta[41] |
| **Dograh** | 6.178[44] | BSD-2-Clause[44] | Telefonía (Twilio/SIP) + WebRTC | Workflow builder visual, MCP server para editar agentes desde un IDE, self-host con docker compose; STT Whisper/Voxtral/Canary-Qwen, TTS Kokoro/Chatterbox[44][45] | Plataforma "tipo Vapi" self-hosted, no un framework de pipeline; útil como referencia de producto, no como librería para control fino de latencia |
| **Baseten Voice Agent Stack** | cerrado (private preview desde 16/11/2026) | propietario | OpenAI Realtime protocol | Orquestador + STT/LLM/TTS intercambiables dentro de su nube | No es self-hosted: es un contraejemplo útil porque documenta el stack y las latencias (ver §5)[46] |

## 5. Arquitectura de referencia y presupuesto de latencia

### 5.1 Presupuesto por etapa (stack local)

| Etapa | p50 | p95 | Fuente y condiciones |
|---|---|---|---|
| Fin de turno (VAD + detector) | 295 ms | ~600 ms | LiveKit Turn Detector v1 al 10 % de cortes (benchmark en inglés)[39], consistente con su `min_delay` de 0,3 s y un `min_silence` de VAD ≥250 ms[50]. Con Silero a 64 ms de silencio + smart-turn local (~65 ms) se puede bajar a ~130–200 ms, a costa de más falsos cortes[38][41] |
| STT final | 92 ms (Qwen3-ASR 0.6B) / 236 ms (Nemotron 3.5) | 105 ms / 253 ms | TTFT vLLM con concurrencia 1, GPU no especificada[6]; TTFS Pipecat self-hosted[3] |
| LLM TTFT | 337 ms | máximo 4.327 ms (arranque en frío); media 1.141 ms | Qwen2.5-7B-Instruct en vLLM 0.8.5 sobre H200[1]. **Para Qwen3.5-4B local no hay TTFT publicado: no verificado** |
| Detección de oración para TTS | 143 ms | no verificado | Medición end-to-end del pipeline de Salesforce[1] |
| TTS TTFB | 134 ms (Qwen3-TTS 1.7B) / 219 ms (ElevenLabs flash v2.5) | 134 ms / 226 ms (máximo) | Coval p95 sobre servicio hosteado[35]; ElevenLabs p50 219 ms, máximo 226 ms, sobre red[1] |
| Transporte | 2,6 ms | 100–400 ms | WebSocket en la misma máquina (Pipecat) vs sala LiveKit Cloud (423 ms de entrada, 214 ms de salida)[2] |
| **Total p50** | **≈ 1,0 s** | **≈ 1,4–1,6 s** | Suma de las etapas locales; sin tool call |

Advertencias:

- **Un tool call cuesta 0,9–1,1 s extra en las tres arquitecturas medidas** — más que cualquier diferencia entre frameworks.[2] Para mantener < 1,5 s con RAG hay que empezar a hablar antes de la tool o resolverla en paralelo: la ejecución especulativa desde hipótesis parciales del ASR baja la TTFA mediana de 5,79 s a 4,60 s en un asistente Android on-device, sin tocar las etapas.[51]
- Las cifras de referencia del mundo real: **755 ms** medidos en el pipeline Deepgram + vLLM + ElevenLabs (LLM en H200, STT y TTS por red)[1]; **~766 ms** en DGX Spark con whisper.cpp large-v3-turbo q8_0 + Ollama + VibeVoice-Realtime-0.5B (una sola medición, sin p50/p95, modelo de Ollama no fijado en el README)[47]; **~1 s de mediana** en Baseten Realtime Voice a 1–56 sesiones concurrentes con STT y TTS en RTX 6000 y LLM de 31B en B200[46]; **2.445–3.090 ms p50** en el estudio telefónico en español con stack hosteado por defecto y tools.[2]

### 5.2 Qué GPU alcanza

| Configuración | VRAM | Qué corre | Evidencia |
|---|---|---|---|
| DGX Spark (GB10) | 128 GB unificada | whisper.cpp turbo + LLM 3–4B en Ollama + VibeVoice 0.5B | 766 ms hasta primer audio, una medición[47] |
| 1× RTX 4090 | 24 GB | Qwen3-ASR-0.6B (1,9 GB) + Qwen3.5-4B bf16 (9,3 GB) + Qwen3-TTS 1.7B (4,5 GB) + caches ≈ 19 GB | suma de pesos según las cards[5][21][48]; `speech-to-speech` pide 24 GB de VRAM para el path con Transformers, y en el path con llama.cpp estima 16 GB, de los cuales ~8 GB son el pipeline de voz[41] |
| 1× RTX 5090 | 32 GB | lo mismo con margen para KV cache de contexto largo y un segundo worker de TTS | — |
| 1× L40S / RTX 6000 Ada | 48 GB | agrega Voxtral Mini 4B Realtime (17,7 GB) en paralelo, o LLM 8B | Voxtral realtime exige ≥16 GB solo[10] |
| 3 nodos (Baseten) | 1×RTX 6000 + 1×B200 + 1×RTX 6000 | Qwen3-ASR, Gemma-4-31B, Qwen3-TTS separados por componente | ~1 s de mediana a 56 sesiones[46] |

## 6. Recomendación concreta

**Stack para agente de conocimiento en español, self-hosted, < 1,5 s:**

1. **Orquestador: Pipecat 1.6.x** (BSD-2). Da el control más fino de barge-in (`InterruptionFrame`, cancelación de tools, drenaje de audio) y el swap de etapas es un processor.[40][42] Si necesitás SIP/WebRTC de producto, **LiveKit Agents 1.6.x** con Turn Detector v1-mini.
2. **VAD: Silero VAD v5** (MIT) con chunks de 32 ms y `min_silence` 250 ms (es el mínimo que exige LiveKit para su detector); **fin de turno: smart-turn v3.2 ONNX int8** (BSD-2, 8 MB, español incluido) como validador, o `v1-mini` del turn detector de LiveKit si vas por LiveKit.[36][38][39][50]
3. **STT: NVIDIA Nemotron 3.5 ASR Streaming 0.6B** (OpenMDW-1.1) con chunk de 160 ms — FLEURS-es 4,64 %, 236 ms p50 / 253 ms p95 de TTFS, licencia sin tope comercial.[7][3] Con chunk de 80 ms subís a 4,87 % de WER y ganás 80 ms. Alternativa si querés Apache puro y un solo runtime con el LLM: **Qwen3-ASR-0.6B** en vLLM (Apache-2.0, TTFT 92/105 ms).[5][6] Mejor WER en español pero sin streaming: **Parakeet TDT 0.6B v3** (CC-BY-4.0, 3,45 %) como segunda pasada sobre el buffer del turno.[9]
4. **LLM: Qwen3.5-4B** (Apache-2.0, 201 idiomas) en **vLLM 0.14+** con function calling y `--enable-auto-tool-choice`; es el LLM por defecto del stack de referencia.[41][48] Con 48 GB, Qwen3.5-8B.
5. **TTS: Qwen3-TTS-12Hz-1.7B-CustomVoice** (Apache-2.0, español entre 10 idiomas, streaming dual-track, 97 ms declarados, 134 ms p95 medidos en un despliegue optimizado).[20][35] Backend: `faster-qwen3-tts` con GGML (`qwentts-cpp`) —el que usa `speech-to-speech`— o vLLM-Omni, sabiendo que hoy vLLM-Omni solo soporta inferencia offline.[21][41] Fallback barato en CPU: **Kokoro-82M** (Apache-2.0, 3 voces en español).[26]
6. **Hardware: 1× RTX 5090 32 GB.** Suma de pesos ≈ 15,7 GB más KV cache y buffers de audio. Con 24 GB (4090) entra, pero sin margen para contexto largo ni concurrencia.
7. **Protocolo: OpenAI Realtime.** Si querés que cualquier cliente de OpenAI apunte a tu máquina, usá `huggingface/speech-to-speech` como fachada (`speech-to-speech serve`, `ws://…/v1/realtime`) y dejá Pipecat o LiveKit como orquestador interno.[41]

**Lo que NO recomendaría** para este caso: Voxtral Mini 4B Realtime si el GPU es de 24 GB (17,7 GB de pesos y solo vLLM); Nemotron 3.5 Transcribe 30B-A4B (offline por diseño y 1×H100/96 GB); VibeVoice-Realtime y Chatterbox para un producto comercial (research-only y sin mantenimiento, respectivamente); XTTS v2 y Fish Drama 3 (no comerciales); TEN VAD si vas a revender la plataforma (cláusula Agora).

## 7. No verificado

- TTFT de Qwen3.5-4B en vLLM sobre RTX 4090/5090: no hay número publicado. El único TTFT local comparable es Qwen2.5-7B en H200 (337 ms p50).[1]
- VRAM y latencia de Qwen3-TTS, Ming-3.0-tts, Chatterbox V3, Piper, Kokoro, Dia y F5-TTS en hardware propio: solo hay pesos en disco y, en algunos casos, claims del vendor.
- WER específico de español para Qwen3-ASR-0.6B/1.7B en la card oficial: la card publica promedios multilingües (7,57 % y 4,90 % en FLEURS), no la fila de español.[4][5] El 3,0 % del 0.6B viene de una medición de terceros en Apple Silicon, no en GPU NVIDIA.[49]
- p50/p95 de los pipelines de DGX Spark y de `speech-to-speech` en español: el primero es una sola medición ("~766 ms"); el segundo no publica benchmark de latencia, solo logs por respuesta.[41][47]
- Latencia de Voxtral Mini Realtime medida en hardware propio: solo hay TTFS de servicio hosteado (525 ms p50) y el delay interno configurado (480 ms).[3][10]

## Sources

[1] https://arxiv.org/html/2603.05413 — Salesforce: Enterprise Realtime Voice Agents (mar-2026)
[2] https://arxiv.org/html/2611.19118v1 — Latencia y turn-taking en agentes de voz en espanol (nov-2026)
[3] https://www.pipecat.ai/benchmarks/speech-to-text — Pipecat STT benchmark (ago-2026)
[4] https://huggingface.co/Qwen/Qwen3-ASR-1.7B — Qwen3-ASR-1.7B
[5] https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf — Qwen3-ASR-0.6B-hf
[6] https://arxiv.org/html/2601.21337 — Qwen3-ASR Technical Report
[7] https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b — Nemotron 3.5 ASR Streaming 0.6B
[8] https://huggingface.co/nvidia/nemotron-speech-streaming-en-0.6b — Nemotron Speech Streaming EN 0.6B
[9] https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3 — Parakeet TDT 0.6B v3
[10] https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602 — Voxtral Mini 4B Realtime 2602
[11] https://huggingface.co/mistralai/Voxtral-Small-24B-2507 — Voxtral Small 24B 2507
[12] https://vocova.app/blog/ai-transcription-accuracy-benchmark-2026 — Whisper FLEURS 12 idiomas (jul-2026)
[13] https://github.com/Mobiss11/Whisper-Skill/blob/main/backends/faster-whisper.md — faster-whisper VRAM/RTX 4090
[14] https://huggingface.co/nvidia/canary-qwen-2.5b — Canary-Qwen 2.5B
[15] https://huggingface.co/UsefulSensors/moonshine-streaming-medium — Moonshine Streaming
[16] https://github.com/alphacep/vosk-api — Vosk API
[17] https://huggingface.co/ibm-granite/granite-speech-4.1-2b — Granite Speech 4.1 2B
[18] https://docs.nvidia.com/nemotron/nightly/nemotron/transcribe35/README.html — Nemotron 3.5 Transcribe (offline)
[19] https://arxiv.org/html/2609.36920v1 — ASR para lenguas ibericas (RTX 3090)
[20] https://qwen.ai/blog?id=qwen3tts-0115 — Qwen3-TTS blog
[21] https://github.com/QwenLM/Qwen3-TTS — Qwen3-TTS repo
[22] https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512 — Fun-CosyVoice3 0.5B
[23] https://huggingface.co/ResembleAI/chatterbox — Chatterbox Multilingual V3
[24] https://huggingface.co/fishaudio/drama-3 — Fish Audio Drama 3
[25] https://github.com/inclusionAI/Ming-3.0-tts — Ming-3.0-tts
[26] https://huggingface.co/hexgrad/Kokoro-82M — Kokoro-82M
[27] https://github.com/OHF-Voice/piper1-gpl — piper1-gpl
[28] https://github.com/microsoft/VibeVoice/blob/main/docs/vibevoice-realtime-0.5b.md — VibeVoice-Realtime 0.5B
[29] https://huggingface.co/coqui/XTTS-v2 — XTTS-v2 (CPML)
[30] https://huggingface.co/SWivid/F5-TTS — F5-TTS
[31] https://github.com/canopyai/Orpheus-TTS — Orpheus-TTS
[32] https://github.com/nari-labs/Dia — Dia 1.6B
[33] https://www.cartesia.ai/learn/open-source-tts — TTS open source por licencia (Cartesia)
[34] https://artificialanalysis.ai/text-to-speech/leaderboard — Artificial Analysis TTS leaderboard
[35] https://benchmarks.coval.ai/tts — Coval TTS TTFA benchmark
[36] https://github.com/snakers4/silero-vad — Silero VAD
[37] https://github.com/ten-framework/ten-vad — TEN VAD (licencia)
[38] https://github.com/pipecat-ai/smart-turn — smart-turn v3.2
[39] https://github.com/livekit/eot-bench/blob/main/output/livekit__eot-bench-data__validation__min_silence_100ms/en/comparison/report.md — LiveKit eot-bench
[40] https://docs.pipecat.ai/pipecat/fundamentals/interruptions — Pipecat interruptions
[41] https://github.com/huggingface/speech-to-speech — speech-to-speech (OpenAI Realtime)
[42] https://github.com/pipecat-ai/pipecat — Pipecat repo
[43] https://github.com/livekit/agents — LiveKit Agents repo
[44] https://github.com/dograh-hq/dograh — Dograh repo
[45] https://www.dograh.com — Dograh sitio
[46] https://www.baseten.co/blog/introducing-the-baseten-voice-agent-stack — Baseten Voice Agent Stack (16-nov-2026)
[47] https://github.com/Logos-Flux/spark-voice-pipeline — Spark Voice Pipeline DGX Spark
[48] https://huggingface.co/Qwen/Qwen3.5-4B — Qwen3.5-4B
[49] https://pypi.org/project/mlx-qwen3-asr — mlx-qwen3-asr
[50] https://docs.livekit.io/agents/logic/turns/turn-detector — LiveKit turn detector docs
[51] https://arxiv.org/html/2610.07641 — Speculative tool execution en agente on-device (Qualcomm, oct-2026)
