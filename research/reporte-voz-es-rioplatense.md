# Voz open source en español rioplatense, self-hosted — estado a noviembre 2026

Cliente: Ciudad Comercial El Recreo (Quito). Requisito: 100% on-premise, datos que no salen, equipo implementador argentino. Foco: español rioplatense/latinoamericano, nombres propios de locales y marcas, code-switching con inglés comercial.

Criterio de este informe: solo números publicados, con fuente. Donde no hay benchmark público, se dice. Nada de "el modelo X es excelente en español" sin número atrás.

---

## 0. Veredicto en dos líneas

**STT:** Qwen3-ASR-1.7B (Apache-2.0) como motor principal del agente + Whisper large-v3-turbo como segunda pasada/contraste, y una capa de léxico del mall (biasing + corrección difusa) por encima. **TTS:** Qwen3-TTS-12Hz-1.7B-Base (Apache-2.0) clonando 3-10 minutos de una locutora rioplatense con consentimiento firmado; CosyVoice 3 0.5B como alternativa de streaming. **Nada de XTTS v2, Fish Audio ni F5-TTS**: licencias no comerciales sobre las salidas.

Y lo más importante: **no hay ningún benchmark público de WER sobre habla conversacional rioplatense de un shopping**. Lo que hay son 150 grabaciones de voseo en un POC y 573 clips de un fine-tune. Cualquier promesa al cliente antes de correr una prueba propia con audio del Recreo es verso.

---

## 1. STT en español: qué números existen de verdad

### 1.1 Tabla comparativa (WER %, más bajo mejor)

La columna "WER ES (LB)" es el promedio de español del *Open ASR Leaderboard* publicado en el paper de octubre 2026, que promedia FLEURS + Common Voice + MLS sobre los mismos audios para todos los modelos. Es la única tabla apples-to-apples que encontré con esta cantidad de modelos abiertos.

| Modelo | Licencia | WER ES (LB 2026) | FLEURS ES | MLS ES | CoVoST ES | Notas |
|---|---|---|---|---|---|---|
| ElevenLabs Scribe v2 (cerrado) | propietaria | **2.33** | – | – | – | techo de referencia, no on-prem |
| Cohere Labs Transcribe | abierta | 2.81 | – | – | – | 491× RTFx |
| **Mistral Voxtral Small 24B** | Apache-2.0 | **3.04** | – | – | – | 4.9% en ES/EN code-switching |
| **NVIDIA Canary 1B v2** | CC BY 4.0 | **3.25** | 2.90 | 2.94 | 3.81 | mejor relación tamaño/calidad en ES |
| Omnilingual ASR LLM 7B v2 (Meta) | Apache-2.0 | 3.44 | – | – | – | 7B, 21× RTFx |
| **OpenAI Whisper large-v3** | Apache-2.0 | **3.65** | – | – | – | baseline universal |
| **Phi-4 Multimodal** | MIT | 3.71 | – | – | – | 5.6B, no rinde mejor que modelos chicos |
| **NVIDIA Parakeet TDT 0.6B v3** | CC BY 4.0 | **3.73** | 3.45 | 4.39 | 3.41 | 1720× RTFx, el más rápido |
| **Qwen3-ASR 1.7B** | Apache-2.0 | **3.87** | n/d | n/d | n/d | Qwen no publica WER por idioma |
| **Whisper large-v3-turbo** | Apache-2.0 | n/d (no está en el LB) | 2.98 | 2.51 | 3.30 | mejor evidencia rioplatense (ver 1.3) |
| Granite Speech 3.3 8B (IBM) | Apache-2.0 | n/d | n/d | n/d | n/d | sus tablas están sólo en imágenes |
| Audio8-ASR 0.1B + SFT rioplatense | **CC BY-NC 4.0** | 12.39 (573 clips AR) | – | – | – | no comercial |
| BSC whisper-large-v3-LoS | Apache-2.0 | n/d | – | – | – | entrenado con corpus argentino, sin WER ES |

Fuentes: [1] para la columna LB; [2] turbo FLEURS/MLS/CoVoST; [3] Parakeet; [4][5] Canary; [6] Qwen3-ASR; [13] surus; [14] BSC.

### 1.2 Lo que estos números NO dicen

- **Son español neutro/leído.** FLEURS es lectura de Wikipedia, MLS es audiolibros, Common Voice es gente leyendo frases. Nada de mostrador de shopping, nada de ruido de food court, nada de voseo espontáneo.
- **3.65% vs 3.04% no es una diferencia que el cliente vaya a notar** si el audio es malo. Entre los 3% y los 4% de WER, la variable que domina es el micrófono y el ruido, no el modelo.
- **Qwen3-ASR no publica WER de español.** Su tabla multilingüe es un macro-promedio sobre 12 idiomas: MLS 8.55, CommonVoice 9.18, FLEURS 4.90 (1.7B). No hay forma de saber desde el paper cuánto de eso es español. El 3.87% del LB es de un tercero, no de Alibaba.
- **Granite Speech 3.3** soporta español desde la revisión 3.3.2 pero publica las tablas como PNG sin número por idioma. **No hay benchmark público de Granite en español; a validar con prueba propia.**
- **Voxtral 3** (nov 2026) declara SOTA "incluyendo español" y superar a Whisper, Scribe v2 y Gemini 3.5 Transcribe, pero **no publica un solo WER por idioma en el anuncio** [9]. Es self-deployable, no open weights: es una licencia comercial de Mistral.

### 1.3 La única evidencia rioplatense real que encontré

Un POC independiente (local-whisper-mcp) con referencias humanas, sobre FLEURS es_419 y sobre un set propio de **español argentino** (150 grabaciones con voseo) [12]:

| Test set | Whisper large-v3-turbo | Gemma 4 E4B | Whisper small | Whisper base |
|---|---|---|---|---|
| FLEURS Spanish | **2.8%** (2.3–3.4) | 5.0% | 5.7% | 11.2% |
| Argentinian Spanish | **3.3%** (2.6–4.1) | 4.8% | 8.2% | 16.0% |
| Argentinian voseo | **4.9%** (3.9–6.2) | 9.2% (3.4% con prompt dialectal) | 11.5% | – |

Dos hallazgos que importan para el Recreo:

1. **El WER sube ~50% al pasar de español neutro a rioplatense** (2.8% → 3.3%, y 4.9% en las frases con voseo). No es dramático, pero es la señal de que el acento cuesta.
2. **Los modelos normalizan el dialecto.** Whisper conservó 93 de 125 formas de voseo (74%); Gemma 4 sin prompt, 53 (42%) y escribió "puedes" por "podés" 36-39 veces. Con un prompt que nombra el dialecto, Gemma subió a 123/125 y bajó a 3.4% de WER en voseo, ganándole a Whisper por 1.6 puntos. **O sea: el prompt de dialecto sirve, y Whisper también pierde voseo.** Si el agente va a repetir "¿vos querés que te reserve?" y transcribe "¿tú quieres?", el TTS va a leer neutro y el cliente lo va a notar.

Modelos específicos de español que existen:
- **BSC-LT/whisper-large-v3-LoS** (Barcelona Supercomputing Center, Apache-2.0): fine-tune de large-v3 sobre 8.110 h en español/catalán/gallego/euskera, con el *Argentinian Spanish Speech Dataset* (openslr 61) adentro. **No publica WER de español** (sólo catalán 0.96). Es el candidato más serio para fine-tunear nosotros.
- **surus-ai/audio8-asr-0.1b-es-rioplatense**: SFT completo sobre Audio8-ASR-0.1B, 12.39% WER / 5.25% CER en 573 clips argentinos held-out, contra 64.76% del base zero-shot. Sirve como prueba de que **con SFT se puede bajar muchísimo en rioplatense**, pero es un modelo de 0.1B no comercial y con techo de ortografía fina.
- No encontré ningún modelo open weights entrenado específicamente en español de Ecuador.

### 1.4 Ruido de deploy real (no de paper)

- **Whisper confunde español con portugués** y degrada detección de idioma: discussion #1331 del repo de Whisper, gente reportando degradación "dramática" en español [31]. Con `language="es"` forzado se mitiga; con autodetección, no.
- **Parakeet v3 rompe el pipeline con palabras españolas**: issue #14854 de NeMo, `get_words_offsets()` falla con "¡Hola!" — el signo de apertura español [30]. Es un bug de tokenización que aparece justo cuando armás timestamps por palabra.
- **Qwen3-ASR en streaming puede derrapar de idioma**: discussion #127, audio chino transcrito como español en bucle [32]. Es streaming, no offline, pero si el agente va a ser full-duplex hay que testearlo.

---

## 2. Nombres propios: el problema real del Recreo

### 2.1 La evidencia

**El WER no mide lo que le importa al cliente.** KeyASRBench (nov 2026) mide *Keyword Error Rate* sobre frases completas — nombres, productos, versiones — en un set bilingüe ZH/EN [15]:

| Sistema | KER control (ciego) | KER challenge 10 h | WER/MER del set |
|---|---|---|---|
| StepAudio 3 ASR Max | **10.65%** | 13.61% | 5.31–12.91% |
| Qwen3-ASR-1.7B | 15.74% | 24.88% | idem |
| GLM-ASR-Nano | 21.30% | 32.50% | idem |
| Qwen3-ASR-0.6B | 24.54% | 33.81% | idem |
| **Whisper large-v3-turbo** | **27.31%** | 31.29% | idem |

Traducido: **el error en nombres propios es 3 a 4 veces el WER**. Un modelo con 3% de WER puede estar errando 1 de cada 4 nombres. Ejemplo textual del paper: Qwen3-ASR-1.7B transcribe "Claude Code" como "Cloud Code" con 1.69% de WER en esa oración — la métrica de secuencia casi ni lo registra, pero el nombre del producto se perdió.

Eso es exactamente el caso "el POI del mall", "el local de Adidas", "el food court", "la tienda de Claro". Y es peor en español porque los nombres de marca suelen ser anglicismos pronunciados a la española.

**En español hay un antecedente académico específico**: corrección ortográfica de entidades nombradas en *voice queries* en español (UC3M) — el paper parte de que los ASR "no son capaces de reconocer entidades que no están en su vocabulario" [36]. Es de antes de los LLMs de audio, pero el diagnóstico sigue vigente.

### 2.2 Qué funciona para mitigarlo

| Técnica | Evidencia concreta | Costo / límite |
|---|---|---|
| **Biasing por lista (trie/word-boosting)** | Reduce el WER de las palabras sesgadas **hasta 88% relativo** y deja el resto casi intacto [16] | requiere motor que lo soporte (NeMo word boosting, Qwen context, Voxtral 3) |
| **Prompt de contexto en Whisper** | Whisper sólo acepta ~224 tokens de prompt y sesga la primera ventana; con fine-tune específico para "contextual biasing instruction" se logra **45.6% de mejora en palabras raras** y 60.8% en palabras no vistas en el fine-tune [17] | hay que entrenar; el prompt solo se diluye en audios largos |
| **Prompting a un speech LLM** | Funciona muy bien en habla leída, **pero se cae con la cantidad de distractores**: con 250 palabras en la lista el WER de las palabras objetivo empeora **39% a 570% relativo** [16] | letal para un mall con 150 locales |
| **Fine-tuning / LoRA con léxico del dominio** | el SFT rioplatense bajó de 64.76% a 12.39% de WER [13] | necesita 10-30 h de audio etiquetado |
| **Corrección posterior (fuzzy + LLM + catálogo)** | es lo que hace producción en todos lados; KeyASRBench lo lista como práctica estándar (hotwords, retrieval, n-best reranking, post-corrección) [15] | latencia extra; nunca corrige lo que no está en el catálogo |

**Conclusión operativa:** para el Recreo, la lista de locales es grande (>100). Eso es *precisamente* el régimen donde el prompting a un speech LLM colapsa y el biasing clásico aguanta. La arquitectura correcta es: biasing con lista corta por contexto (los 10 locales del piso donde está el usuario, no los 150) + post-corrección contra el catálogo con fuzzy matching fonético en español.

---

## 3. TTS en español: qué suena bien de verdad

### 3.1 Tabla comparativa

| Modelo | Licencia pesos | Español | Clonado | WER contenido ES | Elo AA (voz proveedor) | Notas |
|---|---|---|---|---|---|---|
| **Qwen3-TTS 12Hz-1.7B-Base** | **Apache-2.0** | sí (10 idiomas) | 3 s de audio | **1.126** | no rankeado | WER casi igual a ElevenLabs (1.084) y MiniMax (1.029) |
| Qwen3-TTS 12Hz-0.6B-Base | Apache-2.0 | sí | 3 s | 1.491 | no rankeado | streaming 97 ms |
| **CosyVoice 3 0.5B (+DiffRO)** | **Apache-2.0** | sí (9 idiomas) | zero-shot | **2.99** | no rankeado | streaming 150 ms; MOS subjetivo sólo zh/en |
| Audio8-TTS 0.6B | Apache-2.0 | sí (22 idiomas) | sí | 3.39 (SIM 0.668) | no rankeado | corre en Android/LiteRT |
| Chatterbox Multilingual V3 | **MIT** | sí (23 idiomas) | sí | n/d | 1023 (modelo EN) | **marca de agua PerTh en cada archivo**; sin mantenimiento |
| Kokoro 82M | Apache-2.0 | **sólo 3 voces** (1F 2M) | no | n/d | **1064** (EN) | Elo altísimo en inglés, español muy limitado |
| Piper | motor **GPL-3.0**, voces por licencia | es_AR: **una sola voz** ("daniela") | no | n/d | no rankeado | para embedded, no para un agente comercial |
| XTTS v2 | **CPML (no comercial)** | 17 idiomas | sí | n/d | 915 | descartado por licencia |
| Fish Audio S2 Pro | **Research License** | 80+ | sí | n/d | **1108** | el mejor Elo abierto, **no se puede usar** |
| Breeze TTS 2 | research / NC | EN/ZH | – | n/d | 1228 | tope abierto, no comercial |
| Voxtral 4B TTS | **CC BY-NC 4.0** | sí | sí | n/d | – | hereda NC de las voces de referencia |
| F5-TTS | MIT código / **CC BY-NC pesos** | **no evaluado en ES** | sí | – | – | en CV3-Eval figura como "–" (sin soporte) |

Fuentes: [19] licencias + Elo; [20] Qwen3-TTS; [21][22] CosyVoice 3; [23] Audio8-TTS; [27] Kokoro; [28] Piper; [26] XTTS.

### 3.2 Naturalidad y prosodia: qué hay y qué no

- **No existe un ranking público de naturalidad en español que incluya modelos abiertos.** Artificial Analysis lanzó arenas multilingües en septiembre 2026 con español, pero el podio es todo propietario: Cartesia Sonic 3.6 primero en español, alemán y francés [37]. Los Elo de la tabla (Kokoro 1064, XTTS 915, Fish 1108) son del leaderboard de **voces nativas en inglés**, no de español. Comparar un modelo abierto contra otro por esos números en español **no es válido**.
- **Lo que sí es medible en español es inteligibilidad**: el WER de contenido (transcribir lo generado y comparar). Ahí Qwen3-TTS está a la par de los comerciales (1.126% vs 1.084% de ElevenLabs) y CosyVoice 3 está dos puntos atrás. Inteligibilidad ≠ prosodia: un TTS puede ser perfectamente inteligible y sonar a locutor de aeropuerto.
- **El problema del acento no es teórico.** Issue #268 de Chatterbox: en español el modelo pronuncia la "c" siempre como /s/ ("cocinar" → /kosiˈnaɾ/) sin importar el audio de referencia, y el autor reporta que no hay forma de forzar el acento peninsular ni fijar el dialecto desde el clon [24]. Para Argentina el seseo es correcto, así que Chatterbox "acierta" por default — pero el mismo mecanismo significa que **no podés confiar en que el clon respete el acento rioplatense** si la referencia es rioplatense y el modelo deriva.
- **El consenso de los foros es que ningún modelo abierto separa bien dialectos del español.** En r/LocalLLaMA: "ninguno parece separar claramente el español [por dialecto]", y el hilo específico "TTS open source para clonar voces en español argentino para uso comercial" terminó sin una respuesta concreta, con recomendaciones de GPT-SoVITS y forks de Chatterbox [34][35]. Eso es señal, no prueba.
- **Piper y Kokoro no son opción para el Recreo**: Kokoro tiene 3 voces españolas fijas (sin clonado), Piper tiene **una** voz es_AR. Un shopping que quiere la voz de su locutora no puede usar eso.

### 3.3 Lo que hay que asumir

Que un TTS abierto clonado de una locutora rioplatense suene rioplatense **no está garantizado por ningún benchmark**. Se valida grabando 3-10 minutos de referencia, generando 30 frases con nombres del mall y haciendo escucha ciega. Punto.

---

## 4. Clonado de voz y licencias

### 4.1 Qué se puede usar comercialmente

| Modelo | Licencia de pesos | ¿Uso comercial? | ¿Clonado comercial? | Trampa |
|---|---|---|---|---|
| Qwen3-TTS (todas las variantes) | Apache-2.0 | sí | sí | sin restricción explícita de consentimiento en la card: la responsabilidad es tuya |
| CosyVoice 3 | Apache-2.0 | sí | sí | ídem |
| Kokoro 82M | Apache-2.0 | sí | no clona | sin clonado |
| Audio8-TTS 0.6B | Apache-2.0 | sí | sí | ídem |
| Chatterbox Multilingual | **MIT** | sí | sí | **toda salida lleva watermark PerTh** (detectable, sobrevive MP3); el proyecto quedó sin mantenimiento |
| Piper | motor **GPL-3.0** | el motor sí, con obligaciones GPL | no | **si lo embebés en un producto, el GPL del motor contamina**; cada voz tiene su licencia |
| Parakeet v3 / Canary v2 (STT) | CC BY 4.0 | sí | n/a | atribución obligatoria |
| **XTTS v2** | **Coqui Public Model License** | **no** | **no** | la licencia dice literal: "allows only non-commercial use of a machine learning model **and its outputs**". Coqui cerró: no hay licencia comercial que comprar |
| **Fish Audio S2 Pro** | **Fish Audio Research License** | **no** | **no** | pide acordar uso no comercial |
| **F5-TTS** | código MIT / **pesos CC BY-NC 4.0** | **no** | **no** | el código libre no sirve sin pesos |
| **Voxtral 4B TTS** | **CC BY-NC 4.0** | **no** | **no** | hereda la NC de las voces de referencia |
| VibeVoice 1.5B | MIT "pero research only" | gris | gris | Microsoft borró el código TTS del repo en sep-2025 |

Fuente principal: [19], contrastado con [26] (texto de la CPML), [25] (watermark de Chatterbox), [33] (licencia Fish).

**Regla práctica:** si el modelo no es Apache-2.0 o MIT, la salida no se puede vender. Eso deja **Qwen3-TTS, CosyVoice 3, Kokoro y Audio8-TTS** como los únicos cuatro utilizables, y de esos, sólo dos clonan bien en español.

### 4.2 Consentimiento y legalidad

- **Consentimiento escrito, sí o sí.** Ninguna de las licencias abiertas te cubre por la voz de una persona: cubren el modelo. La voz es un derecho de la persona (imagen/voz). Para la locutora del Recreo: contrato que autorice explícitamente (a) clonar, (b) usar en agentes conversacionales, (c) por cuánto tiempo, (d) qué pasa si se va de la empresa.
- **Divulgación de que es IA.** Si el audio se publica o se usa en atención al público dentro de la UE, el Art. 50(4) del AI Act obliga a declarar que es contenido generado/manipulado [29]. Para Ecuador no encontré normativa específica sobre voz sintética: **no hay ley local identificable, a validar con abogado** — y si el cliente tiene matriz o clientes en Europa, aplica el AI Act igual.
- **Watermark: a favor o en contra.** Chatterbox marca todo con PerTh. Es una buena defensa reputacional ("no lo usamos para deepfakes") y una mala noticia si el cliente quiere el audio "limpio" para pauta.
- **Retención.** Si clonás la voz, guardás un embedding biométrico. Eso entra en la política de datos del cliente y en la conversación de "los datos no salen" — el modelo tiene que correr on-prem **y** el audio de referencia no puede salir de la infra del mall.

---

## 5. Code-switching español-inglés

Este es el punto donde los modelos abiertos se parten. Benchmark: **CoSE-E** (ServiceNow, 2026), 1.212 utterances sintéticas de dominios de empresa, español como idioma matriz (64.2%) e inglés embebido (35.8%) — exactamente "el dashboard de KPIs", "mandá el ticket al back office", "el POI del mall" [18].

| Modelo | WER ES/EN | SWER (semántico) | AER (error de tarea) |
|---|---|---|---|
| ElevenLabs Scribe v2 | **2.2%** | 0.4% | 3.3% |
| Gemini 3 Flash | 2.8% | 0.5% | 3.1% |
| AssemblyAI Universal 3.5 Pro | 2.9% | 0.4% | 3.3% |
| **Qwen3-Omni (open)** | 4.2% | 0.4% | **2.7%** (mejor de todos) |
| Deepgram Nova-3 | 4.2% | 1.3% | 8.8% |
| **Voxtral Small 24B (open)** | 4.9% | 0.5% | 3.6% |
| **Parakeet TDT 0.6B v3 (open)** | **11.7%** | 2.7% | 7.5% |
| **Whisper large-v3-turbo (open)** | **16.1%** | 3.0% | 7.3% |

Hallazgos que importan:

1. **Whisper no transcribe el code-switching: lo traduce.** Con autodetección de idioma, el paper documenta que traduce en lugar de transcribir el audio mezclado (apéndice D.3). 16.1% de WER contra 3.3% en español monolingüe rioplatense es un salto de 5×. **Forzar `language="es"` ayuda pero no lo arregla**: en un tramo en inglés el modelo va a castellanizar o traducir.
2. **Parakeet se cae a 11.7%** (vs 3.73% en ES monolingüe). Es el precio de un modelo de 600M con tokenizer único para 25 idiomas.
3. **Voxtral Small 24B es el mejor trade-off abierto**: 4.9% de WER y 3.6% de AER, casi el nivel de los cerrados. Pero 24B.
4. **Qwen3-Omni gana en AER** con el peor WER del top-4: transcribe peor la superficie pero preserva mejor el significado. Para un agente que tiene que *entender* y ejecutar (no producir subtítulos), el AER es la métrica que importa.
5. **Qwen3-ASR (no Omni) no fue evaluado en CoSE-E**, pero en el paper de biasing mostró ser el más robusto a distractores entre los speech LLM (aguanta 10 sin degradar) [16]. Es la mejor apuesta abierta razonable.

Ojo: CoSE-E es español **neutro/latinoamericano sintético**, no rioplatense. Un "POI" dicho por un porteño con yeísmo y voseo no está en ningún benchmark público. **No hay benchmark público de code-switching rioplatense; a validar con prueba propia.**

---

## 6. Stack recomendado

### 6.1 Arquitectura

```
audio (16 kHz)
  └─ VAD (Silero) + segmentación
      └─ STT primario: Qwen3-ASR-1.7B  [language="es" forzado, context biasing con top-10 locales]
          └─ si confidence baja o hay tramo en inglés → segunda pasada Whisper large-v3-turbo
      └─ Post-corrección: fuzzy match fonético español contra catálogo de locales/marcas + LLM chico
      └─ Agente de conocimiento (ya existe)
      └─ TTS: Qwen3-TTS-12Hz-1.7B-Base, voz clonada de locutora rioplatense (3-10 min de referencia)
```

### 6.2 Por qué esa combinación y no otra

- **Qwen3-ASR-1.7B** por tres razones que se sostienen con evidencia: Apache-2.0, KER de 15.74% (el mejor abierto medido, contra 27.31% de Whisper turbo), y robustez a distractores hasta 10 palabras. Su debilidad es que **no hay WER de español publicado** — se apoya en el 3.87% de un tercero.
- **Whisper large-v3-turbo** porque es el único con evidencia rioplatense medida (3.3% en argentino, 4.9% en voseo) y porque corre en cualquier cosa. No como primario por el code-switching.
- **Canary 1B v2 como plan B** si la prueba propia muestra que Qwen falla en acento: 2.90% en FLEURS ES, 978M params, CC BY 4.0. El riesgo es que no está evaluado en code-switching.
- **Qwen3-TTS** porque es el único que combina Apache-2.0 + clonado de 3 s + WER de contenido en español a la par de ElevenLabs (1.126 vs 1.084). **CosyVoice 3 0.5B** si necesitás streaming agresivo (150 ms) y podés pagar 2 puntos más de WER de contenido.
- **Nada de**: XTTS v2 (CPML), Fish (research), F5-TTS (NC en pesos), Voxtral TTS (NC), VibeVoice (research). Y **cuidado con Piper**: el motor es GPL-3.0.

### 6.3 Qué validar antes de prometerle nada al cliente

Protocolo mínimo, con audio del Recreo, no de YouTube:

| # | Prueba | Métrica | Tamaño mínimo |
|---|---|---|---|
| 1 | STT en condiciones reales: mostrador, pasillo, food court, oficina, teléfono | WER global + IC 95% | 200-300 clips de 5-20 s, referencia humana doble |
| 2 | Nombres propios | **KER** sobre 80-120 nombres de locales/marcas + tasa de acierto exacto | los mismos clips |
| 3 | Acento | % de formas de voseo preservadas (como el POC: 93/125) + WER en subconjunto rioplatense | 50-100 clips con voseo |
| 4 | Code-switching | WER + AER en 50-80 frases tipo "el POI del mall", "el dashboard de KPIs", "mandá el ticket" | 50-80 clips |
| 5 | Alucinación | tasa de texto inventado en silencio/ruido (Whisper es famoso por esto) | 20 clips de silencio y ruido |
| 6 | Biasing | ΔWER de nombres con lista de 10 vs 50 vs 150 locales (acá se ve el colapso por distractores) | subconjunto del set 2 |
| 7 | TTS naturalidad | MOS ciego 1-5, 15-20 oyentes, 30 frases con nombres y números del mall | 30 frases × 3 modelos |
| 8 | TTS acento | escucha A/B contra locutora real: ¿suena rioplatense? ¿pronuncia "shopping", "Recreo", "Eloy Alfaro" bien? | 10 oyentes argentinos/ecuatorianos |
| 9 | Licencias | checklist firmado: pesos + voz + watermark + retención | – |

Criterio de corte sugerido (ajustable, pero ponelo por escrito antes): **WER ≤ 8% en mostrador, KER ≤ 15% en nombres de locales, ≥ 70% de voseo preservado, MOS ≥ 3.8**. Si Qwen3-ASR no llega, se fine-tunea con LoRA sobre 10-20 h de audio del mall (la evidencia del SFT rioplatense dice que se puede bajar de 64% a 12% en un modelo chico, así que de 5% a 3% es plausible).

### 6.4 Lo que no hay que prometer

- "Entiende todos los acentos" — no hay benchmark.
- "Reconoce el 100% de los nombres de los locales" — el KER de los mejores sistemas abiertos es 15-25% sin post-corrección.
- "La voz clonada va a sonar exactamente como la locutora" — ningún benchmark de prosodia en español existe para modelos abiertos.
- "Cumple con la ley" — el AI Act aplica si toca la UE; Ecuador no tiene norma específica identificable.

---

## Fuentes

1. Open ASR Leaderboard paper, tabla multilingüe por idioma — https://arxiv.org/html/2510.06961
2. TheWhisper-Large-V3-Turbo, benchmarks multilingües de whisper-large-v3-turbo — https://huggingface.co/TheStageAI/thewhisper-large-v3-turbo
3. nvidia/parakeet-tdt-0.6b-v3 — https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
4. nvidia/canary-1b-v2 — https://huggingface.co/nvidia/canary-1b-v2
5. nvidia/canary-1b (MCV-16.1 ES 3.99) — https://huggingface.co/nvidia/canary-1b
6. QwenLM/Qwen3-ASR — https://github.com/QwenLM/Qwen3-ASR
7. Qwen3-ASR Technical Report — https://arxiv.org/html/2601.21337v2
8. mistralai/Voxtral-Small-24B-2507 — https://huggingface.co/mistralai/Voxtral-Small-24B-2507
9. Voxtral 3 (Mistral, 2026) — https://mistral.ai/news/voxtral-3/
10. ibm-granite/granite-speech-3.3-8b — https://huggingface.co/ibm-granite/granite-speech-3.3-8b
11. Benchmarking ASR Tools for Iberian Languages — https://arxiv.org/html/2609.36920v1
12. POC rioplatense con referencias humanas (FLEURS es_419 + argentino + voseo) — https://github.com/OrihuelaConde/local-whisper-mcp/blob/main/poc/GEMMA-RESULTS.md
13. surus-ai/audio8-asr-0.1b-es-rioplatense — https://huggingface.co/surus-ai/audio8-asr-0.1b-es-rioplatense
14. BSC-LT/whisper-large-v3-LoS — https://huggingface.co/BSC-LT/whisper-large-v3-LoS
15. KeyASRBench (KER) — https://arxiv.org/html/2611.10852
16. Context biasing vs speech LLMs — https://arxiv.org/html/2608.05759v1
17. Improving rare-word recognition of Whisper — https://arxiv.org/html/2502.11572v1
18. CoSE-E (code-switching enterprise ES/EN) — https://arxiv.org/html/2609.35645
19. Cartesia, open-source TTS por licencia (Elo AA nov 2026) — https://www.cartesia.ai/learn/open-source-tts
20. QwenLM/Qwen3-TTS — https://github.com/QwenLM/Qwen3-TTS
21. FunAudioLLM/CosyVoice — https://github.com/FunAudioLLM/CosyVoice
22. CosyVoice 3 paper (CV3-Eval) — https://arxiv.org/html/2505.17589v1
23. Audio8-TTS paper (resultados por idioma) — https://arxiv.org/html/2610.14776
24. Chatterbox issue #268 (acento español) — https://github.com/resemble-ai/chatterbox/issues/268
25. ResembleAI/chatterbox (MIT, PerTh) — https://huggingface.co/ResembleAI/chatterbox
26. Coqui Public Model License (XTTS v2) — https://huggingface.co/coqui/XTTS-v2/raw/main/LICENSE.txt
27. Kokoro VOICES.md (es: 1F 2M) — https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
28. rhasspy/piper-voices (es_AR: sólo "daniela") — https://huggingface.co/rhasspy/piper-voices
29. EU AI Act, Art. 50 — https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50
30. NeMo issue #14854 (Parakeet v3 + "¡Hola!") — https://github.com/NVIDIA-NeMo/NeMo/issues/14854
31. Whisper discussion #1331 (degradación en español) — https://github.com/openai/whisper/discussions/1331
32. Qwen3-ASR discussion #127 (deriva de idioma en streaming) — https://github.com/QwenLM/Qwen3-ASR/discussions/127
33. fishaudio/openaudio-s1-mini (CC BY-NC-SA 4.0) — https://huggingface.co/fishaudio/openaudio-s1-mini
34. r/LocalTextToSpeech, lista TTS 2026 — https://www.reddit.com/r/LocalTextToSpeech/comments/1u3kxxx/
35. r/LocalLLaMA, TTS comercial con voces argentinas — https://www.reddit.com/r/LocalLLaMA/comments/1ods7ff/
36. Corrección de entidades nombradas en voice queries en español (UC3M) — https://e-archivo.uc3m.es/rest/api/core/bitstreams/9c2196cb-c10d-438b-85cd-a81bd4bcc96a/content
37. Artificial Analysis, arenas TTS multilingües (ES) — https://x.com/ArtificialAnlys/status/2102490340678856997
