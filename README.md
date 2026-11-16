# HermesJotax — el sistema operativo de Joaco

Repo de trabajo de Hermes para Joaco (BoulderTech + proyectos personales).

Repo que versiona todo lo que Hermes sabe y produce para Joaco. La idea: si mañana cambia de máquina,
o el agente se rompe, o quiere que otra persona lo entienda, **todo está acá y se puede releer**.

## Estructura

```
work-os/
├── README.md            ← este archivo
├── memory/              ← qué sabe Hermes de Joaco (copia de memoria + perfil)
├── skills/              ← recetas que el agente fue aprendiendo (procedimientos)
├── bouldertech/         ← material de trabajo: estado, roadmap, investigación de mercado
├── ideas/               ← descubrimiento de la próxima startup (tesis, criterios de muerte)
├── experimentos/        ← cosas en pausa y con reglas escritas (FOMO, etc.)
└── logs/                ← qué se hizo y cuándo (diario de trabajo)
```

## Regla de uso

1. Joaco dice "commiteá" o "actualizá".
2. Hermes copia el estado nuevo (memoria, skills, notas, docs) a la carpeta que corresponda.
3. Hace commit con mensaje en castellano y **siempre lo confirma antes de pushear**.
4. Si el repo tiene remoto, hace push; si no, queda local con el commit.

## Qué NO va acá

- Contraseñas, tokens, claves, tarjetas. Nunca.
- Credenciales de OAuth (viven en `~/.hermes/`).
- Datos de clientes que no estén ya en el Drive compartido.

## Remoto

- [ ] Crear repo privado `work-os` en GitHub y agregarlo como `origin`.

## Convención de commits

`área: qué cambió` — por ejemplo:
- `memory: agrego preferencias de trabajo`
- `bouldertech: estado de noviembre con pricing`
- `skills: nueva receta de transcripción`
- `ideas: tres tesis de startup con criterio de muerte`
