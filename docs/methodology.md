# Metodología de trabajo

A partir de la Fase 6, cada bloque de trabajo se planifica y ejecuta en 3 etapas, y se documenta aquí mismo.

## Las 3 etapas
1. **Discussion (Discusión)** — Debatir la idea y las necesidades del negocio. Se hace con preguntas clave una por una, para "vaciar la mente" con calma. → `1-discussion.md`
2. **Research Plan (Investigación)** — Analizar lógica de UI experta, flujos de usuario y mejores prácticas (con fuentes) *antes* de escribir código. → `2-research-plan.md`
3. **Execute (Ejecución)** — Definir los pasos técnicos para programar y desplegar. → `3-execution.md`

## Organización
- **Phase (Fase):** un bloque grande de funcionalidad (ej: Pagos, Rediseño UX).
- **Wave (Ola):** un sprint corto dentro de una fase (un pedazo entregable).

## Convención de documentación
Cada fase vive en su carpeta `docs/phase-NN-nombre/` con los 3 archivos de las etapas. La documentación es un **entregable de primera clase**: debe permitir que alguien externo entienda *qué* se hizo y *por qué*, desde el brainstorm hasta el código.

```
docs/
├── 00-overview.md            ← visión, negocio, arquitectura
├── methodology.md            ← este archivo
├── history/
│   └── phases-0-5.md         ← backfill de lo ya construido
└── phase-06-payments/
    ├── 1-discussion.md
    ├── 2-research-plan.md
    └── 3-execution.md
```

## Idioma
Documentos en **español** (prosa para el equipo y revisores). Código e identificadores en **inglés**.
