# Recomendación técnica — Modelo de voz bidirectional (full-duplex) open source

**Preparado para:** Gerencia / equipo técnico
**Fecha:** 17 de noviembre de 2026
**Objeto:** seleccionar el modelo de audio **full-duplex nativo** (escucha y habla al mismo tiempo) para la interfaz de voz del Agente de Conocimiento, con pesos abiertos, español y despliegue on-premise.

---

## 1. Recomendación en una línea

**Haru-4B (higurashi, 12 de noviembre de 2026), Apache 2.0.**

Es el único modelo de **full-duplex nativo con pesos abiertos que habla español**. Escucha y habla en simultáneo en frames de 133 ms, corre en una GPU de ~12 GB y su código es Apache 2.0. Se publica como modelo base, por lo que el agente necesita una etapa de ajuste fino y una capa de delegación de herramientas (detalladas en §5).

---

## 2. Ficha técnica del modelo

| Atributo | Dato |
|---|---|
| Nombre | **Haru-4B** (`higurashi-ai/Haru-4B`) |
| Autor | higurashi (Tokyo) |
| Fecha de publicación | **12 de noviembre de 2026** |
| Licencia | **Apache 2.0** (pesos y código) |
| Parámetros | ~5,27B, sobre backbone de texto **Qwen3.5-4B** |
| Full-duplex | **Nativo, a 7,5 Hz.** Cada 133 ms toma un frame de audio del usuario y produce un frame de audio y texto propios |
| Arquitectura | Los tres streams (audio del usuario, audio del modelo, texto del modelo) se suman en una sola posición del language model: escuchar y hablar nunca se esperan |
| Códec de audio | VibeVoice, causal, 24 kHz, latentes continuos de 64 dimensiones |
| Idiomas | **9 principales: inglés, español, portugués, alemán, francés, chino, japonés, ruso y coreano** (preentrenado sobre 40M+ horas, 160+ idiomas) |
| Latencia reportada | **65,2 ms p50 end-to-end** en MacBook Pro con M1 Max, int8, app nativa Swift con kernels Metal propios |
| Memoria | **~12 GB** en una GPU NVIDIA |
| Implementaciones | PyTorch, MLX (app nativa macOS) y **plugin para vLLM-Omni**; demo web y servidor local en el puerto 8998 |
| Voz | Se controla con un clip de referencia de 3 s a 3 min. La personalidad, con una "character card" de texto |
| Estado | **Modelo base preentrenado, liberado para investigación** |

---

## 3. Por qué este y no otro

| Modelo | Bidireccional real | Español | Tool calling | Pesos | Licencia | VRAM | Veredicto |
|---|---|---|---|---|---|---|---|
| **Haru-4B** | **Sí (7,5 Hz, 133 ms)** | **Sí (9 idiomas)** | No (base) | Abiertos | Apache 2.0 | 12 GB | **Recomendado** |
| Nemotron VoiceChat 11B (NVIDIA) | Sí | **No (inglés)** | **Sí, nativo** | Abiertos | OpenMDW-1.1 | ~22 GB | Mejor arquitectura con tools, pero sin español |
| Moshi (Kyutai) | Sí (200 ms medidos en L4) | No (inglés) | No | Abiertos | CC-BY-4.0 / Apache | 24 GB | Pionero y referencia; sin español |
| PersonaPlex (NVIDIA) | Sí (170 ms a la interrupción) | No | No | Abiertos | NVIDIA Open Model | ~17 GB | Voz y personaje; sin español |
| MiniCPM-o 4.5 | Sí | No (en/zh) | No documentado | Abiertos | Apache 2.0 | 19 GB (12 GB streaming) | El más liviano; sin español |
| DuplexOmni / XDuplexOmni | Sí | No (zh/en) | Sí, capa de razonamiento | Abiertos | Apache 2.0 | 8× H20 | Demasiado hardware |
| Realtime-Venus (Ant Group) | Sí | No (en/zh) | Delegación a backend | Abiertos con ambigüedad | Apache + "research only" | ≥1× A100 | Licencia inconsistente |
| Qwen3-Omni 30B-A3B | **No** (por turnos) | Sí | Sí, nativo | Abiertos | Apache 2.0 | int4 ≈ 20 GB | Excelente, pero **no es bidireccional** |
| Gemini Live / OpenAI Realtime | Sí | Sí (94-113 idiomas) | Sí | **Cerrados** | API | n/a | Única opción "llave en mano", pero **rompe el requisito on-premise** |

**Conclusión:** si el requisito es *bidireccional + open source + español*, hay **un solo modelo en el mundo hoy: Haru-4B**. La contra es que viene sin instrucciones ni herramientas: eso se resuelve en dos etapas (§5).

---

## 4. Estado del arte en el idioma: lo que hay que decir de frente

- **No existe ningún benchmark público de full-duplex en español.** El mapeo de benchmarks del campo lo dice explícitamente: *"Arabic, Hindi, Spanish, Portuguese, French, German, Russian, Korean: none has a dedicated full-duplex benchmark"*.
- La única evidencia en español es **τ-Multilingual** (septiembre 2026, 4.500 llamadas full-duplex): el español queda **a ≤3,2 puntos del inglés** en task completion — pero evaluó sistemas comerciales (GPT-Realtime, Gemini, Grok Voice), **ningún modelo open-weight**.
- **Haru-4B no publicó benchmarks de calidad**, ni en inglés ni en español. Lo que publicó es arquitectura y latencia.
- Por lo tanto: **la calidad de conversación en español de Haru hay que medirla nosotros.** No hay atajo ni dato de terceros que lo reemplace.

---

## 5. Cómo se convierte Haru-4B en el agente de voz

Haru resuelve el problema de la **conversación** (escuchar y hablar a la vez, interrumpir, ser interrumpido). No resuelve **el conocimiento ni las herramientas**. Se completa en dos etapas:

### Etapa 1 — Ajuste fino para que sea un asistente
**Qué falta:** el modelo es base; su propia model card dice que *"no es una fuente confiable de hechos y no sigue instrucciones como lo hace un asistente"*.
**Cómo se cierra:** ajuste fino supervisado (SFT) con **3.000 a 5.000 pares pregunta-respuesta** del negocio (las preguntas del cuestionario de El Recreo son el punto de partida), más un set de conversaciones con la "character card" del asistente.
**Resultado:** conversación bidireccional en español con la personalidad y el criterio de la marca.

### Etapa 2 — Delegación de herramientas (patrón frontend/backend)
**Qué falta:** Haru no ejecuta herramientas, así que no puede consultar los datos del shopping.
**Cómo se cierra:** el patrón publicado y verificado en 2026 para full-duplex con tools:
1. Haru (frontend duplex) detecta que la consulta requiere datos y **emite un token de delegación** mientras sigue conversando (mantiene el ritmo, hace small talk o dice "dejame ver").
2. El **backend** —el agente de conocimiento que ya funciona, con su RAG y sus tools— recibe la transcripción y ejecuta la consulta.
3. La respuesta vuelve al frontend y Haru la dice con su propia voz, sin cortar la conversación.

Referencia: arXiv 2609.19334, "A frontend-backend architecture for tool calls in full-duplex speech models". Es exactamente nuestro caso de uso.

---

## 6. Arquitectura propuesta

```
Usuario ⇄ (audio bidireccional, frames de 133 ms)
              │
        Haru-4B  (full-duplex, on-premise, ~12 GB)
              │  token de delegación + transcripción
              ▼
   Agente de Conocimiento existente (RAG + tools, solo lectura)
              │  respuesta
              ▼
        Haru-4B  ──►  voz de respuesta (mientras el usuario puede seguir hablando)
```

Ventaja frente a la cascada: el usuario **no espera un turno**. Puede interrumpir, corregirse o agregar un dato mientras el agente habla, y el modelo lo escucha en el mismo frame.

---

## 7. Hardware y costo

| Escenario | Configuración | Costo de referencia |
|---|---|---|
| On-premise del cliente (recomendado) | 1 GPU 16-32 GB (RTX 5090 / L40S), modelo en bf16 o int8 | **≈ US$ 31/mes incremental** si el servidor ya corre el agente de texto |
| On-premise dedicado | 1× L4 / A10 | ≈ US$ 448/mes |
| Desarrollo y demo | MacBook Pro M1 Max (65 ms p50 reportados) o cualquier GPU de 12 GB | sin costo de cómputo cloud |

**Nota de escala:** a 500 conversaciones/mes de 3 minutos, el GPU queda inactivo el 98,9% del tiempo. La voz debe colgarse del servidor que ya existe, no comprar hardware nuevo para ella.

---

## 8. Plan de ejecución propuesto

| Fase | Duración | Entregable | Criterio de aprobación |
|---|---|---|---|
| **0. Prueba de concepto sin ajuste** | 1 semana | Haru corriendo on-premise con la character card y una voz de referencia, conversando en español | Conversación fluida con interrupción, sin cortes; latencia p95 ≤300 ms en red local |
| **1. Ajuste fino del asistente** | 3-4 semanas | Modelo ajustado con 3-5 mil pares del negocio | Responde correctamente ≥85% de un set de 100 preguntas reales |
| **2. Delegación de herramientas** | 2-3 semanas | Frontend duplex + backend con RAG y tools | Consultas con datos resueltas en ≤3,5 s sin cortar la conversación |
| **3. Validación con el cliente** | 2 semanas | Piloto con usuarios del área de Relacionamiento | Error en nombres de locales ≤15%; satisfacción ≥4/5 |

**Total: 8 a 10 semanas.** Es un proyecto de I+D aplicada, no una integración de una semana. Ese es el costo real de tener conversación bidireccional nativa y no un pipeline por turnos.

---

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| **Es un modelo de investigación, sin benchmarks** | Calidad en español desconocida hasta probarla | Fase 0 de una semana, antes de comprometer plazos. Es el primer entregable, no el último |
| Requiere ajuste fino propio | 3-4 semanas y datos etiquetados | Usar las preguntas del cuestionario del cliente como semilla del dataset |
| Sin ecosistema ni soporte | Dependencia de un proveedor chico (higurashi) | Pesos Apache 2.0 y código abierto: el modelo queda en casa. Sin riesgo de que cierren la API |
| Alternativa si el ajuste no rinde | Se pierde tiempo | Plan B documentado: cascada con Qwen3-ASR + Qwen3-TTS (también Apache 2.0 y español), con latencia de 0,75-1,0 s local |
| Voz clonada | Riesgo legal | Clip de referencia con consentimiento escrito de la persona; validar normativa local antes de usar una voz de marca |
| Audio telefónico a 8 kHz | Degrada el modelo | Alcance inicial en web/navegador a 16 kHz |

---

## 10. Qué se solicita aprobar

1. **Modelo:** Haru-4B (Apache 2.0) como motor de conversación bidireccional, on-premise.
2. **Fase 0 de una semana** para validar calidad en español antes de cualquier compromiso con el cliente.
3. **Presupuesto de ajuste fino:** 3-4 semanas de un perfil técnico + etiquetado de 3.000-5.000 pares.
4. **Capa de delegación de herramientas** sobre el agente de conocimiento existente (dos-tres semanas).
5. **Plan B aprobado de antemano:** si Haru no alcanza la calidad esperada, se ejecuta la cascada Qwen3 sin volver a empezar el proyecto.

---

## Anexo — Fuentes

- Model card `higurashi-ai/Haru-4B` (Hugging Face, 12/11/2026): arquitectura, 7,5 Hz, 9 idiomas, 12 GB, licencia Apache 2.0, limitaciones declaradas.
- Blog técnico de higurashi (13/11/2026) y repositorio `higurashi-ai/Haru`: 65,2 ms p50 en M1 Max int8, implementaciones PyTorch/MLX/vLLM-Omni.
- arXiv 2609.19334 — arquitectura frontend-backend para tool calls en modelos full-duplex.
- arXiv 2609.35820 — τ-Multilingual: 4.500 llamadas full-duplex, español a ≤3,2 puntos del inglés.
- fullduplex.ai — mapeo de benchmarks: no existe benchmark dedicado de full-duplex en español.
- arXiv 2609.21967 — NemotronLabs VoiceChat, primer full-duplex abierto con tool calling (inglés).
- Model card y technical report de Qwen3-Omni (alternativa no bidireccional, Apache 2.0, español).
