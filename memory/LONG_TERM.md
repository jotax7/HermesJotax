# LONG_TERM.md — memoria larga de Joaco

> Se lee al inicio de cada sesión (junto con `relations.md`). Acá va lo que no entra en la memoria
> chica: contexto, decisiones tomadas, hilos abiertos y criterios. Lo que se cumple o se descarta, se tacha.
> **Este archivo vive en el repo y se edita acá. No lo pisa el sync.**

## Quién es y qué quiere

- Joaquin Shaw ("Joaco"). Comercial en **BoulderTech** (agentes de conocimiento para shoppings y retail, LatAm; ecosistema Shefa/IRSA, Buenos Aires). **BoulderTech es su trabajo, no su proyecto de vida.**
- Su foco: encontrar **su próxima startup**. Fase de descubrimiento, sin idea cerrada.
- Trabaja por RDP sobre la Raspberry (`/home/bldt`), display :10.
- Prefiere respuestas breves, directas, rioplatense, con fuente y sin halagos.

## Cómo laburamos

- **Tres pistas:** motor comercial BoulderTech · asistente de trabajo · descubrimiento de su startup.
- Todo lo que produzco se versiona en `~/work-os` (repo `jotax7/HermesJotax`, push automático cada 3 días).
- Material crudo del trabajo: Drive → `BOULDER TECH/ESTADO` con fecha. El índice del Drive es la fuente de verdad.
- **Reglas de autonomía:** `~/work-os/AGENTS.md`. Resumen: leer todo, escribir borradores, no enviar ni gastar sin OK.

## Decisiones tomadas

- **16/11** — Google Workspace conectado (Gmail, Calendar, Drive, Sheets, Docs, Contacts). Token `~/.hermes/google_token.json`. Proyecto GCP `hermes-wiggy`, público **Interno** (no vence a los 7 días como Externo en prueba).
- **16/11** — Repo de estado creado y pusheado con deploy key SSH. Sync automático cada 3 días a las 9:30.
- **16/11** — Cherry-pick de 15 skills del repo ECC (`affaan-m/ECC`, MIT). No se corrió su `install.sh`.
- **16/11** — brand-discovery **pausado** para BoulderTech (no es el proyecto de Joaco).
- **16/11** — Experimento FOMO/memecoins con US$ 100: diseñado, en pausa. Él tipia su propia clave.
- **16/11** — Briefing matutino activo: cron 8:30, todos los días, a este chat.

## Criterios de trabajo

- Si un dato contradice a otro, gana el más reciente y se marca la contradicción.
- Separar siempre **hecho / inferencia / recomendación**.
- No inventar cifras. Si no hay dato, se dice "no hay dato".
- Antes de mandar cualquier cosa afuera: mostrar el borrador.

## Hilos abiertos al 16/11

1. **Pricing BoulderTech** — Joaco dice que ya está cerrado (audio 14/11). Nunca lo vi. Falta que me pase los 6 paquetes con montos y moneda.
2. **Pipeline congelado** — 27 leads del CRM con último contacto entre 8 y 15 de septiembre. Nadie los tocó.
3. **Gmail: 4 hilos esperándolo** — Esplendor Asunción ×2 (uno de 27 mensajes), Retail Perú, Dazzler Asunción (POC, 53 días).
4. **El Recreo (Quito)** — Paulina Fuentes prometió el cuestionario el 6/11, sin respuesta. Recordatorio enviado 13/11. Propuesta: ofrecer completarlo en vivo en 20 min.
5. **City Girl** — call comercial 16/11, van a comprar el agente. Dolor: rotación por isla/franquicia sin datos unificados.
6. **Drive desactualizado** — el `CLAUDE TRASPASO` describe OpenClaw, que ya no usan (harness propio).
7. **Contradicción sin resolver** — whitepaper dice 6 clientes en producción; la rueda comercial dice 12.

## Gente del ecosistema

Ver `relations.md`. Núcleo: Rodri Benzaquén (founder/CEO Boulder), Ariel Cohen (PM, mueve las reuniones), Pablo Hegoburu (CTO), Mia (dev de agentes), Emi (backend/servers), Sabri (gerenta comercial de ¡appa!, va a las llamadas), Andre y Tomi (traen clientes).
