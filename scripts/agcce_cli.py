#!/usr/bin/env python3
"""
AGCCE CLI Interactivo v1.0
Interfaz de línea de comandos tipo wizard para AGCCE.

Uso:
  python agcce_cli.py

Comandos:
  1. Indexar codebase
  2. Generar plan
  3. Ejecutar plan
  4. Ver métricas
  5. Configuración
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Importar utilidades
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info, make_header
except ImportError:
    class Colors:
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        RESET = '\033[0m'
        BOLD = '\033[1m'
    class Symbols:
        CHECK = '[OK]'
        CROSS = '[X]'
        WARN = '[!]'
        INFO = '[i]'
        ARROW = '->'
    def make_header(title, width=60):
        return f"\n{'='*width}\n  {title}\n{'='*width}\n"
    def log_pass(msg): print(f"{Colors.GREEN}[OK]{Colors.RESET} {msg}")
    def log_fail(msg): print(f"{Colors.RED}[X]{Colors.RESET} {msg}")
    def log_warn(msg): print(f"{Colors.YELLOW}[!]{Colors.RESET} {msg}")
    def log_info(msg): print(f"{Colors.BLUE}[i]{Colors.RESET} {msg}")


def clear_screen():
    """Limpia la pantalla."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Muestra banner de AGCCE."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
    _    ____  ____ ____ _____   _   _ _ _             
   / \\  / ___|/ ___/ ___| ____| | | | | | |_ _ __ __ _ 
  / _ \\| |  _| |  | |   |  _|   | | | | | __| '__/ _` |
 / ___ \\ |_| | |__| |___| |___  | |_| | | |_| | | (_| |
/_/   \\_\\____|\\____|\\____|_____|  \\___/|_|\\__|_|  \\__,_|
                                                        
{Colors.RESET}      v2.2 - ADAPTIVE INTELLIGENCE EXTRAORDINARY
    """
    print(banner)


def print_menu():
    """Muestra menú principal."""
    print(f"\n{Colors.BOLD}=== MENÚ PRINCIPAL ==={Colors.RESET}\n")
    options = [
        ("1", "Indexar Codebase", "Actualiza el índice RAG"),
        ("2", "Generar Plan", "Crea un plan de acción"),
        ("3", "Ejecutar Plan", "Ejecuta un plan existente"),
        ("4", "Ver Métricas", "Dashboard y estadísticas"),
        ("5", "Escanear Seguridad", "Detecta secretos y vulnerabilidades"),
        ("6", "Verificar Audit Trail", "Integridad del log de auditoría"),
        ("7", "Usar Template", "Crear plan desde template"),
        ("8", "Configuración", "Ver/editar config"),
        ("0", "Salir", "")
    ]
    
    for num, title, desc in options:
        if desc:
            print(f"  {Colors.CYAN}[{num}]{Colors.RESET} {title:<20} {Colors.BLUE}- {desc}{Colors.RESET}")
        else:
            print(f"  {Colors.CYAN}[{num}]{Colors.RESET} {title}")
    print()


def run_script(script_name: str, args: list = None) -> bool:
    """Ejecuta un script Python del proyecto."""
    script_path = f"scripts/{script_name}"
    if not os.path.exists(script_path):
        log_fail(f"Script no encontrado: {script_path}")
        return False
    
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        log_fail(f"Error ejecutando script: {e}")
        return False


def option_indexar():
    """Opción de indexar codebase."""
    print(make_header("INDEXAR CODEBASE"))
    print("Opciones:")
    print("  [1] Indexación completa")
    print("  [2] Indexación incremental (solo cambios)")
    print("  [0] Volver")
    
    choice = input("\nSelecciona opción: ").strip()
    
    if choice == "1":
        log_info("Iniciando indexación completa...")
        run_script("rag_indexer.py")
    elif choice == "2":
        log_info("Iniciando indexación incremental...")
        run_script("rag_indexer.py", ["--incremental"])


def option_generar_plan():
    """Opción de generar plan."""
    print(make_header("GENERAR PLAN"))
    
    objective = input("Describe el objetivo del plan:\n> ").strip()
    if not objective:
        log_warn("Objetivo vacío, cancelado")
        return
    
    files = input("Archivos objetivo (separados por coma, Enter para auto-detectar):\n> ").strip()
    
    args = ["--objective", objective]
    if files:
        args.extend(["--files", files])
    
    log_info("Generando plan...")
    run_script("plan_generator.py", args)


def option_ejecutar_plan():
    """Opción de ejecutar plan."""
    print(make_header("EJECUTAR PLAN"))
    
    plans_dir = "plans"
    if not os.path.exists(plans_dir):
        log_warn("No hay directorio de planes")
        return
    
    plans = [f for f in os.listdir(plans_dir) if f.endswith('.json')]
    if not plans:
        log_warn("No hay planes disponibles")
        return
    
    print("Planes disponibles:")
    for i, plan in enumerate(plans, 1):
        print(f"  [{i}] {plan}")
    
    choice = input("\nSelecciona plan (número): ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(plans):
            plan_path = os.path.join(plans_dir, plans[idx])
            log_info(f"Ejecutando: {plan_path}")
            run_script("orchestrator.py", [plan_path])
    except ValueError:
        log_warn("Selección inválida")


def option_metricas():
    """Opción de ver métricas."""
    print(make_header("MÉTRICAS"))
    print("Opciones:")
    print("  [1] Ver resumen (7 días)")
    print("  [2] Ver resumen (30 días)")
    print("  [3] Timeline de seguridad")
    print("  [4] Abrir dashboard web")
    print("  [0] Volver")
    
    choice = input("\nSelecciona opción: ").strip()
    
    if choice == "1":
        run_script("metrics_collector.py", ["summary", "7"])
    elif choice == "2":
        run_script("metrics_collector.py", ["summary", "30"])
    elif choice == "3":
        run_script("metrics_collector.py", ["timeline", "7"])
    elif choice == "4":
        log_info("Iniciando servidor dashboard...")
        run_script("dashboard_server.py", ["--port", "8888"])


def option_seguridad():
    """Opción de escanear seguridad."""
    print(make_header("ESCANEO DE SEGURIDAD"))
    print("Opciones:")
    print("  [1] Detectar secretos (todo el proyecto)")
    print("  [2] Detectar secretos (archivos staged)")
    print("  [3] Escaneo Snyk Code")
    print("  [0] Volver")
    
    choice = input("\nSelecciona opción: ").strip()
    
    if choice == "1":
        run_script("secrets_detector.py", ["."])
    elif choice == "2":
        run_script("secrets_detector.py", ["--scan-staged"])
    elif choice == "3":
        log_info("Ejecutando Snyk Code...")
        subprocess.run(["snyk", "code", "test"])


def option_audit():
    """Opción de verificar audit trail."""
    print(make_header("AUDIT TRAIL"))
    print("Opciones:")
    print("  [1] Verificar integridad")
    print("  [2] Ver últimos eventos")
    print("  [3] Exportar auditoría")
    print("  [0] Volver")
    
    choice = input("\nSelecciona opción: ").strip()
    
    if choice == "1":
        run_script("audit_trail.py", ["verify"])
    elif choice == "2":
        run_script("audit_trail.py", ["show", "7"])
    elif choice == "3":
        filepath = f"audit_export_{datetime.now().strftime('%Y%m%d')}.json"
        run_script("audit_trail.py", ["export", filepath])


def option_templates():
    """Opción de usar templates."""
    print(make_header("TEMPLATES DE PLANES"))
    
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        log_warn("No hay directorio de templates")
        return
    
    templates = [f for f in os.listdir(templates_dir) if f.endswith('.json')]
    if not templates:
        log_warn("No hay templates disponibles")
        return
    
    print("Templates disponibles:")
    for i, tpl in enumerate(templates, 1):
        try:
            with open(os.path.join(templates_dir, tpl), 'r') as f:
                data = json.load(f)
                name = data.get("name", tpl)
                desc = data.get("description", "")
                print(f"  [{i}] {name} - {desc}")
        except:
            print(f"  [{i}] {tpl}")
    
    print("\n(Templates se usan como base para generar planes)")
    input("\nPresiona Enter para volver...")


def option_config():
    """Opción de configuración."""
    print(make_header("CONFIGURACIÓN"))
    
    bundle_path = "config/bundle.json"
    if os.path.exists(bundle_path):
        with open(bundle_path, 'r') as f:
            bundle = json.load(f)
            print(f"Bundle ID: {bundle.get('bundle_id')}")
            print(f"Versión: {bundle.get('version')}")
            print(f"Governance: {json.dumps(bundle.get('governance', {}), indent=2)}")
    
    print("\nOtras opciones:")
    print("  [1] Configurar webhooks n8n")
    print("  [2] Verificar estado de webhooks")
    print("  [0] Volver")
    
    choice = input("\nSelecciona opción: ").strip()
    
    if choice == "1":
        run_script("event_dispatcher.py", ["configure"])
    elif choice == "2":
        run_script("event_dispatcher.py", ["status"])


def main():
    """Loop principal del CLI."""
    while True:
        clear_screen()
        print_banner()
        print_menu()
        
        choice = input("Selecciona una opción: ").strip()
        
        if choice == "0":
            print(f"\n{Colors.CYAN}¡Hasta luego!{Colors.RESET}\n")
            break
        elif choice == "1":
            option_indexar()
        elif choice == "2":
            option_generar_plan()
        elif choice == "3":
            option_ejecutar_plan()
        elif choice == "4":
            option_metricas()
        elif choice == "5":
            option_seguridad()
        elif choice == "6":
            option_audit()
        elif choice == "7":
            option_templates()
        elif choice == "8":
            option_config()
        else:
            log_warn("Opción no válida")
        
        input(f"\n{Colors.BLUE}Presiona Enter para continuar...{Colors.RESET}")


if __name__ == '__main__':
    main()
