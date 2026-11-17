# Recomendación técnica — Interfaz de voz para el Agente de Conocimiento

**Preparado para:** Gerencia / equipo técnico
**Fecha:** 17 de noviembre de 2026
**Objeto:** definir el modelo de audio open source para que el Agente de Conocimiento sea consultado por voz y responda por voz, en español, dentro de la infraestructura del cliente.

---

## 1. Recomendación

**Qwen3-Omni 30B-A3B (Alibaba), Apache 2.0, servido en producción con vLLM-Omni.**

Un solo modelo recibe voz, razona, **ejecuta herramientas sobre los datos del cliente** y responde con voz en español. Es el único modelo de pesos abiertos que reúne esas cuatro condiciones sin restricciones comerciales.

---

## 2. Sobre el requisito de "bidireccional": qué resuelve y qué no

Es el punto que hay que definir bien, porque la palabra se usa para dos cosas distintas:

| Sentido | ¿Qwen3-Omni lo hace? | ¿Lo necesita el caso? |
|---|---|---|
| **Conversación de ida y vuelta en un mismo modelo** (audio entra → audio sale, sin TTS separado) | **Sí** | **Sí, es el requisito** |
| **Simultaneidad total** (hablar mientras escucha, como una llamada humana) | **No**: conversa por turnos con streaming e interrupción | **No aporta valor acá** |

**Por qué la simultaneidad no es un requisito en este caso.** Un agente de conocimiento se usa para preguntar y recibir una respuesta con datos. El usuario formula su consulta, el agente consulta el sistema y contesta. La simultaneidad es valiosa en conversación social o en atención telefónica de alto volumen; en un caso de consulta agrega complejidad y resta precisión, porque el modelo tiene que decidir cuándo hablar en vez de cuándo responder bien.

**Lo que sí se implementa y el usuario percibe:** respuesta hablada en streaming y **barge-in** — si el usuario interrumpe, el agente se calla en el acto y escucha. Se resuelve en la capa de orquestación (detección de voz), no en el modelo.

**Lo que hay que decir de frente:** los modelos de full-duplex nativo (Moshi, PersonaPlex, Nemotron VoiceChat, Haru) existen y son open source, pero **ninguno combina español con ejecución de herramientas**. Un modelo que escucha y habla a la vez pero no puede consultar los datos del shopping no cumple la función del producto.

---

## 3. Ficha técnica del modelo

| Atributo | Dato |
|---|---|
| Nombre | **Qwen3-Omni-30B-A3B** (variante Instruct) |
| Autor | Alibaba, equipo Qwen |
| Fecha | Septiembre 2025 |
| Licencia | **Apache 2.0** (pesos y código, uso comercial sin regalías) |
| Arquitectura | Mixture of Experts: 30B totales, ~3B activos, con módulo *talker* de generación de voz |
| Modalidades | Texto, imagen, audio y video de entrada; **texto y voz de salida** |
| Idiomas de entrada de voz | 19 |
| Idiomas de salida de voz | **10, incluido español** |
| **Ejecución de herramientas** | **Sí: function calling nativo sobre audio** (el modelo decide llamar la herramienta a partir de una pregunta hablada) |
| Servido en producción | **vLLM-Omni** con streaming de audio. TTFP medido: **0,934 s** |
| Memoria | bf16 no entra en una GPU; **int4 ≈ 20,3 GB** |
| Adopción | 4.116 estrellas en GitHub · **347.566 descargas** |
| Continuidad | **Qwen3.5-Omni salió solo por API, sin pesos.** Éste es el último de la línea abierta: fijar versión en el contrato |

---

## 4. Comparación con las alternativas evaluadas

| Modelo | Pesos abiertos | Español | Herramientas | Un solo modelo | Despliegue probado | Veredicto |
|---|---|---|---|---|---|---|
| **Qwen3-Omni 30B-A3B** | **Sí (Apache 2.0)** | **Sí (voz)** | **Sí, nativo** | **Sí** | Sí (vLLM-Omni) | **Recomendado** |
| Nemotron VoiceChat 11B | Sí (OpenMDW) | No (inglés) | Sí | Sí | Medio | Mejor dúplex abierto, sin español |
| Haru-4B | Sí (Apache 2.0) | Sí | **No** (modelo base) | Sí | Bajo (research) | Dúplex real, sin herramientas ni instrucciones |
| Moshi | Sí | No | No | Sí | Sí | Referencia histórica, inglés |
| PersonaPlex | Sí | No | No | Sí | Medio | Voz y personaje, inglés |
| MiniCPM-o 4.5 | Sí | No | No | Sí | Sí | Liviano, sin español |
| Cascada (ASR + LLM + TTS) | Sí | Sí | Sí | **No (3 piezas)** | Sí | Plan B: más auditable, más piezas |

**El argumento central:** de todos los modelos con pesos abiertos, **solo Qwen3-Omni habla español y ejecuta herramientas en el mismo modelo**. Las alternativas obligan a elegir: o español sin herramientas (Haru), o herramientas sin español (Nemotron), o tres modelos encadenados (cascada).

---

## 5. Arquitectura propuesta

```
Usuario (voz)
    │
    ▼
Detección de voz — Silero VAD (MIT)
    │  audio
    ▼
Qwen3-Omni 30B-A3B  ──►  function call  ──►  Agente de Conocimiento
    │  voz de respuesta                        (datos del cliente, solo lectura)
    │◄──────────────────────────────────────────────┘
    ▼
Audio en streaming  ·  barge-in: el VAD corta la respuesta si el usuario interrumpe
```

**Componentes:** 1 modelo (Qwen3-Omni) + 1 capa de detección de voz + el agente que ya existe. Nada más.

---

## 6. Hardware y costo

| Escenario | Configuración | Costo de referencia |
|---|---|---|
| On-premise sobre el servidor actual | 1 GPU 24-32 GB (RTX 5090 / L40S), modelo en int4 | **≈ US$ 31/mes incremental** |
| On-premise dedicado | 1× L4 / A10 | ≈ US$ 448/mes |
| Comparación: cloud por partes | STT + LLM + TTS gestionados | US$ 71-95/mes a 500 conversaciones |

A 500 conversaciones de 3 minutos por mes el GPU queda inactivo el 98,9% del tiempo: **la voz debe colgarse del servidor que ya corre el agente de texto.**

---

## 7. Latencia

| Condición | Latencia hasta el primer audio |
|---|---|
| Qwen3-Omni con vLLM-Omni (TTFP medido) | **0,93 s** |
| Con function call adicional | +0,9-1,1 s |
| Referencia de cascada local colocalizada | 0,75-1,0 s |

**Compromiso propuesto:** respuesta hablada en **menos de 2 s** para consultas directas y **menos de 3,5 s** cuando el agente debe consultar datos.

---

## 8. Plan de ejecución

| Fase | Duración | Entregable | Criterio de aprobación |
|---|---|---|---|
| **0. Prueba técnica** | 1 semana | Qwen3-Omni en vLLM-Omni, on-premise, conversando en español con function call al agente | Responde por voz y ejecuta una tool con datos reales |
| **1. Integración con el agente** | 2 semanas | Voz conectada al RAG del cliente, con permisos y solo lectura | 20 preguntas reales respondidas correctamente |
| **2. Turnos e interrupción** | 1 semana | VAD + barge-in calibrado | El agente se calla al interrumpirlo en 20/20 intentos |
| **3. Validación en el cliente** | 2 semanas | Piloto con el área de Relacionamiento | Error en nombres de locales ≤15%; satisfacción ≥4/5 |

**Total: 6 semanas.** Sin etapa de ajuste fino: el modelo ya viene instruido y con herramientas.

---

## 9. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| **No es full-duplex simultáneo** | Se implementa barge-in en la capa de orquestación. Se documenta el alcance por escrito antes de firmar |
| Nombres propios mal reconocidos (locales, marcas) | Es el punto crítico: el error en nombres es 3-4× el error general. Sesgo léxico con el top-10 del piso + corrección difusa contra el catálogo |
| int4 necesario para entrar en una GPU | Validar calidad en int4 en la Fase 0; si degrada, usar una GPU de 48 GB en bf16 |
| Qwen3.5-Omni cerrado | Fijar versión en contrato. El modelo corre on-premise: no depende de una API que pueda cambiar |
| Interrupción mal resuelta | Revisar qué se incorpora al contexto, no solo cortar el audio (se observaron falsos positivos de "acuerdo" en pruebas con configuración por defecto) |
| Audio telefónico a 8 kHz | Alcance inicial por navegador (16 kHz) |

---

## 10. Qué se solicita aprobar

1. **Modelo:** Qwen3-Omni 30B-A3B (Apache 2.0), on-premise, servido con vLLM-Omni.
2. **Alcance funcional:** conversación por voz con respuesta en streaming e interrupción del usuario. Se documenta explícitamente que no hay solapamiento simultáneo, y por qué no es necesario para el caso.
3. **Fase 0 de una semana** para validar español y ejecución de herramientas.
4. **Plan B:** cascada Qwen3-ASR + Qwen3-TTS si en la Fase 0 la latencia o la calidad en int4 no alcanzan.

---

## Anexo — Defensa ante preguntas previsibles

**"¿Es bidireccional?"**
Sí en el sentido que importa: un solo modelo recibe voz y responde con voz, en español. No es simultáneo —no habla mientras escucha— y eso está documentado en la propuesta como alcance. La interrupción del usuario sí está cubierta.

**"¿Por qué no usamos un modelo full-duplex?"**
Porque ninguno combina español con ejecución de herramientas. Los full-duplex abiertos son en inglés (Nemotron VoiceChat, Moshi, PersonaPlex) o son modelos base sin instrucciones ni tools (Haru-4B). Un agente que no puede consultar los datos no cumple el objetivo del producto.

**"¿Qué pasa si sale una versión mejor?"**
El modelo es Apache 2.0 y corre en nuestra infraestructura. Cambiar de modelo no requiere cambiar la integración ni rehacer el agente: la voz es una capa sobre el agente existente.

**"¿Es caro?"**
Sobre el servidor que ya existe, el costo incremental es de ~US$ 31/mes. No requiere hardware nuevo.

---

## Fuentes

- Model card y technical report de Qwen3-Omni (Alibaba, sep-2025): idiomas, function calling sobre audio, requisitos de memoria.
- vLLM-Omni: TTFP medido de 0,934 s.
- arXiv 2609.21967 — NemotronLabs VoiceChat: primer full-duplex abierto con tool calling (inglés).
- Model card `higurashi-ai/Haru-4B` (12/11/2026): full-duplex con español, modelo base sin instrucciones.
- arXiv 2609.35820 — τ-Multilingual: español a ≤3,2 puntos del inglés en sistemas comerciales; sin modelos abiertos evaluados.
- fullduplex.ai — mapeo de benchmarks: no existe benchmark dedicado de full-duplex en español.
- KeyASRBench (nov-2026): error en nombres propios 3-4× el error general.
- Modelo de costos self-hosted vs. nube, con break-even en ~3.100 conversaciones/mes.
