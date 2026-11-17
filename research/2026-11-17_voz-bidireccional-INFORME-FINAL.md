# Voz bidireccional open source para un agente de conocimiento — investigación completa

**Fecha:** 17/11/2026
**Caso:** cliente con agente de conocimiento (RAG sobre ventas, tráfico, fidelización y PQR de un centro comercial en Quito) que quiere hablarle por voz y que le responda con voz. Requisito: **self-hosted**, los datos no salen.
**Método:** cuatro investigaciones en paralelo, cada afirmación numérica con fuente. Los informes crudos quedan como anexos.

---

## 1. Resumen ejecutivo

**La decisión es cascada, no end-to-end.** Pero la razón cambió respecto de lo que yo te dije al principio: **no es la latencia de Qwen3-Omni** (esa cifra que te pasé era incorrecta, ver §2), es que un agente de conocimiento necesita **tool calling determinístico y RAG auditable**, y hoy **no existe ningún modelo full-duplex abierto que hable español y tenga tools**.

Cuatro conclusiones que se sostienen con evidencia:

1. **El único full-duplex abierto con tool calling nativo y licencia limpia es inglés** (NemotronLabs VoiceChat 11B). El único full-duplex abierto que declara español es **Haru-4B**, y su propio README dice que *no es una fuente confiable de hechos ni sigue instrucciones como un asistente* — o sea, exactamente lo que un RAG necesita que haga.
2. **La latencia depende de dónde corran las etapas, no del modelo.** Con las etapas locales y colocalizadas: **0,75-1,0 s**. Con proveedores hosteados por red (Deepgram + GPT-4.1-mini + ElevenLabs): **2.616 ms p50 en Pipecat y 3.090 ms en LiveKit** (estudio en español, nov-2026). O sea: para el caso on-prem, el objetivo de ~1 s es alcanzable. Un tool call suma 0,9-1,1 s.
3. **El costo de self-hostear voz a esta escala no cierra**: con 500 conversaciones de 3 minutos por mes el duty cycle del GPU es del 1,14% y el costo por conversación self-hosted (US$ 0,90) es **14 veces mayor** que una cascada cloud por partes (US$ 0,048-0,064). El break-even está en ~3.100 conversaciones/mes. **Pero** si el servidor ya existe por el producto de texto, el costo incremental de sumar voz cae a ~US$ 31/mes.
4. **El riesgo real es el español, no el modelo.** El error en nombres propios es 3-4× el WER general, y el Recreo tiene ~150 locales con nombres que hay que acertar.

---

## 2. Corrección de lo que te dije antes

Tres correcciones, porque investigar es también corregirse:

| Lo que dije | Lo que dice la evidencia |
|---|---|
| "Qwen3-Omni local en Transformers tarda ≈146 s" | **Depende de la fuente y la configuración.** Dos mediciones primarias: **336,10 s E2E en A100 con request offline** y **23,78 s con vLLM-Omni** (TTFP 0,934 s). El número de 146 s aparece citado por el tutorial de Salesforce. En cualquier caso, el orden de magnitud mata la opción y la conclusión se mantiene |
| "vLLM local solo genera texto" | **Parcialmente falso.** El vLLM upstream sirve solo el *thinker*; **vLLM-Omni** sí genera audio con streaming |
| "Latencia esperable 700-1.300 ms" | **Optimista.** Los 755-766 ms son de laboratorio y de un pipeline medido. En producción con transporte real: **2,4-3,1 s p50** según el único estudio en español disponible |

Los 755 ms sí están confirmados: cascada STT→LLM→TTS con function calling, **Salesforce AI Research, arXiv 2603.05413 (marzo 2026)**, con desglose por etapa: LLM TTFT 296 ms + detección de fin de oración 143 ms + TTS 316 ms. Y 758 ms de mediana en un sistema desplegado, con 21 de 36 turnos bajo 800 ms.

---

## 3. Por qué cascada y no full-duplex (la evidencia)

### 3.1 El cuello de botella no es el modelo
El estudio de latencia en español (arXiv 2611.19118, 14/11/2026, 77 llamadas por arquitectura) mide **2.616 ms p50 en Pipecat y 3.090 ms en LiveKit** — pero con el stack **hosteado por defecto** (Deepgram + GPT-4.1-mini + ElevenLabs) sobre red. Con las **mismas etapas locales y colocalizadas, la misma cascada baja a 0,75-1,0 s**. Conclusión: **el transporte y el endpointing definen la latencia, no el tamaño del modelo** — y por eso el requisito on-premise de este cliente no es un obstáculo, es una ventaja de latencia.

### 3.2 Los agentes pierden 50 puntos al pasar a voz
τ-Voice (arXiv 2603.13686): agentes que resuelven **~85% de tareas en texto caen a 26-38% en voz y en tiempo real**. Eso es el dato más honesto del campo y aplica directo: el agente de El Recreo funciona por texto; en voz va a rendir menos, y hay que diseñar para eso.

### 3.3 Full-duplex + RAG es posible pero frágil
MoshiRAG (ICML 2026) inyecta conocimiento en un modelo dúplex con un token de retrieval y búsqueda asíncrona mientras el modelo hace small talk. Funciona, es CC-BY-4.0, corre en 24 GB. Pero la precisión **cae en picada cuando el retrieval pasa los 1,5-3 segundos**. Y es en inglés.

### 3.4 No hay benchmark de full-duplex en español
El mapeo de benchmarks lo dice explícito: *"Arabic, Hindi, Spanish, Portuguese, French, German, Russian, Korean: none has a dedicated full-duplex benchmark"*. La única medición en español es τ-Multilingual, que evaluó GPT-Realtime, Gemini 3.1 Flash Live y Grok Voice — y su sección de limitaciones remata: *"No documented open-weight model covered all five localized languages, full-duplex speech, and live tool use"*. **Cero modelos abiertos.**

Lo bueno: en sistemas comerciales, el español queda **a ≤3,2 puntos del inglés** en task completion. El idioma no es el problema de fondo; la falta de modelos abiertos sí.

---

## 4. Los modelos full-duplex: quién es quién

### 4.1 Full-duplex nativo real (escuchan y hablan en el mismo frame)

| Modelo | Params | Licencia | Español | Latencia medida | Tools | VRAM | Adopción |
|---|---|---|---|---|---|---|---|
| **Moshi** (Moshiko/Moshika) | 7B | CC-BY-4.0 pesos / Apache código | No (inglés) | 200 ms en 1×L4 | **No** — la card dice "cannot access tools" | 24 GB | 11.5k ★, 305k descargas |
| **PersonaPlex** (NVIDIA) | 8.37B | NVIDIA Open Model | No | 170 ms a la interrupción | No | ~17 GB | 12.1k ★, 297k descargas |
| **NemotronLabs VoiceChat 11B** | 11.1B | **OpenMDW-1.1 (comercial libre)** | No | 448 ms turn-taking / 480 ms interrupción, **H100** | **Sí, nativo, con mensajes de espera hablados** | ~22 GB | 3.6k descargas |
| **MiniCPM-o 4.5** | 9.37B | Apache-2.0 | **No** (en/zh) | TTFT 0,6 s · 19 GB bf16 / 12 GB streaming | No documentado | 19 GB (12 GB streaming) | 27.2k ★, 160k descargas |
| **Haru-4B** | 5.27B | Apache-2.0 | **Sí, primario (9 idiomas)** | 65 ms p50 en M1 Max int8; ~15 ms/paso en B300 | **No, es base** | ~12 GB | 568 ★, 4.4k descargas |
| **Realtime-Venus** (Ant) | 2×9B | Apache pesos pero README dice "research only" | No | 75% responde interrupciones | Delegación asíncrona | ≥1×A100 | 284 ★ |
| **DuplexOmni / XDuplexOmni** | 35.3B | Apache-2.0 | No | 506 ms | Sí, capa de thinking | **≥8×H20** | 157 ★ |
| **Lychee-FD** / **BayLing-Duplex** | 12.8B / ~9B | Apache / GLM con registro | No | s/e | No | 2 GPUs / ~20 GB | 172 ★ / 100 ★ |
| **MoshiRAG** | 7.7B | CC-BY-4.0 | No | ~200 ms + retrieval | **Sí, RAG nativo** | 24 GB + encoder | 200 ★ |
| **KAME** (Sakana) | 7B | MIT código, pesos sin licencia | No | s/e | Sí (backend inyectado) | ~24 GB | 126 ★ — **exige OpenAI API key: no es on-prem** |

### 4.2 Los que el catálogo marca como dúplex y no lo son

**Qwen3-Omni 30B-A3B** (Apache-2.0): es *turn-based* con streaming, no simultáneo. Tiene **function calling sobre audio** y salida de voz en 10 idiomas, **español incluido**. 347k descargas. bf16 hace OOM en una GPU; int4 = 20,3 GB. **Es la mejor pieza para una cascada de lujo** (audio nativo → texto → tools → voz), no para reemplazar la cascada.
**Step-Audio 2 mini** (Apache-2.0): tool calling y RAG multimodal, pero turn-based.
**Kimi-Audio** (MIT), **GLM-4-Voice** (Apache código / pesos con registro), **Sesame CSM** (Apache, pero es solo el TTS conversacional), **Freeze-Omni** (licencia Tencent solo académica), **Hibiki** (traducción fr→en).

**Dato estratégico:** Qwen3.5-Omni salió el 30/03/2026 **solo por API, sin pesos**. El último omni abierto de Alibaba es el 3-Omni y no va a haber sucesor open-weight. Hay que planificar sobre un checkpoint congelado.

### 4.3 Veredicto de esta capa

- **Usables en producción hoy:** Nemotron VoiceChat (inglés, con tools), MiniCPM-o 4.5 (en/zh, el más desplegable), PersonaPlex (inglés, voz y rol).
- **Para español, no hay producto: hay una promesa.** Haru-4B es lo más interesante del año arquitectónicamente, pero es un modelo base sin benchmarks, sin instrucciones y sin tools. Usarlo para un RAG de shopping es un proyecto de 3-6 meses de un equipo con GPUs, no una integración.
- **Demos de laboratorio:** DuplexOmni (8×H20 y admite silencios inesperados), Lychee-FD, BayLing, KAME (manda audio a la nube), Realtime-Venus (contradicción legal).

---

## 5. El stack recomendado (cascada)

### 5.1 STT — español con streaming

| Modelo | Licencia | WER ES | Streaming | Latencia | VRAM |
|---|---|---|---|---|---|
| **Nemotron 3.5 ASR Streaming 0.6B** | OpenMDW-1.1 (comercial) | FLEURS-es **4,11-4,87%** según chunk | **Sí, nativo** | TTFS **236 ms p50 / 253 p95** | ~2 GB |
| **Qwen3-ASR 1.7B** | Apache-2.0 | 3,87% (líder) | Sí, vía vLLM | TTFT **92/105 ms** | ~4 GB |
| **Voxtral Mini 4B Realtime** | Apache-2.0 | **3,31% @480 ms** | Sí (solo vLLM) | — | **17,7 GB** |
| **Parakeet TDT 0.6B v3** | CC-BY-4.0 | **3,45%** (el mejor) | **No** (chunked) | — | ~2 GB |
| Whisper large-v3-turbo | Apache-2.0 | 2,98-3,65% | No nativo | — | ~3 GB |

**Elección:** Nemotron 3.5 ASR Streaming (chunk 160 ms) como primario por licencia + streaming + español; Qwen3-ASR como alternativa si preferís el ecosistema vLLM. **Parakeet tiene mejor WER pero no hace streaming** — en un agente de voz, 300 ms de silencio valen más que 0,4 puntos de WER.

### 5.2 TTS — español, comercial, con streaming

| Modelo | Licencia | Español | Streaming | Latencia | Notas |
|---|---|---|---|---|---|
| **Qwen3-TTS 1.7B** | **Apache-2.0** | 10 idiomas, incluye es | dual-track | **97 ms declarados / 134 ms p95** (medido por Coval) | **La elección.** Clonado con 3 s de muestra |
| **Ming-3.0-tts** | MIT | sí | s/e | sin latencia publicada | Lidera Elo abierto (1069) |
| **CosyVoice 3 0.5B** | Apache-2.0 | sí | sí | — | Alternativa sólida, zero-shot |
| **Kokoro-82M** | Apache-2.0 | **3 voces, sin clonado** | — | CPU-friendly | Para prototipar |
| Fish Audio Drama 3 | **No comercial** | — | — | — | 1279 Elo, pero tope de ingresos y no revendible |
| XTTS v2 | **CPML: no comercial "y sus salidas"** | sí | — | — | **Descartar** |
| Chatterbox V3 | MIT | sí, 23 idiomas | — | — | Marca de agua PerTh, sin mantenimiento |
| VibeVoice | **Research only** | — | — | — | Descartar pese al MIT |

### 5.3 Orquestación, VAD y turno

- **Pipecat 1.6.x** — el framework de referencia. Corta por `InterruptionFrame`: cancela LLM y tools, limpia el TTS, drena el transporte y **commitea solo lo que se pronunció**.
- **LiveKit Agents** — si el audio va por WebRTC.
- **huggingface/speech-to-speech** (13.706 ★, Apache-2.0) — la cascada ya armada con servidor compatible OpenAI Realtime (WS + WebRTC), default Silero → Parakeet → Qwen3.5-4B → Qwen3-TTS, **cada etapa swappable**. Corre en producción en los robots Reachy Mini. **Es la mejor base para prototipar en un día.**
- **Silero VAD V5** (min_silence 250 ms) + **smart-turn v3.2 int8** para fin de turno.
- **Ojo con TEN VAD**: trae una cláusula anti-Agora.

### 5.4 Configuración recomendada para El Recreo

```
Silero VAD V5 (250 ms)
   → Nemotron 3.5 ASR Streaming 0.6B (chunk 160 ms)
   → Agente de conocimiento (Qwen3.5-4B o el LLM que ya usa) en vLLM 0.14
   → Qwen3-TTS-12Hz-1.7B-CustomVoice (GGML)
   → Pipecat para barge-in y transporte
Hardware: 1× RTX 5090 32 GB (o L40S en datacenter)
Presupuesto: p50 ≈ 1,0-2,4 s · p95 ≈ 1,4-3,1 s según transporte
```

---

## 6. Costos: la parte que cambia la conversación comercial

### 6.1 El número que importa

| Escenario | Costo mensual | Por minuto | Por conversación (3 min) |
|---|---|---|---|
| **Self-hosted, L4 comprada** | **US$ 448** | US$ 0,299 | **US$ 0,90** |
| Cascada cloud por partes (STT + LLM + TTS) | US$ 71-95 | US$ 0,048-0,064 | **US$ 0,14-0,19** |
| **Incremental si el servidor ya existe** | **~US$ 31** | US$ 0,021 | ~US$ 0,06 |

**Break-even self-hosted vs. cascada cloud propia: ~3.100 conversaciones/mes** (seis veces el volumen del caso). Contra Gemini Live no cierra nunca (~11.500).

### 6.2 La lectura correcta

Con 500 conversaciones de 3 minutos al mes, el GPU está **idle el 98,9% del tiempo**. Comprar una GPU *para voz* es un error económico. **Dos caminos válidos:**

1. **Si el cliente ya tiene servidor por el agente de texto** (es el caso de El Recreo: ya corre el agente on-premise), sumar voz cuesta ~US$ 31/mes incremental. Ahí el self-hosted gana y además respeta el requisito de datos.
2. **Si no lo tiene**, arrancar con cascada cloud por partes y migrar cuando el volumen pase las 3.000 conversaciones/mes.

### 6.3 Costos ocultos que hay que cotizar aparte

- **Telefonía:** Twilio Argentina, **US$ 0,0604/min saliente vs US$ 0,0107/min entrante**; Media Streams agrega US$ 0,0044/min.
- **WhatsApp Business API:** por mensaje (tarifa regional 0,5-1 ¢/mensaje de servicio; el rate card de Argentina no lo pude extraer).
- **Audio almacenado:** 2,88 GB/mes a este volumen — trivial, pero hay que decidir retención (y es dato sensible).
- **Monitoreo y mantenimiento:** el costo real. Cada cambio de API de un proveedor del cliente puede romper el pipeline.

---

## 7. Español: donde se gana o se pierde la demo

### 7.1 El WER miente
**KeyASRBench (nov-2026): el error en nombres propios es 3-4× el WER general.**
- Whisper turbo: WER 5-12% pero **KER 27,3%** en nombres.
- Qwen3-ASR 1.7B: **KER 15,7%**.
- Ejemplo textual: Qwen3-ASR transcribe "Claude Code" como "Cloud Code" con WER de 1,69% en esa oración.

Con ~150 locales en El Recreo, el KER es lo que define si el agente sirve o no.

### 7.2 Cómo mitigarlo
- **Biasing con lista** reduce el WER de las palabras sesgadas **hasta 88% relativo**.
- **Prompting al speech LLM se cae entre 39% y 570% relativo con 250 distractores.** Con 150 locales estás exactamente en el régimen donde colapsa.
- **Regla:** biasing con el **top-10 del piso** que se está consultando + **corrección difusa contra el catálogo**. Nunca la lista completa en el prompt.

### 7.3 Rioplatense: hay evidencia, y es limitada
- Whisper large-v3-turbo: **3,3% en argentino, 4,9% en voseo** (POC propio sobre FLEURS es_419 + 150 grabaciones argentinas).
- **Conserva solo 93 de 125 formas de voseo**: normaliza el dialecto. Un prompt que nombra el dialecto sube la retención a **123/125**.
- Modelos específicos: **BSC whisper-large-v3-LoS** (Apache-2.0, 8.110 h con corpus argentino, sin WER ES publicado) y **surus-ai audio8 0.1B rioplatense** (12,39% WER en 573 clips AR vs 64,76% del base, pero **CC BY-NC**: no comercial).

### 7.4 Code-switching (es/en)
CoSE-E, matriz 64% español / 36% inglés:
- **Qwen3-Omni: 4,2% WER, AER 2,7%** (el mejor open).
- Voxtral Small: 4,9% / 3,6%.
- Parakeet v3: 11,7% / 7,5%.
- **Whisper turbo: 16,1% / 7,3% — traduce en vez de transcribir** cuando detecta mezcla. Salto de 5× respecto de su 3,3% monolingüe.

Para un negocio que dice "el POI del mall", "el dashboard de KPIs", "el ticket promedio": **Whisper es el peor y Qwen3-ASR/Voxtral los mejores.**

---

## 8. Lo que se rompe en producción

1. **Barge-in mal resuelto.** Con los defaults de Pipecat, un "ok" dicho encima del bot quedó registrado como acuerdo en **3 de 15 llamadas**; en LiveKit, **2 de 15**. Hay que revisar qué se commitea al contexto, no solo cortar el audio.
2. **Corte de turno prematuro.** Endpointing demasiado agresivo corta al usuario a mitad de frase; demasiado conservador mete 700 ms de silencio.
3. **Audio de teléfono a 8 kHz** vs. 16 kHz del navegador: el WER empeora y los modelos se entrenaron mayormente en banda ancha.
4. **Eco y audio propio reingresando** al VAD.
5. **Alucinación del TTS** con números y siglas del negocio.
6. **Tail latency:** el p95 es lo que se siente. La diferencia entre p50 y p95 en cascada es de 400-700 ms.
7. **Costo variable sin techo** si el cliente deja el micrófono abierto.

---

## 9. Plan de validación (2 semanas, antes de prometer nada)

**Semana 1 — armar y medir**
1. Levantar `huggingface/speech-to-speech` y cambiar el LLM por el agente de El Recreo. Un día.
2. Grabar **200-300 clips reales** del shopping (mostrador, pasillo, food court, teléfono) con referencia humana doble.
3. Medir: **WER global**, **KER sobre 80-120 nombres de locales**, **% de voseo preservado**, WER/AER en 50-80 frases con "POI", "KPIs", "ticket", tasa de alucinación en silencio.
4. Comparar Nemotron 3.5 ASR vs. Qwen3-ASR con los mismos clips. Quedarse con uno.

**Semana 2 — voz y cierre**
5. Probar dos voces: Qwen3-TTS clonando 3-10 min de una locutora con consentimiento escrito, y CosyVoice 3. **MOS ciego 1-5 con 15-20 oyentes.**
6. Medir latencia p50 y p95 con el transporte real que va a usar el cliente, no en local.
7. Simular 20 llamadas con interrupciones y contar cuántas veces el agente registra como acuerdo algo que no lo fue.

**Cortes sugeridos para aprobar:** WER ≤8% en mostrador · KER ≤15% · voseo ≥70% · MOS ≥3,8 · p95 ≤3 s.

---

## 10. Legal y licencias (no lo dejes para el final)

- **Comercial sin restricciones:** Qwen3-TTS, CosyVoice 3, Kokoro, Audio8-TTS (Apache-2.0/MIT), Nemotron ASR (OpenMDW-1.1).
- **No comercial sobre las salidas:** **XTTS v2** (la CPML dice literal *"non-commercial use of the model and its outputs"*), **Fish Audio S2 Pro** (research), **Drama 3** (tope de ingresos, no revendible como API), **VibeVoice** (research only).
- **Clonado de voz:** consentimiento escrito de la persona, y en UE disclosure obligatoria (AI Act art. 50). **Ecuador: no encontré normativa específica — validar con abogado antes de clonar una voz de marca.**
- **Chatterbox** inserta marca de agua PerTh en el audio generado: si el cliente quiere audio "limpio", no sirve.

---

## 11. Qué decirle al cliente (4 puntos, sin humo)

1. **La voz envuelve al agente, no lo reemplaza.** El motor sigue siendo el mismo agente de conocimiento; la voz es entrada y salida. Una sola fuente de verdad.
2. **Se puede hacer 100% on-premise**, con los datos sin salir. Pero el costo real de sostener una GPU dedicada a voz, a este volumen, no se justifica: conviene colgarlo del servidor que ya tienen.
3. **Latencia esperable: entre 1 y 3 segundos**, según transporte. No es el demo de 200 ms de un paper; es indistinguible de alguien que piensa antes de contestar.
4. **El riesgo no es el modelo, es el español y los nombres de los locales.** Por eso el plan de validación va antes de la promesa comercial.

---

## 12. Anexos

- `voz-fd-modelos-open-source.md` — tabla completa de modelos full-duplex, benchmarks y veredicto por modelo.
- `cascada-voz-open-source-2026.md` — investigación de la cascada, 51 fuentes.
- `reporte-voz-es-rioplatense.md` — español, nombres propios, code-switching, licencias, 37 fuentes.
- `costos-voz-selfhosted-2026.md` — hardware, cuantización, 11 stacks con costo por minuto, operación, 48 fuentes.
