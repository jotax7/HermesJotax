# El Recreo — ajustes a la propuesta (para iterar con el equipo)

**No son cambios de precio: son de arquitectura.** Los números quedan en tus manos.
Referencia: propuesta `Propuesta_Comercial_El_Recreo_BoulderTech.pdf` — Business, setup USD 15.000, fee USD 1.500/mes.

---

## 1. Consultoría de seguimiento: acotarla

**Como está:** "sesiones periódicas de seguimiento" sin tope. Es la línea más cara del documento.

**Propuesta de redacción:**
> Consultoría de seguimiento incluida: 8 horas mensuales de sesiones con el equipo de El Recreo para
> interpretar KPIs, priorizar casos de uso y preparar acciones. Las horas no utilizadas no se acumulan.
> Horas adicionales: [tarifa] por hora, con aprobación previa.

**Por qué:** el cliente lo valora más que el producto y a vos te cuesta horas de alguien senior. Acotado,
además, se vuelve un upsell natural.

## 2. Usuarios: definir asientos

**Como está:** el resumen habla de 3 usuarios iniciales, pero el plan habilita hasta 40. El día que
Gerencia, Operaciones y Finanzas entren, cobrás lo mismo.

**Propuesta de redacción:**
> Plan Business: 10 usuarios incluidos. Usuarios adicionales en tramos de 10: [precio] por tramo mensual.
> El resumen de piloto arranca con 3 usuarios del área de Relacionamiento; la ampliación a otras áreas
> se factura al activarse, no al firmarse.

**Por qué:** ahí está tu crecimiento. Sin tramos, el contrato no tiene dónde expandirse.

## 3. Las 2 fuentes extra: cotizarlas, no regalarlas

**Como está:** "como bonificación para este piloto, esas 2 integraciones quedan incluidas sin cargo".

**Propuesta de redacción:**
> El relevamiento de El Recreo identificó 10 fuentes de datos; el plan Business incluye 8.
> Las 2 restantes (____ y ____) se cotizan como add-on: [precio] por única vez + [precio] mensual por
> mantenimiento. Contratando las 10 en el mismo acuerdo, el add-on se bonifica en un [X]%.

**Por qué:** la bonificación destruye el precio de referencia de la próxima fuente que pidan. El descuento
por bundle te deja el ancla intacta y al cliente le sigue pareciendo una concesión.

## 4. Las tres cláusulas que faltan

**Plazo y salida**
> Plazo mínimo: 12 meses desde la puesta en producción. Renovación automática por períodos iguales salvo
> aviso de cualquiera de las partes con 60 días de anticipación.

**Forma de pago**
> Setup: 50% a la firma, 50% contra puesta en marcha. Fee mensual: adelantado, dentro de los primeros
> 10 días de cada mes.

**Validez**
> Esta propuesta tiene validez hasta el [fecha, 30 días]. Pasado ese plazo, los valores quedan sujetos a
> revisión.

**Qué rompe el fee fijo** (el párrafo que te salva el margen)
> El fee mensual cubre las fuentes y el alcance listados. Quedan fuera y se cotizan aparte: cambios o
> deprecaciones en las APIs de terceros (Qbiz, Urbapark, DataWiFi, Icomm, Social Scan), migraciones de
> sistemas del lado del cliente, nuevas fuentes de datos, nuevas áreas, y usuarios por encima del tramo
> contratado.

**Datos y salida**
> Las definiciones de negocio construidas durante el proyecto (qué es un cliente activo, cómo se cuenta
> una compra cruzada, criterios de segmentación) son propiedad de El Recreo y se entregan documentadas
> al finalizar la relación. Los accesos se revocan a los 30 días del cierre.

## 5. Lo que falta y no es precio

- **El caso IRSA con números** (15 shoppings, 23M+ transacciones, ~180 h/mes). Es la credibilidad más barata del documento y hoy no está.
- **Los 3 problemas de datos que ellos declararon**, tratados como módulos con nombre propio en vez de disueltos en el alcance:
  - mail con errores → normalización de identidad;
  - facturación que solo guarda el nombre del local → modelo de detalle de venta;
  - placa sin dueño → enriquecimiento con Recreo Lovers.
  Cada uno es una venta futura y, además, demuestra que leíste su cuestionario.
- **Criterio de éxito del piloto**: qué número tiene que moverse a los 90 días para que esto escale. Sin eso, la renovación se discute en el aire.

## 6. Preguntas abiertas que cambian el número (mandar antes de firmar)

1. ¿Cuántos usuarios van a consultar el agente en los primeros 6 meses?
2. ¿La facturación de Qbiz es base accesible por conexión o solo exportación? (cambia el esfuerzo)
3. ¿Quién es el referente técnico de Sistemas que habilita los accesos?
4. ¿Duración y fecha de inicio del piloto?
5. ¿Hay alguien del lado de ellos que pueda ser el champion interno del proyecto?
