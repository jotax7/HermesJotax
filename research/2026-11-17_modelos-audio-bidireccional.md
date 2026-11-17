# Modelos de audio bidireccional open source — research (noviembre 2026)

**Para qué:** un cliente de agente de conocimiento quiere hablarle por voz y que le responda con voz.
**Restricción:** todo open source / self-hosted (los datos no salen).
**Fecha de los datos:** 17/11/2026.

---

## 1. La conclusión antes del detalle

**No uses un modelo end-to-end full-duplex para un agente de conocimiento.** Usá una **cascada streaming**: VAD → STT → tu agente (con tool calls) → TTS.

La razón no es opinión, está medida: un paper de 2026 evaluó Qwen3-Omni —el mejor candidato self-hostable end-to-end— en tres configuraciones:

| Configuración | Latencia audio-a-audio |
|---|---|
| API Realtime en la nube | ~702 ms (no es self-hostable) |
| vLLM local | 516 ms, pero **solo genera texto desde audio** (no sintetiza voz) |
| Transformers local (pipeline completo) | **≈146 segundos** — inservible en tiempo real |

Su conclusión textual: *"the cascaded streaming pipeline remains the practical architecture for self-hosted real-time agents"*. Su cascada logra **755 ms hasta el primer audio, con function calling completo**.

Y hay un segundo dato que mata la idea de "full-duplex + RAG": el paper de MoshiRAG muestra que la precisión de recuperación **cae en picada cuando la latencia de retrieval pasa los 1,5 segundos**. Inyectarle conocimiento a un modelo dúplex es posible, pero frágil.

**Traducción para el cliente:** la magia del full-duplex (interrumpir, solaparse, backchannels) no es lo que necesita. Necesita que el agente conteste bien sobre SUS datos, en español, con latencia humana. Eso hoy se hace con cascada.

---

## 2. El panorama end-to-end open source (por si igual querés uno)

Ordenados por lo que importa para este caso.

| Modelo | Origen | Licencia | Latencia reportada | Idiomas | Nota |
|---|---|---|---|---|---|
| **Moshi** | Kyutai (2024) | Pesos CC-BY 4.0, código MIT | 160 ms teórico / **200 ms medido en L4** | inglés | El pionero. Dos streams paralelos (propio y del usuario) + codec Mimi 12,5 Hz |
| **PersonaPlex** | NVIDIA (ene-2026) | open | **170 ms** primer respuesta | inglés | Orientado a persona/avatar |
| **MiniCPM-o 4.5** | OpenBMB (feb-2026) | open | n/d | en, zh +30 | El más liviano de los omni; corre en 8B |
| **Qwen3-Omni 30B-A3B** | Alibaba (sep-2025) | **Apache 2.0** | ver tabla de arriba | en, zh, ja +16 | El flagship abierto. Ojo: Qwen3.5-Omni (mar-2026) es **cerrado** |
| **NemotronLabs VoiceChat 11B** | NVIDIA (ago-2026) | open | **448 ms** | inglés | El único que combina dúplex **y** tool use: 100% de toma de interrupción, 82,5% F1 en selección de tool |
| **Haru-4B** | independiente (nov-2026) | open, uso comercial | n/d | **en, es, pt** +6 | Recién salido, sin benchmarks independientes |
| **Step-Audio 2 mini** | StepFun (ago-2025) | open | n/d | zh, en | Buena calidad de audio |
| **Kimi-Audio** | Moonshot (abr-2025) | open | n/d | zh, en | |
| **GLM-4-Voice** | Zhipu (oct-2024) | open | n/d | zh, en | |
| **Sesame CSM** | Sesame (mar-2025) | open | n/d | inglés | Más TTS conversacional que dúplex |

**Lo peor del end-to-end:** casi todos son inglés/chino primero. El español es de segunda y no hay benchmarks públicos de calidad conversacional en castellano. Para un cliente que va a hablar rioplatense con nombres de locales y marcas, eso es un riesgo de demo.

**Advertencia metodológica que da el propio campo:** las latencias **no son comparables entre familias**. Los 160 ms de Moshi son medición práctica en una L4; los 160-320 ms de Freeze-Omni son solo del predictor de estado, y su pipeline completo en escenario real ronda **1,2 segundos**. Cualquier tabla que compare esos números de frente está mintiendo.

---

## 3. La cascada que sí funciona

### STT (reconocimiento de voz)

| Modelo | Licencia | Idiomas | Streaming | Cuándo usarlo |
|---|---|---|---|---|
| **Qwen3-ASR 1.7B** | Apache 2.0 | **52 idiomas y dialectos** | sí, vía vLLM | La mejor opción multilingüe con streaming. 6,14% WER en inglés |
| **Nemotron 3.5 Transcribe** | open | 7 idiomas | sí | El de menor error promedio: **6,10% en inglés, 4,69% en 7 idiomas** |
| **Parakeet TDT 0.6B v3** | CC-BY-4.0 | 25 idiomas europeos (incluye español) | chunked (NeMo) | El más rápido en batch; muy sólido en español |
| **Whisper large-v3 / turbo** | MIT | **99 idiomas** | no nativo (por chunks) | El que corre en todos lados. Con faster-whisper va 4x más rápido |
| **Voxtral Mini 4B Realtime** | Apache 2.0 | multilingüe | sí | Alternativa europea |
| **Moonshine** | MIT | inglés primero | sí | CPU, edge, Raspberry Pi |
| **Vosk** | Apache 2.0 | 20+ | sí, CPU | Emergencia, hardware mínimo |

**Para español con acento local: Parakeet o Qwen3-ASR.** Whisper sigue siendo el seguro.

### TTS (síntesis de voz)

Ranking del leaderboard de Artificial Analysis al 7/11/2026 (104 proveedores):

- **Fish Audio Drama 3** — 1275 Elo, el mejor open-weight (7º de 104). Pesos de 41,5 GB, tope de ingresos, no se puede revender como API.
- **Ming-3.0-tts-0.5B** — 1187 Elo, el mejor que podés shippear bajo **MIT o Apache 2.0**.
- **Qwen3-TTS** (0.6B / 1.7B) — Apache 2.0, voces preset, diseño de voz y clonado por referencia.
- **Fun-CosyVoice 3.0** (0.5B) — Apache 2.0, **streaming multilingüe con control de pronunciación**.
- **Chatterbox Multilingual V3** (0.5B) — MIT, **23 idiomas con clonado**.
- **Kokoro-82M** — Apache 2.0, 1064 Elo, corre en CPU. Para arrancar barato.
- **Piper** — runtime GPL, voces con términos variables. Edge/offline.

**Para el cliente: CosyVoice 3 o Qwen3-TTS.** Ambos Apache 2.0, ambos con streaming, ambos con opción multilingüe. Y si el español tiene que sonar natural rioplatense, hay que evaluar clonado de una voz propia con Chatterbox o Qwen3-TTS.

### Orquestación
- **Pipecat** — el framework de referencia para cascadas de voz.
- **LiveKit Agents** — si el audio va por WebRTC.
- **Y hay un proyecto abierto de 13,7k estrellas (Apache 2.0)** que ya trae la cascada armada con servidor compatible con OpenAI Realtime: **Silero VAD + Parakeet TDT + Qwen3.5-4B + Qwen3-TTS**, cada etapa swappable. Es la mejor base para prototipar en un día.

### Detección de turno
- **Silero VAD** (MIT) para voz/silencio.
- **Smart-turn** o un clasificador de fin de turno para no cortar al usuario a mitad de frase.
- El *barge-in* (que el usuario interrumpa) se resuelve en la cascada, no en el modelo: se corta el TTS en curso cuando el VAD detecta habla.

---

## 4. Arquitectura recomendada

```
Usuario ──audio──> WebRTC ──> VAD (Silero) ──> STT streaming (Qwen3-ASR / Parakeet)
                                                     │
                                            texto transcrito
                                                     ▼
                                    Agente de conocimiento (LLM + tools + RAG)
                                                     │ texto
                                                     ▼
                                    TTS streaming (CosyVoice 3 / Qwen3-TTS)
                                                     │ audio
                                     barge-in: VAD corta el TTS
```

**Presupuesto de latencia realista (una GPU L4/A10):**
- VAD + fin de turno: 150-300 ms
- STT streaming: 100-250 ms
- LLM + tool call + retrieval: 300-800 ms (depende del agente)
- Primer chunk de TTS: 100-200 ms
- **Total hasta primer audio: 700-1.300 ms** — que es lo que se siente natural en una llamada.

Referencia medida: un pipeline armado sobre un DGX Spark (whisper.cpp large-v3-turbo + Ollama con Llama 3.2 3B + VibeVoice-Realtime) reportó **~766 ms hasta el primer audio**. Y la cascada del paper citado: **755 ms con function calling**.

---

## 5. Lo que yo le diría al cliente

1. **La voz no reemplaza al agente: lo envuelve.** El motor sigue siendo el mismo agente de conocimiento; la voz es una capa de entrada y salida. Eso mantiene una sola fuente de verdad.
2. **Se puede hacer 100% on-premise.** STT, LLM y TTS abiertos en un servidor suyo. Los datos no salen, igual que hoy.
3. **Latencia esperable: alrededor de un segundo.** No es la promesa de 200 ms de un demo de laboratorio, pero es indistinguible de una persona que piensa antes de contestar.
4. **El riesgo no es el modelo, es el español.** Antes de prometer nada, hay que hacer una prueba con 30 preguntas reales del negocio, con nombres de locales y marcas, y medir tasa de acierto de transcripción y naturalidad de la voz.

## 6. Plan de prueba (una semana)

1. Armar la cascada con el proyecto open de 13,7k estrellas y reemplazar el LLM por el agente propio.
2. Grabar 30 preguntas reales del área de Relacionamiento (las 5 preguntas de negocio del cuestionario).
3. Medir: WER en español con nombres propios, latencia p50 y p95 hasta primer audio, y si el TTS interrumpe bien.
4. Comparar Qwen3-ASR vs. Parakeet en las mismas 30 preguntas. Quedarse con uno.
5. Probar dos voces: CosyVoice 3 y Qwen3-TTS. Elegir con el cliente escuchando, no por Elo.
6. Recién ahí cotizar la integración de voz como módulo.

## 7. Fuentes

- Análisis de despliegue self-hosted de Qwen3-Omni y cascadas (arXiv, 2026) — latencias 702 ms / 516 ms / 146 s y la conclusión sobre cascada.
- MoshiRAG (arXiv 2604.12928) — caída de precisión cuando el retrieval supera 1,5 s.
- Arquitectura frontend-backend para tool calls en full-duplex (arXiv 2609.19334) — 2,80 s y 3,14 s con tool calls.
- NeurIPS 2026 — modelo dúplex bilingüe de larga conversación; compara contra Moshi, MiniCPM-o-4.5 y Qwen3-Omni-30B.
- fullduplex.ai/models — tabla de 73 modelos, con licencia, idiomas y fecha.
- gpuwerk (7/11/2026) — ranking de TTS open weight sobre Artificial Analysis; Fish Drama 3, Ming, Qwen3-TTS, CosyVoice 3, Chatterbox, Kokoro.
- micdrop / AssemblyAI / pinggy (nov-2026) — comparativas de STT: Nemotron 3.5, Qwen3-ASR, Parakeet, Whisper, Voxtral, Moonshine.
- Archestack "Best of open-source voice (nov-2026)" — proyecto de cascada con servidor compatible OpenAI Realtime.
