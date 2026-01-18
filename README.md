# AGCCE Ultra v4.0 GUARDIAN MAS - Antigravity Core Copilot Engine

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Snyk](https://img.shields.io/badge/Security-Snyk-purple.svg)](https://snyk.io/)

> Motor de copiloto de IA determinístico con RAG semántico, auto-corrección, Progressive Disclosure y observabilidad completa.

---

## 🎯 ¿Qué es AGCCE Ultra?

AGCCE (Antigravity Core Copilot Engine) es un sistema de copiloto de desarrollo que:

- 🔍 **Busca inteligentemente** en tu código usando RAG semántico
- 🤖 **Planifica y ejecuta** tareas de forma determinística
- 🛡️ **Protege tu código** con escaneos de seguridad (Snyk)
- 📊 **Registra todo** para auditoría y observabilidad
- 🔔 **Notifica eventos** vía webhooks (n8n)

---

## 🚀 Instalación Rápida

### 1. Clonar el repositorio

```powershell
git clone https://github.com/TU_USUARIO/agcce-ultra.git
cd agcce-ultra
```

### 2. Ejecutar el instalador

```powershell
.\scripts\setup.ps1
```

### 3. Activar entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Iniciar el CLI

```powershell
python scripts\agcce_cli.py
```

---

## 📋 Requisitos

| Herramienta | Versión | Requerido |
|-------------|---------|-----------|
| Python | 3.10+ | ✅ |
| Git | 2.0+ | ✅ |
| Docker | 20.0+ | Opcional |
| Snyk CLI | Latest | Opcional |
| n8n | 1.0+ | Opcional |

### MCPs Recomendados (Antigravity)

- `smart-coding-mcp` - Búsqueda semántica
- `filesystem` - Operaciones de archivos
- `sequential-thinking` - Razonamiento estructurado
- `snyk` - Escaneos de seguridad

---

## 📂 Estructura del Proyecto

```
agcce-ultra/
├── scripts/           # Scripts Python del sistema
│   ├── agcce_cli.py   # CLI interactivo
│   ├── orchestrator.py
│   ├── plan_generator.py
│   └── ...
├── config/            # Configuración
│   ├── bundle.json    # Config principal
│   └── n8n_webhooks.json
├── dashboard/         # Dashboard web
├── templates/         # Templates de planes
├── schemas/           # Schemas JSON
├── documentacion/     # Documentación completa
├── n8n/               # Workflows de n8n
├── .agent/            # Reglas y workflows del agente
├── logs/              # Logs y telemetría
├── plans/             # Planes generados
└── evidence/          # Evidencia de ejecuciones
```

---

## 🖥️ Dashboard - Bitácora de Mis Proyectos

Inicia el servidor:

```powershell
python scripts\dashboard_server.py --port 8888
```

Abre en tu navegador:
```
http://localhost:8888/dashboard/index.html
```

**Funcionalidades:**
- 📊 Métricas en tiempo real
- 🌓 Modo oscuro/claro
- 📥 Export PDF/JSON
- 🔍 Filtro por proyecto

---

## 🔧 Comandos Principales

```powershell
# CLI Interactivo (recomendado)
python scripts\agcce_cli.py

# Indexar codebase
python scripts\rag_indexer.py

# Generar plan
python scripts\plan_generator.py --objective "Tu objetivo"

# Ejecutar plan
python scripts\orchestrator.py plans\tu_plan.json

# Ver métricas
python scripts\metrics_collector.py summary 7

# Detectar secretos
python scripts\secrets_detector.py .

# Generar changelog
python scripts\changelog_generator.py
```

---

## 🛡️ Seguridad

AGCCE Ultra implementa múltiples capas de seguridad:

1. **Gate Snyk**: Bloquea commits con vulnerabilidades
2. **Secrets Detector**: Detecta API keys antes de commit
3. **HITL**: Aprobación humana para operaciones de escritura
4. **Audit Trail**: Log inmutable de todas las acciones

---

## 📚 Documentación

La documentación completa está en `documentacion/`:

- [01. Visión General](documentacion/01_vision_general.md)
- [02. Guía de Instalación](documentacion/02_guia_instalacion.md)
- [03. Guía de Uso](documentacion/03_guia_uso.md)
- [04. Referencia de Scripts](documentacion/04_referencia_scripts.md)
- [05. Integración n8n](documentacion/05_integracion_n8n.md)
- [06. Observabilidad](documentacion/06_observabilidad.md)
- [07. Seguridad](documentacion/07_seguridad.md)
- [08. Historial de Desarrollo](documentacion/08_historial_desarrollo.md)
- [09. Troubleshooting](documentacion/09_troubleshooting.md)

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/mi-feature`
3. Haz tus cambios
4. Ejecuta el verificador: `python scripts\secrets_detector.py --scan-staged`
5. Commit: `git commit -m "feat: mi nueva feature"`
6. Push: `git push origin feature/mi-feature`
7. Abre un Pull Request

---

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

---

## 🙏 Créditos

Desarrollado con ❤️ usando:
- [Antigravity](https://github.com/anthropics/anthropic-cookbook) - Motor de agentes
- [Snyk](https://snyk.io/) - Seguridad de código
- [n8n](https://n8n.io/) - Automatización de workflows
- [Chart.js](https://www.chartjs.org/) - Visualizaciones

---

> **Estado: AGCCE v4.0-GUARDIAN-MAS ✅ - Security Red Team + Multi-Agent System**
