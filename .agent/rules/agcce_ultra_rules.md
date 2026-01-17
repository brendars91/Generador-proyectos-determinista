# AGCCE Ultra v2.0 - Reglas Insuperables

> **Version**: BNDL-AGCCE-ULTRA-V2-P1  
> **Estado**: Activo

## Directivas Adicionales v2.1

### 1. RAG Management
```
REGLA: Priorizar smart-coding-mcp para busqueda semantica antes de emitir asunciones.
```
- Siempre consultar indice RAG antes de referenciar archivos
- Usar `rag_indexer.py --status` para verificar estado del indice
- Ejecutar `--incremental` despues de cambios significativos

### 2. Self-Correction con Semantic Verification
```
REGLA: Si validate_plan.py falla, usar Traceback como input para correccion.
REGLA: Verificar existencia semantica de paths (anti-alucinacion).
```
- Maximo 3 reintentos automaticos
- Validar estructura JSON + existencia de paths
- Si path no existe en filesystem/indice = ALUCINACION = reintento

### 3. Security Enforcement
```
REGLA: Bypass de Snyk en pre-commit esta PROHIBIDO.
```
- Gate Snyk bloquea Critical/High en codigo
- Snyk-Diff Policy bloquea vulnerabilidades en dependencias
- No usar `git commit --no-verify`

---

## Verificador Integrado

```json
{
  "verifier": {
    "checks": [
      "schema",          
      "grounding",       
      "security",        
      "semantic_existence" 
    ]
  }
}
```

| Check | Script | Descripcion |
|-------|--------|-------------|
| schema | `validate_plan.py` | Estructura JSON valida |
| grounding | `rag_indexer.py` | Indice RAG actualizado |
| security | `pre_commit_hook.py` | Snyk + Snyk-Diff |
| semantic_existence | `plan_generator.py` | Anti-alucinacion |

---

## Flujo de Verificacion

```
1. Pre-Plan: rag_indexer.py --status
2. Generate: plan_generator.py --objective "..."
   └─ Self-Correction Loop (3x max)
   └─ Semantic Verification (paths existen?)
3. Validate: validate_plan.py <plan.json>
4. Pre-Commit: pre_commit_hook.py
   └─ Lint Check
   └─ Snyk Code Scan
   └─ Snyk-Diff Policy (dependencias)
5. Commit: Solo si todo pasa
```

---

## Prohibiciones Absolutas

1. **NO** referenciar paths sin verificar existencia
2. **NO** saltear Snyk scan con --skip-snyk
3. **NO** usar git commit --no-verify
4. **NO** ignorar vulnerabilidades Critical/High
5. **NO** generar planes sin validacion semantica

---

## Metricas de Observabilidad (Seccion 13)

Para gobernar, debemos medir:

| Metrica | Fuente | Proposito |
|---------|--------|-----------|
| Plan Success Rate | plan_generator.py | Tasa de exito en generacion |
| RAG Latency | rag_indexer.py | Tiempo de indexacion |
| Security Blocks | pre_commit_hook.py | Commits bloqueados por Snyk |
| Hallucinations Detected | Semantic Verification | Alucinaciones evitadas |

> **Nota**: Estas metricas se implementaran en Fase 2 (Dashboard).
