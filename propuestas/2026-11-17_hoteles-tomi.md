# Presupuesto — Hoteles Tomi (agentes de voz)

**Base:** notas de reunión `HOTELES TOMI` (Drive) + criterio de cotizar los dos agentes por separado.

## 1. Qué pidieron

Cadena de **8 hoteles** en Argentina.

**Agente 1 — Leads / recepcionista.** Responde WhatsApp 24/7: consultas de disponibilidad, tarifas, reservas. Es el más simple y el que conviene vender primero.

**Agente 2 — Interno.** Responde preguntas de áreas administrativas, contador y finanzas. También compara con Booking y la competencia.

**El problema que los desvela:** la **tarifa promedio real**. La ocupación sale fácil del PMS, pero la tarifa promedio hoy está mezclada (pesos y dólares, netas y comisionables). Quieren que el agente les devuelva un solo valor real. Es lo de más valor y lo más complejo — va como módulo aparte.

**Dato técnico:** PMS **CQR** sobre **AWS** (cqr.com.ar).

## 2. Cómo se estructura el presupuesto

### Agente 1 — Leads / recepcionista WhatsApp (vendible primero)
**Costo variable real por conversación:**
- WhatsApp Business API: cobra por conversación de 24 h (tarifa distinta por categoría: marketing / utility / service). En LatAm las de servicio son las más baratas, pero se pagan.
- STT + TTS por minuto si el agente es de voz; si es solo texto, no aplica.
- Inferencia del modelo: variable por token, salvo que corra on-premise.
- Telefonía: solo si además contesta llamadas.

**Estructura de precio:** setup + fee mensual por hotel (u 8 hoteles en paquete) + bolsa de conversaciones incluidas y excedente por conversación.

### Agente 2 — Interno / administrativo
**Costos:**
- Conexión a PMS CQR (definir si hay API o si es base de datos directa — esto define el esfuerzo y hay que confirmarlo antes de cerrar precio).
- Integración con Google Workspace (Sheets y mail donde registran la recepción).
- Criterio de negocio: qué es una tarifa neta, qué comisionable, cómo se descuenta IVA y comisión.

**Estructura de precio:** setup (más alto que el agente 1 por la integración al PMS) + fee mensual + horas de configuración del criterio.

### Módulo 3 — Tarifa promedio real
Es el producto caro y el que justifica todo. Se cotiza aparte: setup de la lógica de negocio + fee mensual por hotel o por cadena.

## 3. Decisiones que hay que tomar antes de mandar el número

1. **¿Ocho presupuestos o uno por cadena?** Recomiendo uno por cadena con precio por hotel decreciente: les simplifica la decisión y te asegura las 8 licencias.
2. **¿Quién paga el consumo de WhatsApp?** Si lo pagás vos, el margen se te mueve con el volumen. Cobralo aparte o con una bolsa incluida.
3. **¿Hay API del PMS CQR?** Si no hay, el esfuerzo de integración se multiplica. No cerrar precio sin esto.
4. **¿On-premise o nube?** Si es on-premise (coherente con el discurso de datos que no salen), sumás hardware/servidor al setup.
5. **¿Incluye soporte 24/7 o horario comercial?** El agente 1 promete 24/7 hacia el huésped; el soporte humano no tiene por qué serlo.

## 4. Costos a cubrir (para que el precio no se coma el margen)

- Conversaciones de WhatsApp Business API.
- Inferencia del modelo (por token o servidor propio).
- STT/TTS si hay voz.
- Horas de configuración del criterio tarifario.
- Mantenimiento de la integración al PMS (los proveedores cambian cosas).
- Soporte y monitoreo.

## 5. Próximo paso sugerido

1. Confirmar con Tomi si hay API de CQR antes de dar número.
2. Mandar **solo el Agente 1** como entrada (es el que se vende rápido y no depende del PMS).
3. Ofrecer el módulo de tarifa promedio como upgrade con nombre propio.
