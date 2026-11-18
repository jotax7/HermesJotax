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
- **Documento vivo en Drive: "Work OS — Joaco"** (id `190mCXyGaxFyBT_DxrClr9BbjRJevT-9LmZ7fVbS8fCw`). Es la fuente de verdad visible para Joaco: estado, decisiones, gente, historia. Actualizarlo cuando haya novedades; no duplicar ahí lo que ya está en este archivo.
- Material crudo del trabajo: Drive → `BOULDER TECH/ESTADO` con fecha.
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
- **Si Joaco dice que algo está hecho, está hecho.** No pedir evidencia, no re-auditar, no insistir. Él tiene los números y el contexto que yo no veo. Preguntar una vez como máximo.
- Esto es una startup: se mueve con criterio del fundador, no con checklists de consultoría.

## Hilos abiertos (actualizado 16/11)

**Cerrados por decisión de Joaco:**
- ~~Pricing~~ — **no aplica**: lo define caso por caso, no hay documento. No volver a pedirlo ni proponer un anexo.
- ~~Pipeline de septiembre~~ — **lista muerta**. Los 27 leads del CRM no se tocan. No proponer barridos ni reactivaciones.
- ~~El Recreo~~ — **en espera pasiva**: hay que esperar que Paulina mande el cuestionario. No mandar más follow-ups.

**Cerrado el 17/11:**
- ~~Presupuesto Fulter (módulo de voz)~~ — terminado y enviado. USD 1.500 setup + 800/mes sobre un abono actual de 550 (pasa a 1.350/mes). Cliente existente, entrada original 4.500 + 550.
- ~~Investigación de modelos de voz~~ — informe consolidado en `research/2026-11-17_voz-bidireccional-INFORME-FINAL.md` + PDF de recomendación Qwen3-Omni.
- ~~Presupuesto El Recreo~~ — terminado e iterado con Sabri.

**18/11:**
- Reunión por Meet con **LM Legales** (estudio de abogados, contacto `adm@lmlegales.com.ar`) para **agregar algo al agente** de conocimiento. Alcance a definir; pedir el detalle de qué módulo quieren.

**Pendientes personales (16/11, repetir hasta tachar):**
- **Hablarle a Migoya — PENDIENTE.** El 18/11 el usuario aclaró que todavía no lo hizo; antes estaba mal marcado como hecho.
- ~~Presupuesto de voz para Tomi~~ — **hecho 18/11**.
- ~~Verificar VRAM del servidor de Fulter~~ — **hecho 18/11**. Ya no bloquea la Fase 0.

**Vivos:**
1. **Gmail: 4 hilos esperándolo** — Esplendor Asunción ×2 (uno de 27 mensajes), Retail Perú, Dazzler Asunción (POC, 53 días). Sin instrucción, no tocar.
2. **City Girl** — call del 16/11, van a comprar el agente. Dolor: rotación por isla/franquicia sin datos unificados. Este sí está activo.
3. **Drive desactualizado** — el `CLAUDE TRASPASO` describe OpenClaw, que ya no usan (harness propio).
4. **Contradicción sin resolver** — whitepaper dice 6 clientes en producción; la rueda dice 12.
5. **Descubrimiento de su startup** — sin arrancar formalmente.

## Gente del ecosistema

Ver `relations.md`. Núcleo: Rodri Benzaquén (founder/CEO Boulder), Ariel Cohen (PM, mueve las reuniones), Pablo Hegoburu (CTO), Mia (dev de agentes), Emi (backend/servers), Sabri (gerenta comercial de ¡appa!, va a las llamadas), Andre y Tomi (traen clientes).
