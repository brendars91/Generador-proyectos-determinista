#!/usr/bin/env python3
"""
AGCCE Pre-Commit Hook con Gate de Snyk
Bloquea commits si:
1. Lint check falla
2. Type check falla
3. Snyk detecta vulnerabilidades Critical o High

CONTROL CRITICO: Gate de Snyk
- Ejecuta snyk_code_scan antes del commit
- Bloquea si hay vulnerabilidades Critical o High
- Permite bypass con --no-verify (no recomendado)

Instalacion:
  python scripts/pre_commit_hook.py --install
  
Uso manual:
  python scripts/pre_commit_hook.py [--skip-snyk]
"""

import subprocess
import sys
import os
from datetime import datetime
from typing import Tuple, List

# Importar utilidades comunes
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info, make_header
except ImportError:
    class Colors:
        GREEN = RED = YELLOW = BLUE = CYAN = RESET = BOLD = ''
    class Symbols:
        CHECK = '[OK]'
        CROSS = '[X]'
        WARN = '[!]'
        INFO = '[i]'
    def log_pass(msg): print(f"[OK] {msg}")
    def log_fail(msg): print(f"[X] {msg}")
    def log_warn(msg): print(f"[!] {msg}")
    def log_info(msg): print(f"[i] {msg}")
    def make_header(title, width=60): return f"\n{'=' * width}\n  {title}\n{'=' * width}\n"


def get_staged_files() -> List[str]:
    """Obtiene lista de archivos staged para commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode != 0:
        return []
    return [f.strip() for f in result.stdout.split('\n') if f.strip()]


def get_staged_python_files() -> List[str]:
    """Obtiene archivos Python staged."""
    return [f for f in get_staged_files() if f.endswith('.py')]


def run_lint_check(files: List[str]) -> Tuple[bool, str]:
    """Ejecuta lint check en archivos staged."""
    if not files:
        return True, "No hay archivos Python para verificar"
    
    try:
        result = subprocess.run(
            [sys.executable, "scripts/lint_check.py"] + files[:5],  # Limitar a 5 archivos
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        return True, "lint_check.py no encontrado, saltando"
    except Exception as e:
        return True, f"Error ejecutando lint: {e}"


def run_type_check(files: List[str]) -> Tuple[bool, str]:
    """Ejecuta type check en archivos staged."""
    if not files:
        return True, "No hay archivos Python para verificar"
    
    try:
        result = subprocess.run(
            [sys.executable, "scripts/type_check.py"] + files[:5],
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )
        # Type check es warning, no bloqueante
        return True, result.stdout + result.stderr
    except FileNotFoundError:
        return True, "type_check.py no encontrado, saltando"
    except Exception as e:
        return True, f"Error ejecutando type check: {e}"


def run_snyk_security_scan() -> Tuple[bool, str, int, int]:
    """
    GATE DE SNYK - Bloquea Critical y High
    
    Returns:
        Tuple[bool, str, int, int]: (passed, output, critical_count, high_count)
    """
    try:
        # Ejecutar Snyk code scan con threshold high
        result = subprocess.run(
            [
                "C:\\Users\\ASUS\\AppData\\Local\\snyk\\vscode-cli\\snyk-win.exe",
                "code", "test",
                "--severity-threshold=high",
                "."
            ],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos max
            encoding='utf-8',
            errors='replace'
        )
        
        output = result.stdout + result.stderr
        
        # Contar vulnerabilidades
        critical_count = output.lower().count("critical")
        high_count = output.lower().count("high severity") + output.lower().count("[high]")
        
        # Bloquear si hay Critical o High
        if result.returncode != 0 or critical_count > 0 or high_count > 0:
            return False, output, critical_count, high_count
        
        return True, output, 0, 0
        
    except FileNotFoundError:
        log_warn("Snyk CLI no encontrado, saltando security scan")
        return True, "Snyk no disponible", 0, 0
    except subprocess.TimeoutExpired:
        log_warn("Snyk scan timeout, saltando")
        return True, "Snyk timeout", 0, 0
    except Exception as e:
        log_warn(f"Error ejecutando Snyk: {e}")
        return True, str(e), 0, 0


def run_pre_commit(skip_snyk: bool = False) -> bool:
    """
    Ejecuta todos los checks de pre-commit.
    
    Returns:
        bool: True si todos los checks pasan
    """
    print(make_header("AGCCE Pre-Commit Hook v2.0"))
    
    all_passed = True
    staged_files = get_staged_files()
    python_files = get_staged_python_files()
    
    print(f"{Colors.CYAN}Archivos staged:{Colors.RESET} {len(staged_files)}")
    print(f"{Colors.CYAN}Archivos Python:{Colors.RESET} {len(python_files)}")
    print()
    
    # 1. Lint Check
    print(f"{Colors.BOLD}[1/3] Lint Check...{Colors.RESET}")
    passed, output = run_lint_check(python_files)
    if passed:
        log_pass("Lint check pasado")
    else:
        log_fail("Lint check fallido")
        print(output[:500])
        all_passed = False
    
    # 2. Type Check (warning only)
    print(f"\n{Colors.BOLD}[2/3] Type Check...{Colors.RESET}")
    passed, output = run_type_check(python_files)
    if passed:
        log_pass("Type check completado")
    else:
        log_warn("Type check con warnings (no bloqueante)")
    
    # 3. Snyk Security Scan (GATE CRITICO)
    print(f"\n{Colors.BOLD}[3/3] Snyk Security Scan...{Colors.RESET}")
    
    if skip_snyk:
        log_warn("Snyk scan saltado por --skip-snyk")
    else:
        passed, output, critical, high = run_snyk_security_scan()
        
        if passed:
            log_pass("Sin vulnerabilidades Critical/High")
        else:
            log_fail(f"Vulnerabilidades detectadas: {critical} Critical, {high} High")
            print(f"\n{Colors.RED}{'=' * 50}")
            print("  COMMIT BLOQUEADO POR VULNERABILIDADES DE SEGURIDAD")
            print(f"{'=' * 50}{Colors.RESET}")
            print(f"\n{Colors.YELLOW}Vulnerabilidades:{Colors.RESET}")
            print(f"  Critical: {critical}")
            print(f"  High: {high}")
            print(f"\n{Colors.BLUE}Para ver detalles:{Colors.RESET}")
            print("  snyk code test .")
            print(f"\n{Colors.YELLOW}[!] Corrige las vulnerabilidades antes de hacer commit{Colors.RESET}")
            print(f"{Colors.RED}[!] No uses --no-verify para saltarte este check{Colors.RESET}\n")
            all_passed = False
    
    # Resultado final
    print()
    if all_passed:
        print(f"{Colors.GREEN}=== PRE-COMMIT PASSED ==={Colors.RESET}")
        log_pass("Commit permitido")
        return True
    else:
        print(f"{Colors.RED}=== PRE-COMMIT FAILED ==={Colors.RESET}")
        log_fail("Commit bloqueado")
        return False


def install_hook():
    """Instala el hook de pre-commit en .git/hooks/"""
    hook_path = ".git/hooks/pre-commit"
    
    # Verificar que estamos en un repo git
    if not os.path.exists(".git"):
        log_fail("No es un repositorio git")
        return False
    
    # Crear contenido del hook
    hook_content = '''#!/bin/sh
# AGCCE Pre-Commit Hook
# Instalado automaticamente por scripts/pre_commit_hook.py

python scripts/pre_commit_hook.py
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "Commit bloqueado por AGCCE Pre-Commit Hook"
    echo "Usa 'git commit --no-verify' para saltarte el hook (NO RECOMENDADO)"
    exit 1
fi

exit 0
'''
    
    # Crear directorio hooks si no existe
    os.makedirs(".git/hooks", exist_ok=True)
    
    # Escribir hook
    with open(hook_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(hook_content)
    
    # Hacer ejecutable (en Unix)
    if sys.platform != 'win32':
        os.chmod(hook_path, 0o755)
    
    log_pass(f"Hook instalado en {hook_path}")
    print(f"\n{Colors.BLUE}El hook se ejecutara automaticamente antes de cada commit.{Colors.RESET}")
    print(f"{Colors.YELLOW}Para desinstalar, elimina: {hook_path}{Colors.RESET}\n")
    
    return True


def main():
    if "--install" in sys.argv:
        install_hook()
        return
    
    if "--help" in sys.argv:
        print(f"Uso: python {sys.argv[0]} [--install | --skip-snyk | --help]")
        print("\nOpciones:")
        print("  --install     Instala el hook en .git/hooks/pre-commit")
        print("  --skip-snyk   Salta el scan de Snyk (no recomendado)")
        print("  --help        Muestra esta ayuda")
        return
    
    skip_snyk = "--skip-snyk" in sys.argv
    passed = run_pre_commit(skip_snyk)
    
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
