# Experimentos pendientes

## 1. FOMO + memecoins (parkeado el 14/11/2026, arranca cuando Joaco diga)

**Idea:** cuenta nueva con US$ 100, reglas claras, y Hermes opera o copilotea.
**Decisión tomada:** Joaco tipea él mismo la clave. Hermes no recibe contraseñas.

**Conexiones necesarias:**
- FOMO: versión web en el Chromium del RDP (:10, CDP en 9222). Login por email + código (Privy) → el código lo recibe Joaco. Si es mobile-only, no hay acceso.
- X/Twitter: skill `xurl` (CLI). Requiere instalar `xurl` y hacer el OAuth de su cuenta. Sirve para ver narrativa/momentum de memecoins.

**Reglas a escribir antes de poner un dólar:**
1. Presupuesto de riesgo: US$ 100 total. Si se va a cero, se termina el experimento.
2. Tamaño máximo por posición: por definir (arranque sugerido 10-15% = US$ 10-15).
3. Criterio de entrada explícito: liquidez mínima, edad del token, distribución de holders, mint authority revocada, volumen.
4. Stop de pérdida por posición y salida por tiempo.
5. Máximo de pérdida diaria → al alcanzarlo, kill switch y no se opera más ese día.
6. Log obligatorio de cada trade con motivo de entrada y salida.

**Fases:**
- Fase 0 — papel: 30-50 operaciones simuladas con precios reales (Jupiter). Medir win rate y expectativa.
- Fase 1 — real, tamaño mínimo, modo copiloto (Hermes propone, Joaco confirma).
- Fase 2 — solo si hay edge medido: ejecución por API con wallet dedicada.

**Riesgos conocidos (de la investigación del 14/11):**
- Fee 0,5% por lado → 1% de round trip antes de spread y slippage.
- FOMO avisa que no marca todos los contratos riesgosos y que un honeypot encierra los fondos sin reversa.
- Trading automatizado probablemente viola los términos del servicio → riesgo de cuenta congelada.
- Valor esperado negativo para la mayoría de los participantes.

## 2. (agregar próximos experimentos acá)
