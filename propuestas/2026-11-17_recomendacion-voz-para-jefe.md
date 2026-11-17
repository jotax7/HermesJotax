# Recomendación técnica — Interfaz de voz para el Agente de Conocimiento

**Preparado para:** Gerencia / equipo técnico
**Fecha:** 17 de noviembre de 2026
**Objeto:** definir el modelo de audio open source para que el agente de conocimiento pueda ser consultado por voz y responda por voz, en español, dentro de la infraestructura del cliente.

---

## 1. Recomendación en una línea

**Qwen3-Omni 30B-A3B (Alibaba), licencia Apache 2.0, servido con vLLM-Omni**, complementado con detección de turno (Silero VAD) para la interrupción del usuario.

Es el único modelo de pesos abiertos que reúne las cinco condiciones del caso: **audio entra, audio sale, habla español, ejecuta tool calling nativo y se puede correr on-premise sin restricciones comerciales**.

---

## 2. Ficha del modelo recomendado

| Atributo | Dato |
|---|---|
| Nombre | **Qwen3-Omni-30B-A3B** (variante Instruct) |
| Autor | Alibaba (equipo Qwen) |
| Fecha | Septiembre 2025 |
| Licencia | **Apache 2.0** (pesos y código) |
| Arquitectura | Mixture of Experts: 30B totales, ~3B activos, con módulo *talker* de generación de voz |
| Modalidades | Texto, imagen, audio y video de entrada; **texto y voz de salida** |
| Idiomas de entrada de voz | 19 |
| Idiomas de salida de voz | **10, incluido español** |
| Tool calling | **Sí, nativo sobre audio** (function calling con audio como entrada) |
| Servido en producción | **vLLM-Omni** (streaming de audio). TTFP medido: **0,934 s** |
| Requisito de memoria | bf16 no entra en una GPU; **int4 ≈ 20,3 GB** |
| Adopción | 4.116 estrellas en GitHub · **347.566 descargas** en Hugging Face |
| Riesgo de continuidad | **Qwen3.5-Omni salió solo por API, sin pesos.** Este es el último de la línea abierta: conviene fijar la versión en el contrato |

---

## 3. Por qué este modelo y no otro

| Criterio | Qwen3-Omni | Nemotron VoiceChat 11B | Haru-4B | MiniCPM-o 4.5 | Step-Audio 2 mini |
|---|---|---|---|---|---|
| Pesos abiertos | Sí (Apache 2.0) | Sí (OpenMDW) | Sí (Apache 2.0) | Sí (Apache 2.0) | Sí (Apache 2.0) |
| **Español** | **Sí (salida de voz)** | No (inglés) | Sí (6 idiomas) | No (en/zh) | No (zh/en) |
| Audio entra / audio sale | Sí | Sí | Sí | Sí | Sí |
| **Tool calling** | **Sí, nativo** | Sí, nativo | **No** (modelo base) | No documentado | Sí |
| Full-duplex simultáneo | No (por turnos con streaming) | Sí | Sí | Sí | No |
| Madurez de despliegue | Alta (347k descargas, vLLM-Omni) | Media (nuevo, 3,6k descargas) | Baja (4,4k descargas, sin benchmarks) | Alta | Media |
| Uso para este caso | **Recomendado** | Referencia técnica (inglés) | Requiere ajuste fino | Solo inglés/chino | Sin español |

**Conclusión de la comparación:** Nemotron es el mejor full-duplex abierto con herramientas, pero **solo habla inglés**. Haru es el único full-duplex abierto con español, pero **no sigue instrucciones ni ejecuta herramientas**: es un modelo base que requeriría un proyecto de ajuste fino. Qwen3-Omni es el único que cumple todo lo que el cliente necesita hoy.

---

## 4. Arquitectura propuesta

```
Usuario (voz)
    │
    ▼
Detección de actividad de voz — Silero VAD (MIT)
    │  audio
    ▼
Qwen3-Omni 30B-A3B  ──►  tool call  ──►  Agente de conocimiento (datos del cliente, solo lectura)
    │  audio de respuesta                 │
    │◄────────────────────────────────────┘
    ▼
Reproducción en streaming  ·  barge-in: el VAD corta la respuesta si el usuario interrumpe
```

**Nota sobre la interrupción:** Qwen3-Omni conversa por turnos. La interrupción del usuario (barge-in) se resuelve en la capa de orquestación —Pipecat—, que corta la síntesis en curso cuando el VAD detecta habla. Es el mismo mecanismo que usan los asistentes comerciales.

**Alternativa de respaldo:** si en las pruebas el comportamiento en tiempo real no alcanza, se desacopla en **cascada** con el mismo proveedor: Qwen3-ASR 1.7B (reconocimiento) + el LLM del agente + Qwen3-TTS 1.7B (síntesis). Los tres son Apache 2.0 y con español. La cascada es más fácil de medir y de auditar por etapa.

---

## 5. Hardware y costo

| Escenario | Configuración | Referencia de costo |
|---|---|---|
| On-premise del cliente | 1× GPU 32 GB (RTX 5090 / L40S) con el modelo en int4 | El servidor ya existe por el agente de texto: **costo incremental de voz ≈ US$ 31/mes** |
| On-premise dedicado (sin servidor previo) | 1× L4 / A10 con el modelo cuantizado | **≈ US$ 448/mes**, con el GPU inactivo el 98,9% del tiempo a este volumen |
| Nube por partes (referencia de comparación) | STT + LLM + TTS gestionados | **US$ 71-95/mes** a 500 conversaciones de 3 minutos |

**Lectura:** el volumen previsto (500 conversaciones/mes de 3 minutos) **no justifica comprar hardware dedicado para voz**. La recomendación económica es colgar la voz del servidor que ya corre el agente de texto. Si el cliente no tuviera ese servidor, convendría arrancar en la nube y migrar por encima de las ~3.100 conversaciones/mes.

---

## 6. Latencia esperada

| Condición | Latencia hasta el primer audio |
|---|---|
| Pipeline local, etapas colocalizadas (referencia de cascada) | **0,75-1,0 s** |
| Qwen3-Omni con vLLM-Omni (TTFP medido) | **0,93 s** |
| Con proveedores hosteados por red (referencia comparativa) | 2,6-3,1 s |
| Tool call adicional | +0,9-1,1 s |

**Compromiso propuesto al cliente:** respuesta hablada en **menos de 2 segundos** para consultas que no requieren tool call, y **menos de 3,5 segundos** cuando el agente debe consultar datos.

---

## 7. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| **Nombres propios mal reconocidos** (locales, marcas) | El agente responde sobre el local equivocado | El error en nombres es 3-4× el WER general. Se corrige con sesgo léxico del top-10 + corrección difusa contra el catálogo de locales. **Es el punto a validar primero** |
| Español rioplatense y voseo | Naturalidad percibida, sesgo dialectal | Prueba con 200-300 clips reales del shopping antes de prometer |
| Qwen3.5-Omni cerrado | Riesgo de discontinuidad | Fijar versión en contrato; el modelo corre on-premise, no depende de una API |
| Interrupción mal resuelta | El agente registra como acuerdo algo que no lo fue (se observó en 3 de 15 llamadas con configuración por defecto) | Revisar qué se incorpora al contexto, no solo cortar el audio |
| Audio telefónico a 8 kHz | Peor reconocimiento | Limitar el alcance inicial a navegador/web (16 kHz) |

---

## 8. Qué se solicita aprobar

1. **Modelo:** Qwen3-Omni 30B-A3B (Apache 2.0) servido con vLLM-Omni.
2. **Capa de orquestación:** Pipecat + Silero VAD para turnos e interrupción.
3. **Fase de validación de 2 semanas** antes de comprometer plazos con el cliente: 200-300 clips reales, medición de error en nombres de locales, y prueba de latencia con el transporte definitivo.
4. **Criterios de aceptación:** error global de transcripción ≤8%, error en nombres ≤15%, latencia p95 ≤3,5 s, y prueba de interrupción en 20 llamadas simuladas.

---

## Anexo — Fuentes principales

- Model card y technical report de Qwen3-Omni (Alibaba, sep-2025), incluida la disponibilidad de function calling sobre audio.
- Documentación de vLLM-Omni: TTFP de 0,934 s y latencia E2E de 23,78 s en modo request offline; 336,10 s por el camino de Transformers en A100.
- arXiv 2609.21967 — NemotronLabs VoiceChat, primer full-duplex abierto con tool calling.
- Investigación de Haru-4B (higurashi, nov-2026): pesos Apache 2.0, 6 idiomas con español primario, modelo base sin instrucciones.
- Estudio de latencia y turn-taking en agentes de voz en español (arXiv 2611.19118, nov-2026): 2.616 ms p50 en Pipecat y 3.090 ms en LiveKit con stack hosteado; 0,75-1,0 s con etapas locales.
- Catálogo de modelos full-duplex (fullduplex.ai) y benchmarks Full-Duplex-Bench, VoiceBench, τ-Voice.
- KeyASRBench (nov-2026): error en nombres propios 3-4× el WER general.
- Modelo de costos self-hosted vs. nube, con break-even en ~3.100 conversaciones/mes.
