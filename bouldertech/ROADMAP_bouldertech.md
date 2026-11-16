# BoulderTech — Roadmap comercial y de producto
**Base:** escaneo completo de Drive, carpeta `BOULDER TECH` (75 ítems) + `JOTAX - BOULDER` + carpeta de traslado de Nataddeo (238 ítems). 24 documentos exportados y leídos. Fecha: 13/11/2026.

---

## 1. Inventario de lo que hay

| Bloque | Contenido | Estado |
|---|---|---|
| `COMERCIAL/` | La rueda comercial (6 pasos), Whitepaper Brief v18/9 (11 págs) | Maduro |
| `COMERCIAL/LEADS/` | LEADS (53 filas), Shoppings CRM Leads (27 filas), leads clic celular/mails | Desactualizado |
| `COMERCIAL/Notas/` | 11 notas de reunión (Forbex, Hoteles Tomi, Pañales Andre, APPA Intelligence 5/11, Reus/Carolina Paraguay, Contrato Sabri) | Rico, sin procesar |
| `COMERCIAL/PRODUCTO/` | Guion de demo (13 preguntas con tiempos), Agentes para shoppings, PROYECTO RETAIL | `PROYECTO RETAIL` vacío |
| `COMERCIAL/CLIENTES/` | Cámara Ecuador (VFINAL completo), Toshify, Karen Lozada, Francisco Diaz, Fulther | Activo |
| `COMERCIAL/Pitchs Decks/` | Deck Ejecutivo, Deck Producto, Presentación Técnica, Cuestionario, Appa Intelligence Retail, Shefa_AI | Listo en PDF |
| `JOTAX - BOULDER/` | Traspaso técnico Claude (15k), AI Discovery Playbook, Notas Grupo Masri | Operativo |

Ruido: 238 archivos en la carpeta de traslado (`ntaddeo@bouldertech.fi…`), muchos duplicados de decks. Conviene consolidar o el Drive deja de ser navegable.

---

## 2. Diagnóstico: 6 hallazgos duros

### H1 — Hay dos pitches compitiendo
- **Whitepaper (18/9):** enterprise LatAm, "no somos vendor de software, somos mall operators", foco IRSA, precio flat, self-hosted.
- **Brief "Hello World":** dos patas (servicio a medida + producto), mid-market/PyME LatAm, stack liviano, referencia TextQL.

Mismo producto, dos puertas. Hoy el outbound en frío habla idioma PyME ("te muestro cómo funciona en vivo") pero los decks que se adjuntan son enterprise. **Decisión:** un guion por segmento, y no mezclar.

### H2 — El paso que factura no tiene dueño
La rueda define 6 pasos y quién los hace. En el **paso 4 "Propuesta y cierre"** el documento dice literalmente *"Quién: Sin definir"* — pero en la tabla de equipo Sabri aparece con pasos 1-2-4. Contradicción interna.

### H3 — No hay precio, y sin precio no hay cierre
- Whitepaper: 3 tiers (Starter/Business/Enterprise) con montos **TBD**.
- Notas Contrato Sabri: pide **6 paquetes** (3 retail local/marca + 3 shoppings), pricing en **anexo sin valores**, valores "a mano" por cliente, ARS + IPC trimestral.
- Cláusula 4.7 (excedente): *"linda pero no dice nada"* — referencia $1.600/mes por hora extra, sin parametrizar.
- Facturación vía entidad en Caimán pendiente de Richard; exportación de servicios desde Argentina sin resolver.

**Este es el cuello de botella #1.** Todo lo demás es ejecución; esto es una decisión que falta.

### H4 — Pipeline congelado hace ~2 meses
Shoppings CRM: 27 contactos, último contacto **8, 9 y 15 de septiembre**. Hoy 13/11.
- 6 "sin respuesta / 1er follow-up" (vencidos desde septiembre)
- 3 "interesado / reunión a coordinar" sin fecha
- 2 "reunión confirmada" sin registro posterior
- 1 "mal contacto", 1 "derivó a William", 1 sin estado

Por país: Ecuador 5 · Colombia 4 · Perú 3 · México 2 · Panamá 1 · Chile 1 · sin país 11.

Y del lado de Gmail (90 días): **4 hilos con el último mensaje del prospecto** esperándote — Esplendor Asunción ×2 (uno de 27 mensajes, otro sobre OPERA Cloud), Retail Perú (reunión agendada) y Dazzler Asunción (POC, 53 días).

### H5 — La meta de 30 pilotos ya no cierra con el calendario original
La rueda cuenta desde el 19/10: 10,4 semanas → 2,9 pilotos/semana, 9 demos/semana, 22 llamadas/semana.

Contando desde hoy (13/11) quedan **6,7 semanas**: para 30 pilotos hacen falta **4,5/semana**, es decir **~13,6 demos/semana y ~34 llamadas/semana** con las tasas de ejemplo (33% demo→piloto, 40% llamada→demo). Eso no lo agenda una sola persona. O se baja la meta, o entra otra fuente de llamadas además de Sabri.

### H6 — Activos ya construidos que no están en el circuito de venta
- **Guion de demo con tiempos reales**: 13 preguntas calibradas (8 en segundos, 2 en 30-90s, 3 pesadas) + aviso de qué no preguntar en vivo. Esto vale oro y **no está en ningún deck**.
- **Cuestionario de discovery** de 5 bloques (sistemas, seguridad/residencia, roles, cultura de datos, definición de piloto).
- **Casos con números**: IRSA (15 shoppings, 23M+ tx, ~180 h/mes, ~100 fraudes), Appa (~100 casos, 200+ tx corregidas), Chocorisimo (120 h/mes), Shefa (reporte de cafetería automatizado).
- **Testimonios de nivel C**: CEO IRSA, CFO Shefa, CMO IRSA, COO IRSA, CTO Appa, Chief of Sales IRSA, CFO Chocorisimo.
- **AI Discovery Playbook** de 3 etapas (negocio → journey → conocimiento).

### Contradicción a resolver antes de salir a vender
El whitepaper dice **6 clientes en producción**; la rueda dice **12 clientes en producción**. Esa cifra es prueba social: hay que fijar la oficial y sostenerla en todos los materiales.

---

## 3. Roadmap 30 / 60 / 90

### Fase 0 — Desbloqueo (13–27 nov)
| # | Acción | Dueño | Salida |
|---|---|---|---|
| 0.1 | Cerrar los 6 paquetes con montos, moneda y qué incluye cada uno | Rodri + Richard | Anexo de pricing en PDF |
| 0.2 | Definir facturación (Caimán vs Argentina) y tratamiento de exportación | Richard | 1 decisión escrita |
| 0.3 | Nombrar dueño del paso 4 (propuesta y cierre) y plantilla única | Rodri | 1 owner + 1 template |
| 0.4 | Fijar la cifra oficial de clientes en producción (6 vs 12) | Rodri | Número único |
| 0.5 | Parametrizar cláusula 4.7 (excedente) | Legal + Richard | Cláusula con número |
| 0.6 | Congelar guion de demo de 20 min usando el doc `DEMO` | Vos | Guion de 1 página |

### Fase 1 — Reactivar (18 nov – 20 dic)
| # | Acción | Métrica |
|---|---|---|
| 1.1 | Barrido del CRM: los 27 contactos reciben toque final o pasan a descartado con motivo | 27/27 cerrados |
| 1.2 | Recuperar los 4 hilos de Gmail pendientes (Esplendor prioritario) | 4/4 respondidos |
| 1.3 | Paquete "Ecuador" replicado a Colombia y Perú (carta + deck + cuestionario + testimonios ya existen en VFINAL) | 2 mercados con material localizado |
| 1.4 | 15 marcas/semana de la lista de ~400 mapeadas, secuencia Apollo por rubro empezando por indumentaria/calzado | 60 contactos en 4 semanas |
| 1.5 | Cada reunión sale con propuesta enviada en ≤48 h y próximo paso con fecha | 100% con fecha |
| 1.6 | Tablero semanal: llamadas, demos, propuestas, pilotos, tasa por etapa | Lunes 9 am |

### Fase 2 — Escalar (dic – feb)
| # | Acción | Por qué |
|---|---|---|
| 2.1 | Vender a la **cámara**, no al mall: el "sector benchmark" del whitepaper (cada afiliado con su agente, indicadores agregados y anónimos) | 1 venta = N afiliados. Ecuador es la prueba viva |
| 2.2 | Módulos cobrables como add-on (ads/performance, cámaras + rango etario, fidelidad, omnicanal) | Cobrar más sin inflar el precio de entrada |
| 2.3 | One-pager de caso por cliente nuevo a los 30 días del go-live, con números | Hoy los 4 casos son todos del ecosistema IRSA/Appa: falta prueba externa |
| 2.4 | Formalizar el modelo de comisión con Appa (contrato Sabri en revisión) | Appa factura todo lo de Boulder por diseño |
| 2.5 | Segundo vertical fuera de shoppings: hotelería (Hoteles Tomi) o construcción (Grupo Masri) como caso semilla | Reduce dependencia de un solo vertical |

---

## 4. Roadmap de producto (según los documentos)

**Hoy en producción**
- Agente de Conocimiento: cálculo real vía pandas/Python sobre la base, no estimación del LLM. Read-only sobre réplica, self-hosted, red privada, permisos por rol, memoria persistente, costo flat.
- Integraciones hechas: SQL Server, Oracle, PostgreSQL, MySQL, Snowflake, Supabase, SAP, HubSpot, Nodum, Excel/Sheets. Un deployment conectó ~200 tablas en 15 bases.
- Canales: web app; WhatsApp/Telegram/Discord vía OpenClaw en los bots.

**En curso / standby**
- Copiloto Zendesk (cliente fintech): en standby por bug de login del cliente (~1000 tickets/día). Propuesta interina: modo read-only/audit para baseline.
- Relay Chatwoot ↔ OpenClaw: probado, falta deploy en la Pi (8080) y **rotar el bearer token que quedó expuesto**.
- Sheets vía service account + gspread: POC, falta Sheet compartido.

**Siguiente (de la nota APPA 5/11)**
- Cerebro (datos) → **ojos** (cámaras, rango etario real en vez de inferido) → **boca/manos** (Ads).
- Proveedores, stock, cobranzas, e-commerce.
- Fidelidad ("Recreo Lovers") y análisis de contratos de alquiler (vencimientos, cláusulas) — ya pedidos en Perú.

**Regla de producto que ya está decidida en las notas:** arrancar simple y sumar módulos cobrables, no inflar el precio inicial.

---

## 5. Riesgos

1. **Dependencia del ecosistema Shefa/IRSA**: 4 de los casos y los dueños son los mismos. El primer caso externo con números es urgente.
2. **Precio flat sin excedente definido**: el cliente puede leer la cláusula y no saber cuánto paga si se pasa.
3. **Pipeline de una sola persona**: si Sabri agenda 34 llamadas/semana, es el cuello. Sin ella, la meta no existe.
4. **Materiales desalineados por segmento** (H1): quema reuniones enterprise con pitch PyME y viceversa.
5. **Cifra de clientes inconsistente** (6 vs 12): en una due diligence o con una cámara, esa diferencia se nota.
6. **Seguridad**: token de OpenClaw expuesto en chat, pendiente de rotación.

---

## 6. Lo que puedo automatizar con lo ya conectado

| Automatización | Qué hace | Frecuencia |
|---|---|---|
| Tablero comercial | Lee Gmail + planillas y arma el estado del pipeline: quién espera, qué venció, qué se movió | Lunes 9 am |
| Radar de respuestas | Detecta respuestas de prospectos y me avisa con resumen + borrador | cada 30 min |
| Brief pre-llamada | Por cada reunión agendada: caso comparable + preguntas de discovery + demo guion | 24 h antes |
| Propuesta en 10 min | Genera la propuesta desde plantilla + anexo de pricing según segmento | on demand |
| One-pager de caso | Convierte un go-live en caso con números y testimonios | 30 días post go-live |

---

## 7. Huecos de información detectados
- `PRODUCTO/PROYECTO RETAIL` y `Notas/mensaje a prospectos` están vacíos.
- `Notas/Hello World` (brief v0) no está versionado: no se sabe si reemplazó al whitepaper o convive.
- No hay documento de pricing con números en ningún lado del Drive.
- No hay registro de propuestas enviadas y su resultado (ganadas/perdidas) — sin eso no se puede calcular tasa real de cierre.
- `Grupo Masri` y `El Recreo` solo existen como notas sueltas de reunión, sin propuesta asociada.
