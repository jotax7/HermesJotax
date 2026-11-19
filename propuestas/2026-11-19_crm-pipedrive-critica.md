# Crítica del borrador CRM — lectura de asesor, no de editor

**Sobre:** `2026-11-19_crm-pipedrive-draft.md` · **Para:** Joaco
**Lente:** ¿esto lo puede leer Rodri en 5 minutos, decidir, y no volver a preguntar?

---

## Veredicto en una línea

**La recomendación es correcta; el documento no está listo.** Le sobran ~40% de páginas, le falta la única página que lo vuelve ejecutable, y tiene tres números de costo que no cierran entre sí — con eso, el socio lo devuelve en la primera lectura y la discusión pasa a ser sobre la aritmética, no sobre el CRM.

---

## 1. ¿Responde la pregunta? Sí, pero contestó otra

La pregunta fue: *"poner Pipedrive para el orden y seguimiento de mis comerciales"*. El documento contesta **"qué CRM comprar"**. Son dos preguntas distintas.

- El 70% del texto es selección de proveedor (precios, planes, comparativa de 7 herramientas). Eso es el 20% del problema.
- El problema real —que no hay un lugar único donde vive el próximo paso de cada deal, ni un ritual semanal que lo haga cumplir— aparece recién en §7 y §9, y nunca se dice con todas las letras.
- La frase que debería abrir el documento es: **"El CRM no te ordena. Te ordena la reunión del lunes; Pipedrive es el soporte de esa reunión."** Si eso no se entiende en la primera línea, el resto es un catálogo.

**Los 20 segundos:** el arranque ("Sí, Pipedrive sirve — Growth, 4 asientos") está bien: hay respuesta clara. El problema es que la respuesta viene con dos datos falsos (el costo es el de 5 asientos, no 4; el "1,3 puntos" no se deriva del ACV que declara), así que la claridad se cae en cuanto alguien agarra una calculadora.

---

## 2. Largo: sobra casi la mitad

Hoy son ~1.900 palabras, 6 tablas y 11 secciones para una decisión de USD 1.900 al año. Joaco se impacienta; Rodri está poco. El documento está escrito para impresionar, no para decidir.

**Sobra (y qué queda en su lugar):**

| Sección | Qué hacer |
|---|---|
| §2 "Qué es Pipedrive hoy" | Dejar 3 líneas: "Growth es el plan mínimo que sirve porque Lite no tiene sync ni automatizaciones". Borrar la tabla de 4 planes, los límites por asiento y el rating de la app. |
| §5 tabla de 7 herramientas | Dejar 3 filas (Pipedrive / Zoho / HubSpot) + Apollo como "opción no comprar". Attio, Close, folk, Salesforce Starter y Kommo van a un pie de página o afuera. |
| §6 tabla 3/5/10 usuarios | Una sola columna: 4 asientos. La tabla de 10 usuarios es para una empresa que no es esta. |
| §8 las 5 métricas | Dejar 2 (cobertura de próxima acción y actividad semanal vs 22/9/3). Las otras tres son tablero de gerente, no de 5 personas. |
| §9 plan de 10 días | Se contradice con la realidad (ver §3 acá abajo). Reemplazar por "plan de 10 horas" o "plan de enero". |
| §10 los 5 errores | Ya están dichos en §1 y §4. Dejar 2: el fundador pidiendo el número afuera, y las 10 etapas. |
| "Lectura honesta", "Tres cosas importan más", "Ruido, no lo crees" | Afuera. Es el registro de un consultor, no el de alguien que conoce la casa. |

**Falta:**

1. **Un deal real recorriendo las etapas.** El Recreo o IRSA, con fechas, monto, próximo paso y el momento en que se estanca. Sin eso, las 6 etapas son genéricas y no se pueden copiar.
2. **El guion de la reunión del lunes (30 min).** Es el artefacto de adopción más importante del documento y no existe. "Primera reunión semanal corriendo desde el CRM" (§9, día 9) no dice qué se pregunta ni en qué orden.
3. **La respuesta a "¿por qué ahora y no en enero?"**
4. **El costo en pesos, quién paga y si va por Appa.** Rodri va a preguntar eso antes que cualquier otra cosa.
5. **Qué pasa con los 27 leads de septiembre y con la contradicción 6 vs 12 clientes.** El documento afirma "12 clientes en producción" cuando el roadmap dice que esa cifra está sin resolver (0.4, dueño Rodri). Poner un número no verificado en un documento para el jefe es la forma más rápida de que lo devuelva.

---

## 3. La recomendación contra las alternativas: el argumento está forzado en tres puntos

**a) El caso económico usa tres ACV distintos.** Es el problema más grave del documento.

| Frase del doc | Implica un ACV de | Pero el pie de página declara |
|---|---|---|
| "0,53 cierres al año" | 15.900 | 24.000 |
| "+1,3 puntos de tasa de cierre" | 16.200 | 24.000 |
| "un tercio de un contrato" | 25.300 | 24.000 |

Con ACV 24.000 y 40 oportunidades, USD 8.432 son **0,35 contratos y 0,88 puntos**, no 0,53 ni 1,3. Los números de equilibrio se calcularon con ~16k y el titular con ~25k.

**b) Se cobra dos veces la implementación.** §6 carga USD 1.500 de "implementación externa" y, en la misma tabla, 45 horas internas de setup. Pero §9 asigna *todas* las tareas a "Vos": no hay implementador externo en el plan. O se paga, o lo hace Joaco — no las dos.

**c) El ACV de 24.000 no sale de ningún lado.** Fulter, el único caso con número: USD 4.500 de entrada + 550/mes = **11.100 el primer año** (hoy 1.350/mes). El Recreo todavía no tiene precio. Con 11.100, el equilibrio es **0,77 contratos/año o 1,9 puntos**, y "un tercio de un contrato" pasa a ser **tres cuartos**.

**Cómo se arregla, y por qué el caso queda mejor:** poner el rango real (11k–24k), una sola columna de 4 asientos, sin doble conteo, y decir: *"cuesta entre USD 5.000 y 7.000 el primer año; se paga con 0,5 a 0,8 clientes más por año. Si cerraste 8 de 40 el año pasado, necesitás cerrar 8,8."* Eso es verificable, es honesto y aguanta que lo miren. El número actual no.

**d) Contra "no comprar" no hay análisis, hay una fila.** Apollo ya está pago, el Sheet es gratis, WhatsApp ya se usa. El documento no cuantifica qué se pierde hoy por no tener seguimiento, así que el upside queda como afirmación ("todo el upside está en el seguimiento") sin un solo deal perdido que lo respalde. La opción "no comprar nada hasta enero" no aparece nunca — y es la más barata y probablemente la correcta para las próximas 6 semanas.

**e) Contra Zoho el argumento es "adopción", y no está probado.** Es el eje correcto, pero se sostiene en una impresión ("interfaz más pesada") sin prueba, sin trial, sin dos vendedores usándolo una semana. Pipedrive tiene **14 días gratis sin tarjeta** — está en su propia página de precios. Recomendar pagar sin usar el trial es lo que hace que un fundador desconfíe.

**f) HubSpot está descartado con un dato viejo.** Hoy Sales Hub Starter (USD 20/asiento) incluye prospecting agent, notetaker y calling con 500 créditos. Eso ataca exactamente el cuello de botella (22–34 llamadas por semana), y el documento lo despacha como "trampa de precio" sin mencionarlo. Cualquiera que abra la página de HubSpot va a verlo.

**g) Dato verificado, por si se usa:** WhatsApp en Argentina cuesta **USD 0,0618** por plantilla de marketing y **0,0260** por utility/servicio (tarifa Meta vigente 1/10/2026). Los USD 60–100/año del TCO no dicen qué volumen asumen: a 200 plantillas/mes son ~148/año, a 1.000 son ~740. Es la única línea que escala con el uso y es la única sin supuesto declarado.

---

## 4. Lo que va a preguntar el socio (y el documento no contesta)

1. **"¿Por qué ahora, en el medio del sprint?"** — la más difícil. Faltan 6,7 semanas, la meta ya no cierra con 3 pilotos/semana sino con 4,5 (34 llamadas y 13,6 demos por semana), y el plan le pide al que tiene que hacer esas demos que se pase **7,5 horas por semana configurando** (50 h / 6,7 semanas). El documento no reconoce ese conflicto.
2. **"¿Cuánto es en pesos y quién paga?"** — contesta "resolverlo con el contador". Eso no es una respuesta, es una derivación.
3. **"¿Quién lo administra y qué deja de hacer?"** — dice "nombrar un dueño" y no dice quién ni a costa de qué. Si la respuesta es Joaco, el documento se contradice solo.
4. **"¿Ya probaste que el equipo lo usa?"** — no hay prueba, hay convicción.
5. **"Vendemos que los datos del cliente no salen, y subimos el pipeline de IRSA a un SaaS yanqui. ¿Cómo lo explicamos?"** — no aparece. Es la pregunta que haría cualquiera del otro lado del mostrador.
6. **"¿Los deals son de Appa o nuestros? ¿Quién factura?"** — el paso 2 de la rueda es "Call con Appa" y Appa factura todo por diseño. El CRM no modela eso y el documento no lo menciona.
7. **"¿Cuántos deals abiertos hay hoy?"** — el documento asume "10-25" en §10 y nunca da el número real. Con 8 deals, seis etapas es decoración.

---

## 5. Lo que delata que lo escribió una IA

No es el vocabulario: es la **simetría**. Todo está prolijo, balanceado y sin una sola duda.

- "Tres cosas importan más que la elección de la herramienta" / "Los 5 errores que matan la adopción" / "Ruido, no lo crees". Listicle de consultoría.
- "El riesgo no es el precio. Es que…" y "La decisión real no es Pipedrive contra HubSpot. Es Pipedrive contra Zoho." La misma figura retórica dos veces en 12 páginas.
- "**Lectura honesta:**" — anunciar la honestidad es la forma más rápida de que no se la crea.
- Cada sección termina con una frase en negrita que quiere ser un remate.
- La columna "Veredicto" de §5 ya viene decidida: las 7 herramientas están ordenadas para que gane Pipedrive, y hasta los días de implementación (3-5 vs 5-10) favorecen al elegido sin fuente.
- Precisión falsa: 6.175 / 8.432 / 14.058, "36-50 horas", "12-18 meses". Ninguno tiene de dónde salir, y los tres primeros no cierran entre sí.
- Cero primera persona, cero anécdota, cero "no sé". Nunca dice "hablé con Sabri", "en la call de IRSA pasó esto", "no tengo dato de cuántos deals hay". Un documento humano sobre la propia casa tiene al menos una de esas tres.
- La sensibilidad está puesta en el knob equivocado: mueve la tarifa horaria (que cambia el TCO 19%) y no el ACV (que cambia el punto de equilibrio 2,6×).
- "Fuentes principales" cita Nucleus 2014 para desacreditar los ROI inflados de otros… y después construye el caso sobre supuestos propios presentados con la misma tipografía que los datos verificados.

---

## 6. Orden propuesto

1. **La respuesta** (media página): qué, cuánto, qué decidir hoy, y la advertencia de timing.
2. **Por qué el problema no es el software** (el ritual del lunes + el fundador pidiendo el número afuera). Acá vive el 80% del valor.
3. **La decisión: Pipedrive / Zoho / no comprar todavía.** Tres opciones, un criterio explícito (adopción), y qué evidencia lo resolvería (trial de 14 días, 3 personas, 3 deals).
4. **El proceso en una carilla**, listo para copiar: etapas, criterios de salida, campos, 2 automatizaciones.
5. **Un deal real recorriendo las etapas** (El Recreo).
6. **La reunión del lunes** (30 min, guion).
7. **Costo y punto de equilibrio** (con rango de ACV y sin doble conteo).
8. **Límites de Pipedrive** (5 líneas).
9. **Plan mínimo** y **decisiones que necesito de vos**.
- Anexo: tabla completa de alternativas, precios y fuentes.

Se invierte el orden actual: primero la decisión y el riesgo, después la herramienta. Hoy el lector tiene que llegar a la página 6 para enterarse de que el problema es su jefe.

---

## 7. Los 5 cambios, por impacto

1. **Cambiar la tesis de apertura:** "el CRM no te ordena, te ordena la reunión del lunes". Reordena todo el documento y contesta la pregunta que hizo.
2. **Rehacer el caso económico:** un ACV real con rango, una sola columna de asientos, sin doble conteo, sensibilidad sobre ACV. Sin esto no pasa la primera lectura.
3. **Agregar la opción "no comprar ahora" y la decisión de timing:** 6,7 semanas, 4,5 pilotos/semana, 50 horas de setup. La respuesta honesta puede ser "comprá 3 asientos mensuales y configurá 4 horas, o esperá a enero".
4. **Reparar el mapa de la rueda:** falta "Captar" y "Call con Appa". Si el pipeline arranca en "Calificado", el CRM no puede producir el número de 22–34 llamadas que pide el fundador — y el fundador va a seguir pidiéndolo afuera, que es exactamente el fracaso que el documento anticipa.
5. **Bajar todo a un caso real + el guion del lunes.** Es lo que convierte el documento en algo que se ejecuta sin volver a preguntar.

---

## 8. Listo / no listo

**No está listo para entregar.** Con los números corregidos y las secciones 4 y 6 del orden propuesto, sí: el diagnóstico es bueno y la recomendación se sostiene incluso después de arreglar la aritmética — que es justamente la prueba de que el caso es real y no está forzado.
