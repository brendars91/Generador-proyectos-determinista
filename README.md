# Antigravity Core Copilot Engine (AGCCE)

> **Versión**: 1.1.0-OPTIMIZED  
> **Bundle ID**: BNDL-AGCCE-FINAL-2026

## 🎯 Descripción

AGCCE es un sistema de copiloto inteligente diseñado para asistir en el desarrollo de software con las siguientes características principales:

- **RAG Determinista**: El código local es la única fuente de verdad
- **Pre-Check Obligatorio**: Validación antes de proponer cambios
- **Plan JSON**: Emisión de planes estructurados antes de cualquier acción
- **HITL (Human-in-the-Loop)**: Aprobación humana requerida para operaciones de escritura
- **Evidencia Reproducible**: Logs, tests y rutas de archivos documentados

## 📁 Estructura del Proyecto

```
.
├── .agent/
│   ├── rules/
│   │   ├── snyk_rules.md          # Reglas de seguridad Snyk
│   │   └── agcce_directives.md    # Directivas v1.1.0
│   ├── workflows/
│   │   ├── docker-executor.md     # Alternativa a Docker MCP
│   │   ├── git-protocol.md        # Control de versiones local
│   │   └── pre-flight-check.md    # Verificaciones previas
│   └── skills/
│       ├── _core/                 # Skills fundamentales
│       └── automation/            # Skills de automatización (n8n)
├── schemas/
│   └── AGCCE_Plan_v1.schema.json  # Schema de validación de planes
├── scripts/
│   ├── validate_plan.py           # Validador de planes JSON
│   ├── lint_check.py              # Verificación de estilo
│   └── type_check.py              # Verificación de tipos
├── config/
│   └── bundle.json                # Configuración del bundle AGCCE
└── README.md
```

## 🔧 MCPs Activos

| MCP | Tools | Propósito |
|-----|-------|-----------|
| context7 | ~5 | Documentación de librerías |
| snyk | ~15 | Análisis de seguridad |
| sequential-thinking | ~3 | Razonamiento estructurado |
| smart-coding-mcp | ~6 | Búsqueda semántica de código |
| n8n-native | ~3 | Workflows de automatización |
| fetch | ~3 | HTTP requests |
| filesystem | ~5 | Acceso a archivos |

**Total**: ~40 tools (bajo el límite recomendado de 50)

## 📋 Directivas v1.1.0

### 1. Acoplamiento Docker-Plan
Antes de ejecutar scripts Docker, validar mapeo explícito en Plan JSON.

### 2. Restricción Snyk
Solo usar en fases: Pre-flight Check y Verification Report.

### 3. Protocolo Git Local
- Pre: `git status` antes de emitir plan
- Post: Commit con Conventional Commits

### 4. Validación Automática
`scripts/validate_plan.py` actúa como gate automático.

## 🚀 Uso

### Validar un Plan JSON
```bash
python scripts/validate_plan.py <plan.json>
```

### Ejecutar Lint Check
```bash
python scripts/lint_check.py <archivo_o_directorio>
```

### Ejecutar Type Check
```bash
python scripts/type_check.py <archivo_o_directorio>
```

### Workflows Disponibles
- `/docker-executor` - Comandos Docker sin MCP
- `/git-protocol` - Control de versiones Git
- `/pre-flight-check` - Verificaciones previas

## 📝 Licencia

Proyecto interno - Antigravity Platform
