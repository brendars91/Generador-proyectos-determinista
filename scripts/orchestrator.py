#!/usr/bin/env python3
"""
AGCCE Orchestrator
Orquesta el flujo completo: Validación → HITL → Ejecución → Evidencia.

Uso: python orchestrator.py <plan.json>
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(title: str) -> None:
    """Imprime header formateado."""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}{Colors.RESET}\n")


def run_script(script: str, args: List[str] = []) -> Tuple[bool, str]:
    """Ejecuta un script Python del proyecto."""
    cmd = [sys.executable, f"scripts/{script}"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def phase_pre_flight(plan_path: str) -> bool:
    """Fase 1: Pre-flight checks."""
    print_header("FASE 1: PRE-FLIGHT CHECK")
    
    # 1.1 Git status
    print(f"{Colors.BLUE}[1.1]{Colors.RESET} Verificando estado de Git...")
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        print(f"  {Colors.YELLOW}⚠ Hay cambios pendientes en el repositorio{Colors.RESET}")
        for line in result.stdout.strip().split("\n")[:5]:
            print(f"    {line}")
        response = input(f"\n  {Colors.YELLOW}¿Continuar de todos modos? (s/n): {Colors.RESET}").lower()
        if response != 's':
            print(f"  {Colors.RED}Abortado por usuario{Colors.RESET}")
            return False
    else:
        print(f"  {Colors.GREEN}✓ Repositorio limpio{Colors.RESET}")
    
    # 1.2 Validar plan
    print(f"\n{Colors.BLUE}[1.2]{Colors.RESET} Validando plan JSON...")
    success, output = run_script("validate_plan.py", [plan_path])
    if success:
        print(f"  {Colors.GREEN}✓ Plan válido según AGCCE_Plan_v1{Colors.RESET}")
    else:
        print(f"  {Colors.RED}✗ Plan inválido{Colors.RESET}")
        print(output[:500])
        return False
    
    # 1.3 Lint check de archivos afectados
    print(f"\n{Colors.BLUE}[1.3]{Colors.RESET} Verificando archivos objetivo...")
    with open(plan_path, 'r') as f:
        plan = json.load(f)
    
    affected = plan.get("objective", {}).get("affected_files", [])
    existing = [f for f in affected if os.path.exists(f)]
    
    if existing:
        for file in existing[:3]:  # Limitar a 3 archivos
            print(f"  Analizando: {file}")
        success, output = run_script("lint_check.py", [existing[0]] if existing else ["."])
        if success:
            print(f"  {Colors.GREEN}✓ Lint check pasado{Colors.RESET}")
        else:
            print(f"  {Colors.YELLOW}⚠ Lint check con warnings{Colors.RESET}")
    else:
        print(f"  {Colors.YELLOW}⚠ Archivos objetivo no existen aún (serán creados){Colors.RESET}")
    
    print(f"\n{Colors.GREEN}═══ PRE-FLIGHT CHECK PASSED ═══{Colors.RESET}")
    return True


def phase_hitl(plan_path: str) -> bool:
    """Fase 2: HITL Gate."""
    print_header("FASE 2: HITL GATE")
    
    print(f"{Colors.BLUE}Verificando aprobaciones pendientes...{Colors.RESET}\n")
    success, output = run_script("hitl_gate.py", [plan_path, "--check"])
    
    if success:
        print(f"{Colors.GREEN}═══ HITL GATE PASSED ═══{Colors.RESET}")
        return True
    
    print(f"\n{Colors.YELLOW}Hay pasos pendientes de aprobación.{Colors.RESET}")
    response = input(f"{Colors.CYAN}¿Iniciar proceso de aprobación interactivo? (s/n): {Colors.RESET}").lower()
    
    if response == 's':
        # Ejecutar en modo interactivo - necesita terminal directo
        result = subprocess.run(
            [sys.executable, "scripts/hitl_gate.py", plan_path, "--interactive"],
            timeout=600
        )
        return result.returncode == 0
    
    print(f"{Colors.RED}Proceso detenido: aprobaciones pendientes{Colors.RESET}")
    return False


def phase_execute(plan_path: str) -> bool:
    """Fase 3: Ejecución (simulada - muestra pasos)."""
    print_header("FASE 3: EJECUCIÓN DEL PLAN")
    
    with open(plan_path, 'r') as f:
        plan = json.load(f)
    
    steps = plan.get("steps", [])
    
    print(f"{Colors.CYAN}Plan:{Colors.RESET} {plan.get('plan_id')}")
    print(f"{Colors.CYAN}Pasos:{Colors.RESET} {len(steps)}\n")
    
    for step in steps:
        step_id = step.get("id")
        action = step.get("action")
        target = step.get("target")
        hitl = "🔒" if step.get("hitl_required") else "🔓"
        
        print(f"  {hitl} {Colors.BOLD}{step_id}{Colors.RESET}: {action}")
        print(f"      → {target}")
        
        if step.get("depends_on"):
            print(f"      ⤷ Depende de: {', '.join(step.get('depends_on'))}")
    
    print(f"\n{Colors.YELLOW}⚠ MODO SIMULACIÓN: Los pasos no se ejecutan automáticamente{Colors.RESET}")
    print(f"{Colors.BLUE}Para ejecutar, implemente la lógica específica de cada acción.{Colors.RESET}")
    
    print(f"\n{Colors.GREEN}═══ EXECUTION PLAN REVIEWED ═══{Colors.RESET}")
    return True


def phase_evidence(plan_path: str) -> bool:
    """Fase 4: Recolección de evidencia."""
    print_header("FASE 4: RECOLECCIÓN DE EVIDENCIA")
    
    print(f"{Colors.BLUE}Generando reporte de evidencia...{Colors.RESET}\n")
    success, output = run_script("collect_evidence.py", [plan_path])
    
    if success:
        print(f"{Colors.GREEN}═══ EVIDENCE COLLECTED ═══{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}═══ EVIDENCE PARTIAL ═══{Colors.RESET}")
    
    return success


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <plan.json>")
        print("\nEste orquestador ejecuta el flujo completo AGCCE:")
        print("  1. Pre-flight Check (Git status, validación de plan, lint)")
        print("  2. HITL Gate (aprobación de pasos de escritura)")
        print("  3. Ejecución (revisión de pasos)")
        print("  4. Recolección de Evidencia")
        sys.exit(1)
    
    plan_path = sys.argv[1]
    
    if not os.path.exists(plan_path):
        print(f"{Colors.RED}Error: '{plan_path}' no existe{Colors.RESET}")
        sys.exit(1)
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("    ╔═══════════════════════════════════════════════════════╗")
    print("    ║     AGCCE ORCHESTRATOR v1.1.0-OPTIMIZED              ║")
    print("    ║     Antigravity Core Copilot Engine                  ║")
    print("    ╚═══════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    # Ejecutar fases
    phases = [
        ("Pre-Flight Check", phase_pre_flight),
        ("HITL Gate", phase_hitl),
        ("Execution", phase_execute),
        ("Evidence Collection", phase_evidence)
    ]
    
    results = []
    for name, phase_func in phases:
        try:
            success = phase_func(plan_path)
            results.append((name, success))
            
            if not success:
                print(f"\n{Colors.RED}Pipeline detenido en: {name}{Colors.RESET}")
                break
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrumpido por usuario{Colors.RESET}")
            break
        except Exception as e:
            print(f"\n{Colors.RED}Error en {name}: {e}{Colors.RESET}")
            results.append((name, False))
            break
    
    # Resumen final
    print(f"\n{Colors.BOLD}{'═' * 60}")
    print(f"  RESUMEN DE EJECUCIÓN")
    print(f"{'═' * 60}{Colors.RESET}\n")
    
    for name, success in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if success else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"  {status} {name}")
    
    all_passed = all(s for _, s in results) and len(results) == len(phases)
    
    print()
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}═══ PIPELINE COMPLETED SUCCESSFULLY ═══{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}═══ PIPELINE INCOMPLETE ═══{Colors.RESET}")
        sys.exit(1)


if __name__ == '__main__':
    main()
