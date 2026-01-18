# AGCCE Ultra v4.0 APEX - Antigravity Core Copilot Engine

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Non--Commercial-orange.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Snyk%20Protected-purple.svg)](https://snyk.io/)
[![Version](https://img.shields.io/badge/Version-4.0.0--APEX-green.svg)](https://github.com/brendars91/Generador-proyectos-determinista)

> **Motor de IA Determinístico con Arquitectura Multi-Agente, Security Guardian y Observabilidad Completa**

---

## 🏗️ Arquitectura Multi-Agente (MAS)

AGCCE v4.0 implementa un sistema jerárquico de agentes especializados:

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGCCE ULTRA v4.0 APEX                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                                              │
│   │ ORCHESTRATOR │ ◄── Coordina, no ejecuta                    │
│   └──────┬───────┘                                              │
│          │                                                      │
│   ┌──────▼───────────────────────────────────────────────┐     │
│   │              MULTI-AGENT SYSTEM (MAS)                │     │
│   │                                                       │     │
│   │  ┌──────────┐  ┌───────────┐  ┌─────────┐            │     │
│   │  │Researcher│─→│ Architect │─→│Constructor│           │     │
│   │  └──────────┘  └───────────┘  └────┬────┘            │     │
│   │                                     │                 │     │
│   │                    ┌────────────────▼────────┐       │     │
│   │                    │        Auditor          │       │     │
│   │                    │   (Security Guardian)   │       │     │
│   │                    └────────────┬────────────┘       │     │
│   │                                 │                    │     │
│   │                    ┌────────────▼────────┐           │     │
│   │                    │       Tester        │           │     │
│   │                    └─────────────────────┘           │     │
│   └───────────────────────────────────────────────────────┘     │
│                                                                 │
│   ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│   │ Blackboard │  │ Graceful   │  │ Telemetry  │               │
│   │  (Estado)  │  │ Recovery   │  │ Dashboard  │               │
│   └────────────┘  └────────────┘  └────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

### Roles de Agentes

| Agente | Rol | MCPs Permitidos |
|--------|-----|-----------------|
| **Researcher** | Busca contexto en codebase y docs | smart-coding-mcp, context7, fetch |
| **Architect** | Diseña solución, crea Plan JSON | sequential-thinking, filesystem |
| **Constructor** | Escribe código según el plan | filesystem, smart-coding-mcp |
| **Auditor** | Revisa seguridad (Red Team) | snyk, filesystem |
| **Tester** | Verifica calidad y tests | filesystem |

---

## 🚀 Instalación Rápida

### 1. Clonar Repositorio

```powershell
git clone https://github.com/brendars91/Generador-proyectos-determinista.git agcce-ultra
cd agcce-ultra
```

### 2. Ejecutar Instalador

```powershell
.\scripts\setup.ps1
```

### 3. Activar Entorno

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Verificar Instalación

```powershell
python scripts/agcce_cli.py
```

---

## 📋 Requisitos

| Componente | Versión | Requerido |
|------------|---------|-----------|
| Python | 3.10+ | ✅ |
| Git | 2.0+ | ✅ |
| Snyk CLI | Latest | ✅ Seguridad |
| pytest | Latest | Tests |
| Docker | 20.0+ | Opcional |

### MCPs Recomendados

- `smart-coding-mcp` - Búsqueda semántica RAG
- `filesystem` - Operaciones de archivos
- `snyk` - Escaneos de seguridad
- `sequential-thinking` - Razonamiento estructurado

---

## 🎯 Uso Principal

### CLI Interactivo (Recomendado)

```powershell
python scripts/agcce_cli.py
```

### Comandos Directos

```powershell
# Orquestador - Ejecutar un plan
python scripts/orchestrator.py plans/mi_plan.json

# Security Guardian - Analizar código
python scripts/security_guardian.py analyze scripts/

# Ver flujo de agentes
python scripts/agent_switcher.py workflow

# Estado del Blackboard
python scripts/blackboard.py status

# Ejecutar tests
pytest tests/ -v
```

---

## 🛡️ Security Guardian (Red Team)

El sistema detecta vulnerabilidades lógicas que Snyk no puede ver:

| Tipo | Descripción |
|------|-------------|
| **IDOR** | Acceso no autorizado cambiando IDs |
| **Race Condition** | Condiciones de carrera |
| **Auth Bypass** | Bypass de autenticación |
| **Logic Flaw** | Errores de lógica de negocio |
| **Data Exposure** | Filtración de datos sensibles |
| **SSRF** | Server-Side Request Forgery |

### Protocolo Red-to-Green

1. **Hipótesis de Ataque**: "¿Cómo explotaría esto un atacante?"
2. **PoC Test**: Escribir test que demuestre el fallo
3. **Fix**: Implementar corrección
4. **Verify**: Ejecutar test para confirmar

---

## 🆘 Primeros Auxilios

### Si el Orquestrador Falla

```powershell
# 1. Ver estado actual
python scripts/blackboard.py status

# 2. Ver último error
python scripts/blackboard.py get errors

# 3. Limpiar estado y reintentar
python scripts/blackboard.py clear
python scripts/orchestrator.py plans/mi_plan.json
```

### Si un Agente No Responde

```powershell
# Ver estadísticas de recuperación
python scripts/graceful_recovery.py stats

# El sistema reintenta automáticamente 3 veces
# Si persiste, revisa logs/recovery_events.jsonl
```

### Si Snyk Bloquea el Commit

```powershell
# Ver vulnerabilidades
python scripts/security_guardian.py analyze .

# Opciones:
# 1. Corregir vulnerabilidades
# 2. Si es falso positivo, documentar en .snyk
```

### Si los Tests Fallan

```powershell
# Ejecutar test específico con debug
pytest tests/test_skill_loader.py -v --tb=long

# Ver cobertura
pytest tests/ --cov=scripts --cov-report=html
```

---

## 📂 Estructura del Proyecto

```
agcce-ultra/
├── .agent/                    # Configuración del agente
│   ├── rules/                 # Reglas de comportamiento
│   ├── workflows/             # Workflows automatizados
│   └── skills/                # Skills especializados
│       └── security-red-team/ # Skill de seguridad
├── config/                    # Configuración
│   ├── bundle.json            # Config principal
│   ├── skill_manifest.json    # Mapa de MCPs por fase
│   └── agent_profiles/        # Perfiles de agentes MAS
├── scripts/                   # Scripts Python
│   ├── orchestrator.py        # Orquestador principal
│   ├── security_guardian.py   # Red Team automatizado
│   ├── agent_switcher.py      # Cambio de contexto MAS
│   ├── blackboard.py          # Estado compartido
│   ├── graceful_recovery.py   # Manejo de errores
│   └── agcce_cli.py           # CLI interactivo
├── tests/                     # Tests automatizados
├── schemas/                   # JSON schemas
├── templates/                 # Plantillas de planes
├── dashboard/                 # Dashboard web
├── documentacion/             # Documentación completa
├── logs/                      # Telemetría y logs
├── plans/                     # Planes y cola de tareas
├── evidence/                  # Evidencia de ejecuciones
├── LICENSE                    # Licencia (no comercial)
└── README.md                  # Este archivo
```

---

## 📊 Observabilidad

### Dashboard

```powershell
python scripts/dashboard_server.py --port 8888
# Abrir: http://localhost:8888/dashboard/index.html
```

### Telemetría

Todas las métricas van a `logs/telemetry.jsonl`:
- Incluye `project_id` y `agent_id`
- Formato JSONL append-only
- Retención: 30 días

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [01. Visión General](documentacion/01_vision_general.md) | Arquitectura |
| [02. Instalación](documentacion/02_guia_instalacion.md) | Setup |
| [03. Uso](documentacion/03_guia_uso.md) | Guía de uso |
| [04. Scripts](documentacion/04_referencia_scripts.md) | Referencia |
| [05. n8n](documentacion/05_integracion_n8n.md) | Webhooks |
| [06. Observabilidad](documentacion/06_observabilidad.md) | Métricas |
| [07. Seguridad](documentacion/07_seguridad.md) | HITL, Snyk |
| [08. Historial](documentacion/08_historial_desarrollo.md) | Changelog |
| [09. Troubleshooting](documentacion/09_troubleshooting.md) | Problemas |
| [10. v4.0 MAS](documentacion/10_v4_guardian_mas.md) | Multi-Agent |

---

## 📜 Licencia

**Uso Personal y No Comercial Únicamente**

- ✅ Usar, copiar, modificar para uso personal
- ❌ Vender, sublicenciar, uso comercial sin permiso
- ✅ Redistribuir si mantiene esta licencia

Ver [LICENSE](LICENSE) para detalles completos.

---

## 🙏 Créditos

Desarrollado con:
- [Antigravity](https://github.com/google/generative-ai-python) - Motor de agentes
- [Snyk](https://snyk.io/) - Seguridad
- [n8n](https://n8n.io/) - Automatización
- [Chart.js](https://www.chartjs.org/) - Visualizaciones

---

> **AGCCE v4.0-APEX MISSION READY 🚀**
