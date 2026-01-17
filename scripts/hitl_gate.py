#!/usr/bin/env python3
"""
AGCCE HITL Gate
Human-in-the-Loop gate para operaciones de escritura.
Verifica que las acciones de escritura tengan aprobación explícita.

Uso: python hitl_gate.py <plan.json> [--check-step S01]
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


# Archivo de tokens de aprobación
APPROVAL_FILE = ".hitl_approvals.json"


def load_plan(path: str) -> Dict[str, Any]:
    """Carga el plan JSON desde archivo."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_approvals() -> Dict[str, Any]:
    """Carga aprobaciones existentes."""
    if os.path.exists(APPROVAL_FILE):
        with open(APPROVAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"approvals": {}}


def save_approvals(approvals: Dict[str, Any]) -> None:
    """Guarda aprobaciones."""
    with open(APPROVAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(approvals, f, indent=2)


def get_write_steps(plan: Dict) -> List[Dict]:
    """Obtiene pasos que requieren HITL."""
    write_actions = ['write_file', 'delete_file', 'git_commit']
    steps = []
    
    for step in plan.get('steps', []):
        if step.get('hitl_required', False) or step.get('action') in write_actions:
            steps.append(step)
    
    return steps


def check_step_approval(plan_id: str, step_id: str, approvals: Dict) -> bool:
    """Verifica si un paso tiene aprobación válida."""
    plan_approvals = approvals.get("approvals", {}).get(plan_id, {})
    step_approval = plan_approvals.get(step_id)
    
    if not step_approval:
        return False
    
    # Verificar que no haya expirado (24h)
    approved_at = datetime.fromisoformat(step_approval.get("approved_at", ""))
    if (datetime.now() - approved_at).total_seconds() > 86400:
        return False
    
    return step_approval.get("approved", False)


def request_approval(plan: Dict, step: Dict) -> bool:
    """Solicita aprobación interactiva para un paso."""
    print(f"\n{Colors.BOLD}{'═' * 60}")
    print(f"  HITL GATE - Aprobación Requerida")
    print(f"{'═' * 60}{Colors.RESET}\n")
    
    print(f"{Colors.CYAN}Plan:{Colors.RESET} {plan.get('plan_id')}")
    print(f"{Colors.CYAN}Objetivo:{Colors.RESET} {plan.get('objective', {}).get('description', 'N/A')}")
    print()
    
    print(f"{Colors.YELLOW}⚠ Paso que requiere aprobación:{Colors.RESET}")
    print(f"  {Colors.BOLD}ID:{Colors.RESET} {step.get('id')}")
    print(f"  {Colors.BOLD}Acción:{Colors.RESET} {step.get('action')}")
    print(f"  {Colors.BOLD}Target:{Colors.RESET} {step.get('target')}")
    print(f"  {Colors.BOLD}Resultado esperado:{Colors.RESET} {step.get('expected_outcome', 'N/A')}")
    
    if step.get('rollback'):
        print(f"  {Colors.BOLD}Rollback:{Colors.RESET} {step.get('rollback')}")
    
    print()
    
    while True:
        response = input(f"{Colors.GREEN}¿Aprobar esta acción? (s/n/ver): {Colors.RESET}").lower().strip()
        
        if response in ['s', 'si', 'yes', 'y']:
            return True
        elif response in ['n', 'no']:
            return False
        elif response in ['ver', 'v', 'view']:
            print(f"\n{Colors.BLUE}Detalle completo del paso:{Colors.RESET}")
            print(json.dumps(step, indent=2, ensure_ascii=False))
            print()
        else:
            print(f"{Colors.YELLOW}Respuesta no válida. Usa 's' para aprobar, 'n' para rechazar, 'ver' para más detalles.{Colors.RESET}")


def approve_step(plan_id: str, step_id: str, user: str = "human") -> None:
    """Registra aprobación de un paso."""
    approvals = load_approvals()
    
    if plan_id not in approvals["approvals"]:
        approvals["approvals"][plan_id] = {}
    
    approvals["approvals"][plan_id][step_id] = {
        "approved": True,
        "approved_at": datetime.now().isoformat(),
        "approved_by": user
    }
    
    save_approvals(approvals)
    print(f"{Colors.GREEN}✓ Paso {step_id} aprobado y registrado{Colors.RESET}")


def reject_step(plan_id: str, step_id: str, reason: str = "") -> None:
    """Registra rechazo de un paso."""
    approvals = load_approvals()
    
    if plan_id not in approvals["approvals"]:
        approvals["approvals"][plan_id] = {}
    
    approvals["approvals"][plan_id][step_id] = {
        "approved": False,
        "rejected_at": datetime.now().isoformat(),
        "reason": reason
    }
    
    save_approvals(approvals)
    print(f"{Colors.RED}✗ Paso {step_id} rechazado{Colors.RESET}")


def check_all_hitl(plan_path: str) -> bool:
    """Verifica todos los pasos HITL de un plan."""
    plan = load_plan(plan_path)
    approvals = load_approvals()
    plan_id = plan.get('plan_id')
    
    write_steps = get_write_steps(plan)
    
    if not write_steps:
        print(f"{Colors.GREEN}✓ No hay pasos que requieran aprobación HITL{Colors.RESET}")
        return True
    
    print(f"\n{Colors.BOLD}Verificando {len(write_steps)} pasos con HITL...{Colors.RESET}\n")
    
    all_approved = True
    pending = []
    
    for step in write_steps:
        step_id = step.get('id')
        is_approved = check_step_approval(plan_id, step_id, approvals)
        
        status = f"{Colors.GREEN}✓ Aprobado{Colors.RESET}" if is_approved else f"{Colors.YELLOW}○ Pendiente{Colors.RESET}"
        print(f"  {status} {step_id}: {step.get('action')} → {step.get('target')}")
        
        if not is_approved:
            all_approved = False
            pending.append(step)
    
    print()
    
    if all_approved:
        print(f"{Colors.GREEN}═══ HITL GATE PASSED ═══{Colors.RESET}")
        return True
    else:
        print(f"{Colors.YELLOW}═══ {len(pending)} PASOS PENDIENTES DE APROBACIÓN ═══{Colors.RESET}")
        return False


def interactive_approval(plan_path: str) -> bool:
    """Proceso interactivo de aprobación de pasos."""
    plan = load_plan(plan_path)
    plan_id = plan.get('plan_id')
    approvals = load_approvals()
    
    write_steps = get_write_steps(plan)
    
    for step in write_steps:
        step_id = step.get('id')
        
        if check_step_approval(plan_id, step_id, approvals):
            print(f"{Colors.GREEN}✓ {step_id} ya aprobado{Colors.RESET}")
            continue
        
        approved = request_approval(plan, step)
        
        if approved:
            approve_step(plan_id, step_id)
        else:
            reason = input(f"{Colors.YELLOW}Razón del rechazo (opcional): {Colors.RESET}").strip()
            reject_step(plan_id, step_id, reason)
            print(f"\n{Colors.RED}Proceso de aprobación detenido por rechazo.{Colors.RESET}")
            return False
    
    print(f"\n{Colors.GREEN}═══ TODOS LOS PASOS APROBADOS ═══{Colors.RESET}")
    return True


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <plan.json> [--interactive | --check]")
        print("  --interactive: Solicita aprobación interactiva")
        print("  --check: Solo verifica estado de aprobaciones")
        sys.exit(1)
    
    plan_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "--check"
    
    if not os.path.exists(plan_path):
        print(f"{Colors.RED}Error: '{plan_path}' no existe{Colors.RESET}")
        sys.exit(1)
    
    if mode == "--interactive":
        success = interactive_approval(plan_path)
    else:
        success = check_all_hitl(plan_path)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
