Google Workspace conectado como jshaw@bouldertech.fi: proyecto GCP "hermes-wiggy" (audiencia Interna), cliente OAuth Desktop "Hermes Agent". Token en ~/.hermes/google_token.json (auto-refresh), client secret en ~/.hermes/google_client_secret.json. Scopes: Gmail read/send/modify, Calendar, Drive, Contacts readonly, Sheets, Docs.
§
Escritorio gráfico de esta máquina = sesión xrdp/xfce en DISPLAY=:10 con XAUTHORITY=~/.Xauthority (no hay DISPLAY en el entorno del gateway, así que computer_use falla por defecto). Chromium está en /usr/bin/chromium; no hay xdotool ni wmctrl.
§
Host: escritorio XFCE vía xrdp en DISPLAY=:10 (Chromium y Firefox instalados). Chrome 156 bloquea --remote-debugging-port sobre el perfil default, así que para automatizar el navegador logueado hay que copiar ~/.config/chromium a otro --user-data-dir.
§
Google Workspace ya autenticado (cuenta jshaw@bouldertech.fi, proyecto GCP hermes-wiggy, audiencia Interna): token ~/.hermes/google_token.json y client secret ~/.hermes/google_client_secret.json. El python de Hermes no tiene las libs de Google y setup.py falla con "Run this script in the Hermes environment": correr google_api.py con /home/bldt/.hermes/venvs/google/bin/python.
§
Escritorio: sesión RDP en DISPLAY=:10 (XFCE, usuario bldt, XAUTHORITY=~/.Xauthority) con Chromium logueado en Google. cua-driver/computer_use no hereda DISPLAY (devuelve "no DISPLAY is set") y le falta AT-SPI: para manejar el navegador logueado usar CDP con --remote-debugging-port; Chrome 156+ ignora el flag con el perfil default, hay que copiar ~/.config/chromium a un user-data-dir propio.
§
BoulderTech abandonó OpenClaw: ahora usan un harness propio de agentes. Los documentos viejos del Drive (p. ej. 'CLAUDE TRASPASO') siguen describiendo OpenClaw como stack central y están desactualizados.
§
Google conectado: ~/.hermes/google_token.json; usar /home/bldt/.hermes/venvs/google/bin/python para google_api.py (el python de Hermes no tiene libs). Chromium RDP :10 con --remote-debugging-port=9222 y helper cdp.py en ~/.hermes/cache/scratch; computer_use degradado sin AT-SPI.