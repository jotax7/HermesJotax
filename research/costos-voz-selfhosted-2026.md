# Agente de voz open source self-hosted: costos, hardware y operación

**Caso:** agente de conocimiento con RAG (ventas, tráfico, fidelización, PQR) de un centro comercial, consultable por voz en español rioplatense, self-hosted en un servidor del cliente. Equipo técnico chico, fee mensual ya cobrado → el costo marginal de cómputo es la variable que decide.
**Fecha de corte:** 17/11/2026. Todos los precios son de lista público a esa fecha; los que no pude verificar están marcados.

---

## 0. Veredicto en cinco líneas

1. **El costo no justifica el self-hosting en este volumen.** 500 conversaciones × 3 min = **1.500 min/mes = 25 horas**. Un GPU comprado para eso queda **98,9 % del tiempo idle**. El costo por minuto self-hosted sale ~6× el de una cascada cloud equivalente.
2. **La razón válida para self-hosted acá es el límite de datos** (audio de clientes del shopping, PQR con datos personales), no la plata.
3. **Lo que sí conviene on-premise es el LLM+RAG**, no el stack de voz completo: es el componente con datos sensibles, el que ya necesitás para el resto del producto, y el que amortizás con otras cargas.
4. **Cascada > end-to-end** para este caso: el RAG necesita texto intermedio auditable, y el end-to-end open (Qwen3-Omni) no llega a latencia de voz sin un serving especializado.
5. **El número que hay que mirar no es el p50, es el p95 de turno** — y en teléfono, con audio 8 kHz, el WER sube y el p95 se estira.

---

## 1. Verificación de los tres datos de partida

| Dato a verificar | Resultado | Evidencia |
|---|---|---|
| Qwen3-Omni end-to-end en Transformers local tarda ~146 s (inservible) | **Dirección correcta, cifra no confirmada.** La medición publicada es **336,10 s** de latencia E2E (A100, request offline único) contra **23,78 s** con vLLM-Omni, y **TTFP de 0,934 s**. No encontré ninguna fuente con 146 s; puede corresponder a una respuesta más corta o a otro GPU. La conclusión operativa se sostiene: por el camino HF Transformers no sirve para voz. El propio README de Qwen3-Omni avisa que la inferencia MoE en Hugging Face Transformers es "muy lenta" y recomienda vLLM. | [1][3] |
| En vLLM "solo genera texto" | **Parcialmente falso.** Es cierto para **vLLM upstream**: el checkpoint se sirve *thinker-only* (texto, sin Talker ni Code2Wav) salvo que cargues el pipeline completo. Pero **vLLM-Omni** (proyecto separado) sirve audio real con streaming: TTFP 0,934 s y 10 conversaciones concurrentes con E2EL de ~105 s. O sea: el problema no es "vLLM no hace audio", es que **necesitás el plugin omni y un GPU grande**. | [1][2] |
| La cascada logra 755–766 ms hasta primer audio | **Confirmado en el orden correcto.** Cascada con streaming (Deepgram + Qwen2.5-7B en vLLM + ElevenLabs): **755 ms**, contra **950 ms** si las etapas van en serie. Sistema desplegado full-duplex: **758 ms de mediana** (36 turnos medidos, 21 por debajo de 800 ms). El 766 no aparece en las fuentes que encontré, pero cae dentro del ruido de medición. | [5][4] |

**Lectura:** la cascada es la única arquitectura que hoy te da <800 ms con modelos abiertos y RAG en el medio. El end-to-end abierto sigue siendo un proyecto de investigación, no un deploy de cliente.

---

## 2. Hardware: VRAM real y concurrencia

### 2.1 Cuánta VRAM pide cada etapa

| Etapa | Modelo de referencia | Peso en VRAM | Pico con runtime y batch |
|---|---|---|---|
| STT streaming | Nemotron Streaming 0.6B (cache-aware) | ~1,2 GB | 2–3 GB |
| STT alternativo | faster-whisper large-v3 | 4.525 MB fp16 / 2.926 MB int8 (medido por maintainers) | 3–5 GB |
| STT alternativo | faster-whisper large-v3-turbo | ~1,6 GB int8, ~30× tiempo real | 2–3 GB |
| LLM chico (voz) | 8B clase Q4_K_M | 5–6 GB | 7–10 GB con KV cache de 8–32K |
| LLM mediano | 27B Q4, contexto 64K | ~20,3 GB pico medido | 21–24 GB |
| LLM grande end-to-end | Qwen3-Omni-30B-A3B | 84,6 GB @16-bit / 42,3 @8-bit / 21,2 @4-bit | + Talker + Code2Wav (~0,4 GB por copia de decoder en BF16) |
| TTS | Kokoro-82M | ~0,3 GB | 0,5–1 GB |
| TTS | XTTS v2 / Qwen3-TTS 1.7B | 3–4 GB | 4–6 GB |

Fuentes: [6] para el ledger por tier, [19] para Whisper medido, [20] para turbo int8, [11] para Qwen3-Omni, [2] para Code2Wav. [10] confirma el 27B Q4 en 20.266 MiB con 64K de contexto.

**El error clásico es sumar los picos como si corrieran a la vez.** Un turno es secuencial: STT → LLM → TTS, y nada corre en Whisper mientras el LLM piensa. Lo que importa es la **co-residencia de pico**: cuánto está *cargado* (no activo) en el peor momento. Con **3 conversaciones concurrentes**, sin embargo, las etapas de distintas sesiones **sí se solapan** — mientras la sesión A está en TTS, la B está en LLM. Ahí necesitás las tres etapas residentes y con headroom de batch, no solo cargadas.

**Presupuesto para este caso (3 concurrentes, LLM 8–14B):** 12–16 GB de VRAM con todo residente y margen. Una **L4 de 24 GB alcanza y sobra**. Con un LLM de 27B Q4 subís a 26–30 GB y necesitás 48 GB (L40S / RTX 6000 Ada / 2×24 GB).

### 2.2 Cuántas conversaciones aguanta cada GPU

Nadie publica esto para *tu* stack: el techo lo fija la etapa más lenta bajo presupuesto de latencia, no la memoria. Los anclajes medidos:

- **STT:** 160–180 conexiones concurrentes en una **A10**; 100–200 en A10G; **560 streams** en H100 con chunks de 320 ms (benchmark publicado por NVIDIA). [8][9][7]
- **TTS:** **20–50 streams** por A10G (es la etapa más pesada), ~180 conversaciones en A10 según el proveedor, **20 generaciones concurrentes medidas en una L4** con TTS fine-tuneado. [9][8][42]
- **Cascada completa:** el único modelo público con LLM da **~6 sesiones en RTX 5090** y **~14 en H100 PCIe** (Llama 3.1 8B 4-bit + Kokoro, recomendando correr al 50–70 % de eso). [10]

| Configuración | VRAM / ancho de banda | Conversaciones simultáneas (planificación) | Comentario |
|---|---|---|---|
| **L4** 24 GB | 24 GB, 300 GB/s | **4–6** (8B Q4) | La opción racional para 3 concurrentes. $0,59/h en RunPod [10], $0,80/h en AWS [36] |
| **A10 / A10G** 24 GB | 24 GB, 600 GB/s | **6–10** | Mejor relación que L4 en TTS |
| **RTX 4090** 24 GB | 24 GB, 1008 GB/s | **5–8** | Rápida, sin ECC, sin soporte de fabricante, consumo alto |
| **RTX 5090** 32 GB | 32 GB, 1792 GB/s | **~6** (modelo Spheron, 8B+4bit) | El mejor precio/rendimiento si la conseguís a MSRP |
| **L40S** 48 GB | 48 GB, 864 GB/s | **12–20** | Entra un 27B Q4 con TTS en la misma placa |
| **A100** 80 GB | 80 GB, 2 TB/s | **20–30** | Sobredimensionado para 3 concurrentes |
| **H100** 80 GB | 80 GB, 3,35 TB/s | **14** (8B) a **30–40** (MoE 30B-A3B) | STT sola: 560 streams |
| **DGX Spark** 128 GB | 128 GB unificada, **273 GB/s** | **2–4** | Entra el modelo grande, pero el ancho de banda es de notebook: decode lento. $6.950 |
| **Mac Studio M4 Max** 128 GB | 128 GB unificada, **546 GB/s** | **3–6** | MLX con continuous batching escala 4,3× a 16 requests; sin CUDA, sin soporte de vendor para serving |

Fuentes: [8][9][10][7][42] para los anchos; [32] precio DGX Spark ($6.950 al 17/11/2026, subió desde $3.999); [33] 273 GB/s; [34][35] Apple Silicon y precio; [36][37][38] para las tarifas de alquiler (L4 USD 0,80/h en AWS, H100 USD 3,79–4,59/h, L40S USD 0,96–1,67/h).

Las cifras de la columna "conversaciones simultáneas" son **estimación propia** anclada en esos tres puntos medidos, no benchmarks publicados para cada placa. Cualquier número de esta tabla hay que confirmarlo con un load test del stack real antes de comprar.

**Regla de planificación:** corré producción al 50–70 % del techo medido y dimensioná por **p95 de turno**, no por OOM. El GPU puede sostener cientos de sesiones en memoria y romper el presupuesto de latencia mucho antes de llenarse. [8][9]

---

## 3. Cuantización: qué ganás y qué perdés

| Formato | Qué es | Ganancia | Costo de calidad (evidencia) | ¿Para voz? |
|---|---|---|---|---|
| **GGUF (Q4_K_M / Q5)** | pesos 4–5 bits, formato llama.cpp/Ollama | 27B de 54 GB de pesos → ~20 GB pico en una placa de 24 GB | Perplejidad +0,3–0,8 puntos en 7–8B; en 27–70B el daño absoluto baja. No hay kernels rápidos para batching alto como en vLLM | OK para el LLM si estás en una sola placa. **No** para producción con concurrencia: llama.cpp no batchea bien |
| **AWQ (INT4)** | protege canales salientes por magnitud de activación | 4,8 GB vs 15,5 GB en 8B; 6.100 tok/s vs 3.850 | +0,17 ppl (8B), +0,13 (14B), +0,09 (70B). En MMLU/ARC cae 1–3 %, en código 3–6 % | **La mejor opción INT4** para el LLM de voz. En tool-calling se banca, en razonamiento multi-paso no |
| **GPTQ (INT4)** | corrección layer-by-layer tipo OBQ | Igual que AWQ en memoria, algo menos de throughput | Peor que AWQ de forma consistente: +0,34 ppl en 8B, +0,28 en 14B, +0,23 en 70B. En MMLU 2–5 % | Solo si el tooling te obliga. En vLLM, AWQ gana |
| **FP8 (W8A8)** | pesos y activaciones en float de 8 bits | 8,1 GB vs 15,5 GB; 5.620 tok/s (+46 %); TTFT 14 ms vs 19 | **Prácticamente sin pérdida** en benchmarks académicos (>500.000 evaluaciones, "effectively lossless"). Pero: a 64 requests concurrentes la self-consistency cae de **97,6 % a ~75 %** | **Default si tenés Hopper/Blackwell.** En Ada (L4, 4090) el FP8 corre pero la ganancia es sobre todo memoria; el salto de velocidad aparece con tensor cores FP8 de datacenter |
| **INT8 (STT)** | CTranslate2 / Optimum-Quanto dinámico | Whisper large: 4.525 → 2.926 MB (−35 %); un paper reporta **−57 % de tamaño y WER por debajo del baseline**; en L4 el INT8 es lo que permite meter varios workers en la placa | Otro benchmark da **+0,20 puntos absolutos de WER** (5,76 % → 5,96 %) con −10,7 % de latencia y +12 % de throughput | **Sí, sin drama.** Es la cuantización más segura del stack |
| **INT8 / W4 (TTS)** | cuantización post-entrenamiento del modelo de voz | Reduce footprint, permite más streams por placa | El **vocoder es el componente sensible**: cuantizarlo a W4 cuesta **−2,87 UTMOS**; el resto del modelo a W4 solo −0,17. Mantener vocoder en W8 devuelve 4,252 UTMOS | **Sí, pero nunca cuantices el vocoder por debajo de 8 bits** |

Fuentes: [13] tablas de perplejidad/throughput por formato y tamaño; [14] FP8 lossless; [15] caída de self-consistency en alta concurrencia; [16][17] Whisper int8; [12] empaquetado int8 en L4; [18] vocoder TTS; [6][10] footprints.

**Lo que importa para voz y no aparece en las tablas de perplejidad:**

- **El LLM de voz no necesita un genio, necesita constancia.** Perder 1 % en MMLU es irrelevante; que la misma pregunta devuelva respuestas distintas según el batch (el 97,6 % → 75 % de FP8 a 64 concurrentes) **sí** es un problema, porque el agente contesta precios y horarios. [15]
- **STT: int8 es gratis.** La degradación es de décimas de punto de WER y el ahorro de memoria es lo que te deja correr STT + LLM + TTS en una placa. [16][17]
- **TTS: cuantizá el transformer, no el vocoder.** El oído detecta artefactos de vocoder mucho antes que cualquier métrica de perplejidad. [18][43]
- **Regla práctica:** FP8 para el LLM si el GPU lo soporta nativo, AWQ si no; int8 en STT; vocoder de TTS en FP16/BF16. No bajes de 8 bits en ninguna etapa que toque audio.

---

## 4. Costo por minuto: self-hosted vs APIs cerradas

Base: 1.500 minutos/mes (500 conversaciones × 3 min). Supuestos: el agente habla ~45 % del tiempo; TTS a ~800 caracteres por minuto hablado; telefonía de entrada a Argentina (el cliente llama al shopping).

| Stack | $/min | $/conv (3 min) | $/mes (1.500 min) | Fuente |
|---|---|---|---|---|
| **Gemini 3.8 Live** (audio in $0,005 + out $0,018/min) | **0,013** | 0,04 | **20** | [22] |
| **DIY cascade low-cost** (Deepgram Nova-3 + LLM + Aura-2 + Twilio AR) | **0,048** | 0,14 | **71** | [24][30] |
| **OpenAI gpt-live-1** (tarifa plana por minuto) | 0,050 | 0,15 | 75 | [21] |
| **OpenAI gpt-realtime-2.1** ($32/$64 por 1M tokens de audio) | 0,054 | 0,16 | 81 | [21] |
| **DIY cascade calidad** (Deepgram + LLM + ElevenLabs Flash + Twilio AR) | 0,064 | 0,19 | 95 | [24][23][30] |
| **Vapi** ($0,05 host + STT + LLM + TTS) | 0,082 | 0,25 | 123 | [27] |
| **ElevenLabs Agents** ($0,08/min + LLM + telefonía) | 0,101 | 0,30 | 151 | [23] |
| **Retell** (infra $0,055 + TTS $0,015 + LLM $0,032) | 0,102 | 0,31 | 153 | [26] |
| **Bland Start** (plano) | 0,140 | 0,42 | 210 | [28] |
| **Self-hosted, L4 comprada** (amortización + luz + 0,1 FTE) | **0,299** | 0,90 | **448** | cálculo propio, §8 |
| **Self-hosted, L4/L40S alquilada always-on** (RunPod $0,59/h + ops) | **0,454** | 1,36 | **681** | [10] |

Notas de lectura:

- **Gemini Live es outliers por abajo.** Es audio-a-audio cerrado; no te da control del RAG ni del corpus del shopping, y cada turno re-factura toda la sesión. Sirve como benchmark de piso, no como reemplazo del caso.
- **Vapi/Retell/ElevenLabs cobran orquestación, no inteligencia**: el $0,05–0,10 de plataforma se suma a los modelos que ya pagás. [27][26][23]
- **Cartesia** cobra **$0,03/min** de agente gestionado y sus créditos de Sonic salen ~$0,05/min de audio en el plan Pro: es la alternativa de TTS más barata con calidad buena, no la más barata a secas. [25]
- **Bland y las tarifas planas** ($0,12–0,14) incluyen LLM+STT+TTS, que a este volumen es más caro que armarlo por partes.
- **Ojo con el promo de Deepgram:** Nova-3 monolingüe está a **$0,0048/min** con tarifa de lista tachada de $0,0077 y sin fecha de fin. Si el promo se cae, el DIY low-cost pasa de $0,048 a **$0,050/min** — no cambia la conclusión. [24]
- **El self-hosted no compite en precio a 1.500 min/mes.** Compite en soberanía del dato.

Para conversaciones de 3 minutos el número que se factura al cliente final es **$/conv**, no $/min: ahí la diferencia entre Gemini ($0,04) y Bland ($0,42) es 10×.

---

## 5. Costos ocultos

### 5.1 Telefonía

| Ítem | Precio | Fuente |
|---|---|---|
| Twilio Argentina — llamada local **entrante** | **$0,0107/min** + **$8,00/mes** por número | [30] |
| Twilio Argentina — llamada local **saliente** | **$0,0604/min** | [30] |
| Twilio Argentina — **móvil** saliente | **$0,3528/min** | [30] |
| Twilio Argentina — toll-free entrante | $0,2582/min + $25/mes | [30] |
| Twilio US — entrante / saliente | $0,0085 / $0,0140/min | [29] |
| Twilio SIP / browser | $0,0040/min | [30] |
| Media Streams (necesario para mandar audio al agente) | **+$0,0044/min** | [30] |
| Grabación de llamada | +$0,0025/min + $0,0005/min/mes de storage | [30] |
| SIP trunk propio (BYOC) | $0,0040/min | [30] |

**El ítem que se olvida:** para conectar el audio a tu cascada necesitás Media Streams o Conversation Relay ($0,07/min) además del minuto de voz. Y en Argentina el saliente local es **6× el entrante** — si el agente llama (campañas de fidelización), el modelo de costos cambia de signo. [30]

### 5.2 WhatsApp Business API

Meta factura **por mensaje entregado**, no por conversación, desde julio 2025. [31]

- Las **1.000 primeras respuestas de servicio por número y por mes son gratis**; de ahí en adelante se paga tarifa por mercado × categoría. [31]
- Servicio (respuesta a un usuario dentro de la ventana de 24 h): tarifa baja. Ejemplo publicado para Brasil: **0,68 ¢/mensaje**. [31]
- **Meta Business Agent** (si usás su agente y no el tuyo): **$2,00 por 1M tokens**, ~20.000–25.000 tokens por mensaje → **4–5 ¢/mensaje**. [31]
- Tarifa exacta de Argentina: **precio no verificado** — Meta publica rate card por mercado en CSV/PDF que no pude extraer. Rango observado en la región: **0,5–1 ¢ por mensaje de servicio**.

Un handoff típico "el agente manda el resumen de la consulta por WhatsApp" son 2–4 mensajes → **1–4 ¢ por conversación**, más el costo del agente que los redacta.

### 5.3 Ancho de banda y almacenamiento

| Formato | Bitrate | Por llamada de 3 min | 500 llamadas/mes |
|---|---|---|---|
| PCM16 16 kHz mono (navegador) | 256 kbps | 5,76 MB | **2,88 GB** |
| PCM16 8 kHz mono (telefonía) | 128 kbps | 2,88 MB | 1,44 GB |
| G.711 con headers IP/UDP/RTP | ~87 kbps | 1,96 MB | 0,98 GB |
| Opus 24 kbps | 24 kbps | **0,54 MB** | **0,27 GB** |
| PCM16 24 kHz (formato típico de Realtime) | 384 kbps | 8,64 MB | 4,32 GB |

Cálculo propio sobre bitrates de [45][46]. **Conclusión:** el almacenamiento de audio es ruido (menos de 3 GB/mes en el peor formato); el ancho de banda tampoco es el problema a 3 concurrentes (3 × 384 kbps = 1,2 Mbps). **Lo que sí pesa es la retención**: si guardás audio por compliance, 3 GB/mes × 24 meses = 72 GB, y ahí entran cifrado, backup y política de borrado.

### 5.4 Los costos que no aparecen en ninguna tarifa

| Ítem | Orden de magnitud | Fuente |
|---|---|---|
| **Personas**: 1,5–2 ingenieros que sepan operar inferencia GPU en producción | **$25.000–40.000/mes** de staffing en el modelo de Softcery | [9] |
| Monitoreo (APM + logs + alertas + evaluación de calidad) | $50–300/mes de herramientas a este volumen; el costo real es el tiempo de armado | — |
| Mantenimiento de integraciones (Twilio, WhatsApp, cambios de API, versiones de modelo) | 15–30 % del tiempo del equipo, permanente | [9] |
| Re-entrenamiento / re-indexado del RAG cuando cambian los datos del shopping | recurrente, no puntual | — |
| Guardia y incidentes (el agente atiende clientes reales) | el "3 a.m. incident" es parte del costo de ownership | [9] |

A este volumen, **el ítem de personas es 10–20× el costo del GPU**. Ese es el argumento honesto contra el self-hosting, y también el motivo por el que conviene colgarlo de un servidor que ya existe por otra razón.

---

## 6. Operación: qué se rompe en producción

### 6.1 Los cinco modos de falla que vas a ver

| Falla | Cómo se manifiesta | Causa | Mitigación |
|---|---|---|---|
| **Alucinación del TTS** | El agente dice palabras que no están en el texto, o directamente mete ruido/gibberish. Más frecuente en modelos de baja latencia tipo Turbo | El decoder se "escapa" del texto con prosodia forzada o chunks mal cortados | Round-trip STT vs guion (ver §6.3); fallback a un segundo motor TTS; no mandar chunks <8 palabras |
| **Corte de turno (falso positivo)** | El agente arranca a hablar cuando el cliente hizo una pausa para pensar | Endpointing por timer de silencio: necesita ≥600 ms para no cortar, y eso ya te come el presupuesto. Un detector aprendido puede bajar el recall a 12,5 % | Política híbrida: silencio + semántica + timeout de 800 ms. El paper Voice-Light terminó descartando el detector aprendido y quedándose con Silero por timing |
| **Eco / se escucha a sí mismo** | El agente se interrumpe, se contesta, o repite | Falta AEC, o el TTS entra en el micrófono | AEC en el cliente (WebRTC) + regla de "audio generado ≠ audio escuchado": sólo la historia confirmada por el navegador es contexto durable |
| **8 kHz vs 16 kHz** | En el navegador anda, en el teléfono el WER se dispara y confunde nombres propios y precios | La telefonía recorta todo arriba de 4 kHz; el STT entrenado en 16 kHz pierde consonantes. Pasar de 8 a 16 kHz reduce el WER ~20 % relativo — y ese upsampling **no recupera** lo que nunca se capturó | Probar con audio telefónico real, no con el micrófono de la notebook. Modelo STT entrenado en banda angosta o con augmentación de canal |
| **Tail latency (p95/p99)** | El p50 está bien y un 5 % de los turnos tiene 3–4 s de silencio | Un tool call del RAG, un cold start, un pico de cola en el GPU, GC del runtime | Presupuesto por etapa, límite de tool steps, timeouts con respuesta de relleno ("dejame chequear eso"), y medir p95 no p50 |

Fuentes: [43][44] artefactos TTS y detección; [4] turn-taking y barge-in reversible; [41] presupuesto de latencia y tool calls; [47] 8→16 kHz; [9] banda angosta en agentes telefónicos.

### 6.2 Presupuesto de latencia de referencia

| Etapa | Objetivo / techo | Observado |
|---|---|---|
| Detección de fin de turno | 120 / 280 ms (P50/P95) | timer de silencio ≥600 ms; semántico <300 ms |
| STT (fin de habla → final) | 350 / 500 ms | 60/150 ms si es local; ~250 ms por API; 83 ms medido on-prem |
| LLM primer token | 375 / 750 ms | 250/600 ms local; 700 ms–1,5 s por API |
| Tool call | no cubierto | **+1 pasada completa de LLM**; APIs <1 s, outliers de 10 s |
| TTS primer audio | 100 / 250 ms | 110/220 ms local; 75 ms de inferencia ≠ 197 ms de benchmark con red |
| Red + telefonía + playout | 60/160 ms red + 80/150 ms buffer | +200–300 ms fuera de región |
| **Turno completo** | **1.115 / 1.400 ms** (Twilio) · **~680 / ~1.560 ms** (ElevenLabs) | |

Fuente: [41]. Los targets de la industria son P50 <800 ms y P95 <1,5 s. [41]

**El tool call es lo que rompe el presupuesto.** Una consulta al RAG (precio de alquiler de un local, horario de un servicio) cuesta una pasada completa de LLM + otro TTFT. Un solo lookup puede costar más que todo el resto del turno. [41]

### 6.3 Qué hace falta para monitorear calidad en vivo

| Señal | Cómo se mide | Alerta |
|---|---|---|
| **WER real** | STT sobre el audio del propio agente vs el texto que se mandó a sintetizar (round-trip). Detecta alucinación de TTS y garble | >2 % de turnos con divergencia |
| **TTFA por etapa** | Span por componente (VAD, STT final, LLM TTFT, TTS primer chunk), no sólo end-to-end | p95 >1,5 s |
| **Tasa de interrupción / falso corte** | Cuántas veces el usuario habló encima del agente y cuántas el agente se cortó solo | >10 % de turnos |
| **Tasa de no-resolución** | Turnos que terminan en derivación a humano o en silencio >4 s | tendencia semanal |
| **Groundedness del RAG** | Cada respuesta con su chunk citado; sampled audit semanal | <95 % de respuestas con cita válida |
| **Costo por conversación** | Tokens + minutos + storage por sesión | desvío >30 % sobre la mediana |
| **Eco / loop** | Detección de que la transcripción del agente se parece a su propio output | cualquier ocurrencia |

La detección de artefactos de TTS se hace con round-trip STT + diff contra el guion: es la única forma confiable de agarrar garble sin escuchar todas las llamadas. [44][43]

---

## 7. On-premise vs cloud para este caso

| Dimensión | Cloud gestionado (Vapi/Retell/ElevenLabs) | Cascada cloud por partes | Self-hosted on-prem |
|---|---|---|---|
| **Time to production** | días | 2–4 semanas | **meses** (armar, afinar tool-calling, load-testear) [9] |
| **Costo a 1.500 min/mes** | $123–210/mes | $71–95/mes | $448–681/mes |
| **Costo a 100.000 min/mes** | $8.000–14.000/mes | $4.800–6.400/mes | ~$700–1.200/mes (estimación: la misma placa + una segunda por redundancia) |
| **Soberanía del audio** | el audio sale | el audio sale, salvo STT on-prem | **total** |
| **Control del modelo / versionado** | nulo | bajo | total |
| **Quién se despierta a las 3 a.m.** | el proveedor | vos | **vos** |
| **Latencia** | mejor (todo co-locado en el proveedor) | buena | **mejor si co-locás** (STT local −140 ms, TTS local −90 ms) [8] |

**Cuándo conviene cada uno, sin vueltas:**

- **Cloud gestionado:** volumen bajo o irregular, equipo sin nadie de infra, o cuando el audio no es dato sensible. Acá es el default.
- **Cascada cloud por partes:** querés control del RAG y del prompt pero no querés operar GPUs. Es el punto dulce para 500–10.000 conversaciones/mes.
- **On-premise:** (a) hay un requisito duro de que el audio no salga, (b) el volumen es alto y estable — Softcery pone el umbral en **1–2 millones de minutos conectados por mes** [9], o (c) ya tenés GPU operada por otra razón y el costo marginal real es sólo energía.

**Qué implica sostener un servidor con GPU en la infraestructura del cliente:**

1. **Hardware físico:** rack, energía estabilizada, refrigeración, repuestos. Una L4 consume 72 W pero el servidor completo 300–550 W → 219–402 kWh/mes.
2. **Sin scale-to-zero:** el agente atiende a cualquier hora, así que la placa está encendida 730 h/mes aunque se use 25. El costo fijo no se diluye.
3. **Drivers, CUDA, versiones:** actualizar el stack de inferencia puede romper el modelo. Necesitás pinning y un entorno reproducible.
4. **Un solo punto de falla:** si se cae la placa, el agente no atiende. Sin redundancia (2× GPU) no hay SLA que puedas firmar.
5. **Acceso y actualizaciones:** cada cambio es una visita o un VPN. El ciclo de mejora se vuelve más lento que en cloud.
6. **Datos:** backups, cifrado en reposo del audio, retención, y alguien que responda un pedido de acceso a datos.

---

## 8. Modelo de costos concreto del caso

**Parámetros:** 1 servidor · 3 conversaciones concurrentes · 500 conversaciones × 3 min = **1.500 min/mes = 25 h/mes**.

### 8.1 El dato que define todo

| Métrica | Valor |
|---|---|
| Minutos por mes | 1.500 |
| Horas por mes | **25** |
| Capacidad instalada (3 slots × 730 h) | 2.190 h |
| **Duty cycle** | **1,14 %** |
| **GPU idle** | **98,9 %** |

Con 3 concurrentes y 500 conversaciones, el servidor está prendido **25 horas de 730**. Cualquier costo fijo se divide por 1.500, no por la capacidad real. Ese es el problema económico, y no lo arregla ninguna optimización de modelo.

### 8.2 Costo self-hosted, tres variantes

Supuestos: amortización 36 meses, 0,1 FTE de operación a $2.500/mes, energía a $0,12/kWh (tarifa industrial; el precio mayorista argentino rondó **USD 90–169/MWh** en 2026, y la tarifa final suma distribución e impuestos → **tarifa exacta del cliente: precio no verificado, rango US$ 0,10–0,20/kWh**) [48].

| Variante | Capex | Amortización | Energía | Ops | **Total/mes** | **$/min** | **$/conv** |
|---|---|---|---|---|---|---|---|
| **L4 24 GB comprada** ($3.197 GPU [39] + $3.000 servidor) | $6.197 | $172 | $26 (300 W) | $250 | **$448** | **$0,299** | $0,90 |
| **L40S 48 GB comprada** (~$8.900 [38] + $3.000 servidor) | $11.900 | $331 | $48 (550 W) | $250 | **$629** | **$0,419** | $1,26 |
| **L4 alquilada always-on** (RunPod $0,59/h [10]) | $0 | — | — | $250 | **$681** | **$0,454** | $1,36 |
| **RTX 4090 usada** (~$3.555 [40] + $2.500 servidor) | $6.055 | $168 | $66 (450 W @ 0,20) | $250 | **$484** | $0,323 | $0,97 |

Sin el ítem de operación (si el equipo ya está pagado por el fee mensual), restale $250:

| Variante | Total/mes sin ops | $/min | $/conv |
|---|---|---|---|
| L4 comprada | **$198** | $0,132 | $0,40 |
| L40S comprada | $379 | $0,253 | $0,76 |
| L4 alquilada | $431 | $0,287 | $0,86 |

### 8.3 Comparación contra el caso

| Opción | $/mes | $/conv | Diferencia vs L4 comprada |
|---|---|---|---|
| Gemini 3.8 Live | $20 | $0,04 | −$428 |
| DIY cascade low-cost | $71 | $0,14 | −$377 |
| DIY cascade calidad | $95 | $0,19 | −$353 |
| Vapi | $123 | $0,25 | −$325 |
| **Self-hosted L4 comprada (con ops)** | **$448** | **$0,90** | — |
| Self-hosted L4 alquilada | $681 | $1,36 | +$233 |

### 8.4 Punto de equilibrio

Con el caso base (**L4 comprada, $448/mes**):

| Contra | Precio cloud | Minutos/mes para empatar ($448 ÷ precio) | Conversaciones/mes |
|---|---|---|---|
| DIY cascade low-cost | $0,048/min | **9.333 min** | **~3.100 conv** |
| DIY cascade calidad | $0,064/min | 7.000 min | ~2.300 conv |
| Vapi | $0,082/min | 5.463 min | ~1.800 conv |
| Retell | $0,102/min | 4.392 min | ~1.460 conv |
| Gemini 3.8 Live | $0,013/min | 34.462 min | ~11.500 conv |

**Lectura:** el self-hosting empata con una cascada cloud por partes recién a **~3.100 conversaciones/mes**, 6× el volumen del caso; contra Vapi/Retell empata a ~1.500–1.800 conversaciones/mes, todavía 3–3,6× el caso. Contra Gemini Live necesitarías ~11.500 conversaciones/mes para que la cuenta cierre. Sin el ítem de operación el break-even contra DIY low-cost baja a ~4.100 min (~1.400 conv) — sigue siendo 3× el caso.

### 8.5 La variante que sí cierra

**El servidor no se compra para voz: se compra para el RAG.**

El agente de conocimiento necesita igual un LLM + base vectorial + embeddings. Si ese servidor ya existe por el producto de texto (chat web, WhatsApp, backoffice), el costo marginal de sumarle voz es:

| Ítem incremental | $/mes |
|---|---|
| Energía extra de los modelos de voz (STT 0,6B + TTS 82M, ~4 GB residentes) | ~$8 |
| Almacenamiento de audio (Opus, 0,27 GB/mes) | ~$0,01 |
| Telefonía Twilio AR entrante + Media Streams ($0,0151/min) | **$23** |
| **Total incremental** | **~$31/mes → $0,021/min** |

A **$0,021/min** el self-hosted le gana a todo, incluido Gemini Live. Pero eso es porque el capex ya está pago por otra carga, no porque el stack de voz se pague solo.

---

## 9. Recomendación

1. **No compres un GPU para voz a este volumen.** A 1.500 min/mes el duty cycle es 1,14 % y el $/min self-hosted es 2,5–6× el cloud.
2. **Arrancá con cascada cloud por partes** (Deepgram/AssemblyAI + tu LLM + TTS + Twilio AR): ~$71–95/mes, controlás el RAG y el prompt, y la migración futura es cambiar una URL.
3. **Si el requisito duro es que el audio no salga**, hacé **híbrido**: STT on-prem + LLM on-prem sobre texto, y TTS/telefonía en cloud. El audio se convierte en texto dentro del perímetro; el texto hacia afuera lo podés anonimizar. Es el 80 % del beneficio de soberanía con el 20 % del costo.
4. **Si igual van full on-premise**, comprá **una L4 de 24 GB** (no L40S, no A100): alcanza para 3 concurrentes con LLM 8–14B, consume 300 W y es lo más barato de sostener. Reservá el 20 % de VRAM para STT+TTS y poné el LLM a FP8 si migrás a L40S/H100, AWQ si te quedás en L4.
5. **Medí antes de firmar el SLA:** p95 de turno con audio telefónico real de 8 kHz, WER sobre 100 llamadas del shopping, y tasa de falso corte. Sin esos tres números no hay compromiso de latencia posible.

---

## Sources

[1] https://docs.vllm.ai/projects/vllm-omni/en/latest/design/qwen3_omni_tts_performance_optimization
[2] https://docs.vllm.ai/projects/vllm-omni/en/latest/user_guide/examples/online_serving/qwen3_omni
[3] https://github.com/QwenLM/Qwen3-Omni
[4] https://arxiv.org/html/2609.20995v1
[5] https://www.dograh.com/hub/blogs/how-voice-ai-pipeline-works
[6] https://www.bigiron.cc/guides/one-gpu-voice-stack-whisper-llm-tts-vram-budget
[7] https://softcery.com/lab/self-hosting-streaming-stt-for-voice-agents
[8] https://cerebrium.ai/resources/concurrent-voice-sessions-per-gpu
[9] https://softcery.com/lab/self-hosted-voice-ai-stack
[10] https://www.dograh.com/hub/blogs/voice-ai-own-gpus
[11] https://savrn.com/models/qwen3-omni-30b-a3b-instruct/gpus
[12] https://www.e2enetworks.com/blog/benchmarking-asr-models-nvidia-l4-parakeet-whisper-nemotron
[13] https://www.generalcompute.com/blog/quantized-vs-full-precision-gptq-awq-fp8-benchmarks-across-model-sizes
[14] https://arxiv.org/html/2411.02355
[15] https://dev.to/huilin_ye_f804826bf674576/fp8-cut-our-tpot-by-25-at-high-concurrency-it-also-changed-the-answers-4foe
[16] https://aclanthology.org/2026.speakable-1.5.pdf
[17] https://github.com/ankushChoudhary1903/cpu-asr-benchmark
[18] https://arxiv.org/html/2609.28974
[19] https://localaimaster.com/blog/voice-ai-vram-requirements-by-gpu
[20] https://www.spheron.network/blog/faster-whisper-gpu-cloud-production-deployment-guide
[21] https://developers.openai.com/api/docs/pricing
[22] https://blog.google/innovation-and-ai/technology/developers-tools/build-real-time-voice-applications-gemini-audio
[23] https://elevenlabs.io/pricing/agents
[24] https://deepgram.com/pricing
[25] https://www.cartesia.ai/pricing
[26] https://www.retellai.com/pricing
[27] https://vapi.ai/pricing
[28] https://app.bland.com/pricing
[29] https://www.twilio.com/en-us/voice/pricing/us
[30] https://www.twilio.com/en-us/voice/pricing/ar
[31] https://developers.facebook.com/docs/whatsapp/pricing
[32] https://aliteq.com/dgx-spark-price
[33] https://voltgridnews.com/story/nvidia-dgx-spark-review-128gb-gb10-box-now-lists-at-6-950
[34] https://ar5iv.labs.arxiv.org/html/2601.19139
[35] https://www.apple.com/shop/buy-mac/mac-studio/m4-max-chip-16-core-cpu-40-core-gpu-128gb-memory-1tb-storage
[36] https://gpuledger.dev/providers/aws/l4
[37] https://pricingsaas.com/companies/lambdalabs/diffs/2026W46
[38] https://gpurentalprices.com/l40s
[39] https://www.insight.com/en_US/shop/product/900-2G193-0000-000/nvidia/900-2G193-0000-000/NVIDIA-L4-GPU-computing-processor-L4-24-GB
[40] https://rigprice.com/gpu/rtx-4090
[41] https://vaya-soft.com/blog/voice-agent-latency
[42] https://www.reddit.com/r/AI_Agents/comments/1x8g109/how_we_achieved_20_concurrent_lowlatency_regional
[43] https://onepin.ai/blog/tts-audio-artifacts-detection-and-fixes-2026
[44] https://ttsaudit.com/blog/common-tts-audio-artifacts
[45] https://callsphere.ai/blog/vw2c-opus-24khz-vs-pcm16-bandwidth-cost-tradeoff-2026
[46] https://www.vobiz.ai/resources/blogs/telephony-infrastructure/what-is-voip
[47] https://www.eurasip.org/Proceedings/Eusipco/Eusipco2014/HTML/papers/1569910419.pdf
[48] https://energiaestrategica.com/energiaestrategica/en/notes/aes-argentina-ve-mas-apetito-ppa-tras-el-salto-del-precio-electrico-los-grandes-usuarios-estan-empezando-a-tomar-riesgo
